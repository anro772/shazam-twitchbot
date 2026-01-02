# Twitch Song Recognition Bot

CLI tool that identifies songs playing on a Twitch stream using Shazam.

## Requirements

- Python 3.10+
- FFmpeg (must be in PATH)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.json`:

```json
{
  "stream_url": "https://twitch.tv/channelname",
  "duration_seconds": 10,
  "cleanup_audio": true
}
```

- `stream_url` - Twitch stream to listen to
- `duration_seconds` - How long to capture (10-15 recommended)
- `cleanup_audio` - Delete temp audio file after recognition (set to `false` to keep it)

## Usage

```bash
python main.py
```

Or override config with CLI args:

```bash
python main.py --url https://twitch.tv/channelname --duration 15
```

## How It Works

1. Connects to the live Twitch stream via Streamlink
2. Captures audio from the live edge (current moment) using FFmpeg
3. Sends audio to Shazam for recognition
4. Displays song title and artist

## Notes

- Stream must be live
- Works best when music is clear (less talking/gameplay noise)
- Recognition may fail if audio is too noisy or no music is playing
