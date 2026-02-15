"""
Dedup is enforced via:

1)Chunk.id as stable SHA1 (primary key)

2)Unique constraint on (video_id, start, end) too (extra guard)

3)Ingestion log table tracks if a video already indexed for a namespace + embedding model

"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from src.db import Base

class Video(Base):
    __tablename__ = "videos"
    id = Column(String, primary_key=True)     # video_id
    title = Column(String, nullable=True)

    chunks = relationship("Chunk", back_populates="video")

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(String, primary_key=True)     # stable sha1
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)

    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

    video = relationship("Video", back_populates="chunks")

    __table_args__ = (
        UniqueConstraint("video_id", "start", "end", name="uq_chunk_video_time"),
    )

Index("ix_chunks_video_id", Chunk.video_id)
Index("ix_chunks_video_time", Chunk.video_id, Chunk.start)

class IngestionLog(Base):
    """
    Tracks idempotent ingestion for a given namespace + embed model.
    If a video is already ingested, we skip (unless you force rebuild).
    """
    __tablename__ = "ingestion_log"
    id = Column(Integer, primary_key=True, autoincrement=True)

    namespace = Column(String, nullable=False)
    embed_model = Column(String, nullable=False)
    video_id = Column(String, nullable=False)

    status = Column(String, nullable=False, default="done")  # done|failed
    error = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("namespace", "embed_model", "video_id", name="uq_ingest_identity"),
    )

Index("ix_ingestion_namespace", IngestionLog.namespace)
