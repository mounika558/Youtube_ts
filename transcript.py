import re
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """Pull the 11-character video ID out of common YouTube URL formats."""
    patterns = [
        r"v=([\w-]{11})",                                   # youtube.com/watch?v=ID
        r"youtu\.be/([\w-]{11})",                           # youtu.be/ID
        r"youtube\.com/(?:shorts|embed|live)/([\w-]{11})",  # shorts / embed / live
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Could not find a video ID in that URL.")


def get_transcript(url: str) -> str:
    """Return the full transcript of a video as one long string."""
    video_id = extract_video_id(url)
    api = YouTubeTranscriptApi()

    # Ask YouTube which transcripts exist for this video
    available = list(api.list(video_id))

    # Rank them: English variants first (en, en-IN, en-US...),
    # and within that, human-written captions before auto-generated ones.
    best_first = sorted(
        available,
        key=lambda t: (not t.language_code.startswith("en"), t.is_generated),
    )

    fetched = best_first[0].fetch()
    return " ".join(snippet.text for snippet in fetched)