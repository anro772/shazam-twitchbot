import subprocess
import tempfile
import os
from pathlib import Path
import streamlink


class AudioCaptureError(Exception):
    """Raised when audio capture fails."""
    pass


def get_stream_url(twitch_url: str) -> str:
    """Get the actual stream URL from a Twitch channel URL."""
    try:
        streams = streamlink.streams(twitch_url)
    except streamlink.NoPluginError:
        raise AudioCaptureError(f"Invalid URL format: {twitch_url}")
    except streamlink.PluginError as e:
        raise AudioCaptureError(f"Error accessing stream: {e}")

    if not streams:
        raise AudioCaptureError("Stream is offline or unavailable")

    # Prefer audio_only if available, otherwise use worst quality (less data to process)
    if "audio_only" in streams:
        return streams["audio_only"].url
    elif "worst" in streams:
        return streams["worst"].url
    elif "best" in streams:
        return streams["best"].url
    else:
        # Get any available stream
        return list(streams.values())[0].url


def capture_audio(twitch_url: str, duration_seconds: int = 10) -> str:
    """
    Capture audio from a Twitch stream.

    Returns the path to the temporary audio file.
    """
    # Get the actual stream URL
    stream_url = get_stream_url(twitch_url)

    # Save audio file in current directory for easy access
    audio_path = os.path.join(os.getcwd(), "captured_audio.mp3")

    # Use FFmpeg to capture audio from the stream
    # -live_start_index -3 starts from near the live edge (not beginning of stream)
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file
        "-live_start_index", "-3",  # Start from live edge
        "-i", stream_url,
        "-t", str(duration_seconds),
        "-vn",  # No video
        "-acodec", "libmp3lame",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "192k",
        audio_path
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=duration_seconds + 30  # Give extra time for connection
        )
    except FileNotFoundError:
        raise AudioCaptureError(
            "FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.\n"
            "Download from: https://ffmpeg.org/download.html"
        )
    except subprocess.TimeoutExpired:
        raise AudioCaptureError("Timeout while capturing audio from stream")

    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        raise AudioCaptureError(f"Failed to capture audio. FFmpeg error:\n{result.stderr}")

    return audio_path


def cleanup_audio(audio_path: str) -> None:
    """Delete the temporary audio file."""
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except OSError:
        pass  # Ignore cleanup errors
