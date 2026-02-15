import re
from pytube import Playlist

_VIDEO_ID_RE = re.compile(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})")

def extract_video_id(url: str) -> str:
    m = _VIDEO_ID_RE.search(url)
    if not m:
        raise ValueError(f"Could not parse video id from URL: {url}")
    return m.group(1)

def extract_video_ids(input_text: str) -> list[str]:
    t = input_text.strip()
    # Playlist URL (common pattern)
    if "list=" in t and "watch" not in t:
        pl = Playlist(t)
        return [extract_video_id(u) for u in pl.video_urls]

    urls = [u.strip() for u in t.splitlines() if u.strip()]
    return [extract_video_id(u) for u in urls]
