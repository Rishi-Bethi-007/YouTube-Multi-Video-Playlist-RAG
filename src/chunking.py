from dataclasses import dataclass

@dataclass
class ChunkObj:
    text: str
    start: int
    end: int

def chunk_transcript(items: list[dict], chunk_chars: int, overlap_chars: int) -> list[ChunkObj]:
    chunks: list[ChunkObj] = []
    buf: list[str] = []
    buf_len = 0
    buf_start = None
    buf_end = None

    def flush():
        nonlocal buf, buf_len, buf_start, buf_end
        if not buf:
            return
        text = " ".join(buf).strip()
        chunks.append(ChunkObj(text=text, start=int(buf_start or 0), end=int(buf_end or (buf_start or 0))))

        if overlap_chars > 0 and len(text) > overlap_chars:
            tail = text[-overlap_chars:]
            buf = [tail]
            buf_len = len(tail)
            buf_start = chunks[-1].end
            buf_end = chunks[-1].end
        else:
            buf, buf_len, buf_start, buf_end = [], 0, None, None

    for seg in items:
        t = (seg.get("text") or "").strip()
        if not t:
            continue
        s = float(seg.get("start", 0.0))
        e = s + float(seg.get("duration", 0.0))

        if buf_start is None:
            buf_start = s
        buf_end = e

        buf.append(t)
        buf_len += len(t) + 1

        if buf_len >= chunk_chars:
            flush()

    flush()
    return chunks
