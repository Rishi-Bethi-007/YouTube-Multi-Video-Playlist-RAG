import json
import time
from pathlib import Path
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript

from src.subtitles_fallback import fetch_subtitles_with_ytdlp

CACHE_DIR = Path("data/transcripts")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _path(video_id: str) -> Path:
    return CACHE_DIR / f"{video_id}.json"

def _normalize(items: list[dict]) -> list[dict]:
    out = []
    for it in items:
        text = (it.get("text") or "").strip()
        if not text:
            continue
        start = float(it.get("start", 0.0))
        if "duration" in it:
            dur = float(it.get("duration", 0.0))
        elif "end" in it:
            dur = max(0.0, float(it["end"]) - start)
        else:
            dur = 0.0
        out.append({"text": text, "start": start, "duration": dur})
    return out

def _select_transcript(video_id: str, preferred_langs: list[str]) -> list[dict]:
    transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

    for lang in preferred_langs:
        try:
            return transcripts.find_manually_created_transcript([lang]).fetch()
        except Exception:
            pass

    for lang in preferred_langs:
        try:
            return transcripts.find_generated_transcript([lang]).fetch()
        except Exception:
            pass

    t = next(iter(transcripts))
    return t.fetch()

def load_or_fetch_transcript(
    video_id: str,
    preferred_langs: Optional[list[str]] = None,
    retries: int = 3,
    backoff_s: float = 1.5,
) -> list[dict]:
    preferred_langs = preferred_langs or ["en", "en-US", "en-GB"]

    p = _path(video_id)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))

    # 1) Try youtube-transcript-api (fast path)
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            items = _select_transcript(video_id, preferred_langs)
            items = _normalize(items)
            if items:
                p.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
                return items
            raise RuntimeError("Transcript fetched but empty after normalization.")
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            # Hard fail for API path; try fallback next
            last_err = e
            break
        except (CouldNotRetrieveTranscript, Exception) as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff_s * attempt)
                continue
            break

    # 2) Fallback: yt-dlp subtitles extraction
    try:
        items = fetch_subtitles_with_ytdlp(video_id, lang="en")
        items = _normalize(items)
        if not items:
            raise RuntimeError("yt-dlp returned subtitles but they were empty.")
        p.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
        return items
    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch transcript for {video_id}. "
            f"API error: {type(last_err).__name__ if last_err else 'None'}: {last_err}. "
            f"Fallback error: {type(e).__name__}: {e}"
        )
