import hashlib
from sqlalchemy import select
from langchain_openai import OpenAIEmbeddings
from src.config import OPENAI_API_KEY, EMBED_MODEL
from src.db import SessionLocal
from src.models import Video, Chunk, IngestionLog
from src.pinecone_store import ensure_index

def stable_chunk_id(video_id: str, start: int, end: int, text: str) -> str:
    return hashlib.sha1(f"{video_id}|{start}|{end}|{text}".encode("utf-8")).hexdigest()

def already_ingested(namespace: str, embed_model: str, video_id: str) -> bool:
    db = SessionLocal()
    try:
        row = db.execute(
            select(IngestionLog).where(
                IngestionLog.namespace == namespace,
                IngestionLog.embed_model == embed_model,
                IngestionLog.video_id == video_id,
                IngestionLog.status == "done",
            )
        ).scalar_one_or_none()
        return row is not None
    finally:
        db.close()

def mark_ingest(namespace: str, embed_model: str, video_id: str, status: str, error: str | None = None) -> None:
    db = SessionLocal()
    try:
        row = db.execute(
            select(IngestionLog).where(
                IngestionLog.namespace == namespace,
                IngestionLog.embed_model == embed_model,
                IngestionLog.video_id == video_id,
            )
        ).scalar_one_or_none()
        if row is None:
            row = IngestionLog(namespace=namespace, embed_model=embed_model, video_id=video_id, status=status, error=error)
            db.add(row)
        else:
            row.status = status
            row.error = error
        db.commit()
    finally:
        db.close()

def ingest_video(video_id: str, title: str | None, chunks: list, namespace: str, force: bool = False) -> dict:
    """
    Returns stats dict.
    Dedup:
      - If ingestion_log says done and not force -> skip entire video
      - Chunk primary key prevents duplicates; we only embed+upsert newly inserted chunks
    """
    if (not force) and already_ingested(namespace, EMBED_MODEL, video_id):
        return {"video_id": video_id, "skipped": True, "new_chunks": 0}

    db = SessionLocal()
    new_rows: list[Chunk] = []

    try:
        # upsert video
        v = db.get(Video, video_id)
        if not v:
            v = Video(id=video_id, title=title)
            db.add(v)
        elif title and not v.title:
            v.title = title

        # insert chunks if not exist
        for c in chunks:
            cid = stable_chunk_id(video_id, int(c.start), int(c.end), c.text)
            if db.get(Chunk, cid) is not None:
                continue
            row = Chunk(id=cid, video_id=video_id, start=int(c.start), end=int(c.end), text=c.text)
            db.add(row)
            new_rows.append(row)

        db.commit()

        if not new_rows:
            mark_ingest(namespace, EMBED_MODEL, video_id, status="done", error=None)
            return {"video_id": video_id, "skipped": False, "new_chunks": 0}

        emb = OpenAIEmbeddings(model=EMBED_MODEL, api_key=OPENAI_API_KEY)
        dim = len(emb.embed_query("dimension probe"))
        index = ensure_index(dimension=dim)

        texts = [r.text for r in new_rows]
        vecs = emb.embed_documents(texts)

        vectors = []
        for r, vec in zip(new_rows, vecs):
            meta = {"video_id": r.video_id, "start": r.start, "end": r.end}
            vectors.append((r.id, vec, meta))

        B = 100
        for i in range(0, len(vectors), B):
            index.upsert(vectors=vectors[i:i+B], namespace=namespace)

        mark_ingest(namespace, EMBED_MODEL, video_id, status="done", error=None)
        return {"video_id": video_id, "skipped": False, "new_chunks": len(new_rows)}

    except Exception as e:
        mark_ingest(namespace, EMBED_MODEL, video_id, status="failed", error=str(e))
        raise
    finally:
        db.close()
