import asyncio
from dataclasses import dataclass
from typing import Optional
from shazamio import Shazam


@dataclass
class SongResult:
    """Result from song recognition."""
    found: bool
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[str] = None

    def __str__(self) -> str:
        if not self.found:
            return "No song detected"
        parts = [f"{self.title} by {self.artist}"]
        if self.album:
            parts.append(f"Album: {self.album}")
        if self.year:
            parts.append(f"({self.year})")
        return " - ".join(parts)


class SongRecognitionError(Exception):
    """Raised when song recognition fails."""
    pass


async def _recognize_async(audio_path: str) -> SongResult:
    """Async implementation of song recognition."""
    shazam = Shazam()

    try:
        result = await shazam.recognize(audio_path)
    except Exception as e:
        raise SongRecognitionError(f"Shazam API error: {e}")

    # Parse the result
    if not result or "track" not in result:
        return SongResult(found=False)

    track = result["track"]

    return SongResult(
        found=True,
        title=track.get("title"),
        artist=track.get("subtitle"),
        album=track.get("sections", [{}])[0].get("metadata", [{}])[0].get("text") if track.get("sections") else None,
        year=None  # Shazam doesn't always provide year in a consistent place
    )


def recognize_song(audio_path: str) -> SongResult:
    """
    Recognize a song from an audio file.

    Args:
        audio_path: Path to the audio file to analyze

    Returns:
        SongResult with song information if found
    """
    return asyncio.run(_recognize_async(audio_path))
