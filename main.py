#!/usr/bin/env python3
"""
Twitch Song Recognition Bot

Captures audio from a Twitch stream and identifies the currently playing song.
"""

import argparse
import json
import sys
from pathlib import Path

from audio_capture import capture_audio, cleanup_audio, AudioCaptureError
from song_recognizer import recognize_song, SongRecognitionError


def load_config(config_path: str = "config.json") -> dict:
    """Load configuration from JSON file."""
    path = Path(config_path)
    if not path.exists():
        print(f"Error: Config file not found: {config_path}")
        print("Create a config.json with your stream URL:")
        print('  {"stream_url": "https://twitch.tv/username", "duration_seconds": 10}')
        sys.exit(1)

    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Identify songs playing on a Twitch stream"
    )
    parser.add_argument(
        "--url",
        help="Twitch stream URL (overrides config.json)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Duration in seconds to capture (default: 10)"
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to config file (default: config.json)"
    )
    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # Get settings (CLI args override config)
    stream_url = args.url or config.get("stream_url")
    duration = args.duration or config.get("duration_seconds", 10)
    cleanup = config.get("cleanup_audio", True)

    if not stream_url or stream_url == "https://twitch.tv/username":
        print("Error: Please set a valid stream URL in config.json or use --url")
        sys.exit(1)

    print(f"Listening to: {stream_url}")
    print(f"Capturing {duration} seconds of audio...")

    audio_path = None
    try:
        # Capture audio from stream
        audio_path = capture_audio(stream_url, duration)
        print(f"Audio captured: {audio_path}")
        print("Identifying song...")

        # Recognize the song
        result = recognize_song(audio_path)

        if result.found:
            print(f"\n>> Now playing: {result.title} by {result.artist}")
            if result.album:
                print(f"   Album: {result.album}")
        else:
            print("\n>> Could not identify the song (no music detected or too much noise)")

    except AudioCaptureError as e:
        print(f"\nError capturing audio: {e}")
        sys.exit(1)
    except SongRecognitionError as e:
        print(f"\nError recognizing song: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    finally:
        # Cleanup temp file
        if audio_path and cleanup:
            cleanup_audio(audio_path)
        elif audio_path:
            print(f"\nAudio saved: {audio_path}")


if __name__ == "__main__":
    main()
