import subprocess
from pathlib import Path
import webvtt

TMP_DIR = Path("data/transcripts")
TMP_DIR.mkdir(parents=True, exist_ok=True)

def fetch_subtitles_with_ytdlp(video_id: str, lang: str = "en") -> list[dict]:
    """
    Uses yt-dlp to fetch subtitles (manual or auto) as VTT, then converts to
    [{"text":..., "start":..., "duration":...}, ...]
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    outtmpl = str(TMP_DIR / f"{video_id}.%(ext)s")

    # Try manual subs first, then auto subs
    cmds = [
        ["yt-dlp", "--skip-download", "--write-subs", "--sub-lang", lang, "--sub-format", "vtt", "-o", outtmpl, url],
        ["yt-dlp", "--skip-download", "--write-auto-subs", "--sub-lang", lang, "--sub-format", "vtt", "-o", outtmpl, url],
    ]

    vtt_path = None
    last_err = None

    for cmd in cmds:
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            # yt-dlp writes something like: VIDEOID.en.vtt or VIDEOID.en-GB.vtt etc.
            candidates = sorted(TMP_DIR.glob(f"{video_id}*.vtt"))
            if candidates:
                vtt_path = candidates[0]
                break
        except Exception as e:
            last_err = e

    if not vtt_path:
        raise RuntimeError(f"yt-dlp subtitles not available for {video_id}. Last error: {last_err}")

    items: list[dict] = []
    for cap in webvtt.read(str(vtt_path)):
        text = (cap.text or "").replace("\n", " ").strip()
        if not text:
            continue
        start = _ts_to_seconds(cap.start)
        end = _ts_to_seconds(cap.end)
        items.append({"text": text, "start": float(start), "duration": float(max(0.0, end - start))})

    return items

def _ts_to_seconds(ts: str) -> float:
    # "00:01:02.345"
    hh, mm, rest = ts.split(":")
    ss, ms = rest.split(".")
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000.0
