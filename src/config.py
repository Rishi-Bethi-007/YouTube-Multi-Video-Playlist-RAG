import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "youtube-rag")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://rag:rag@localhost:5432/ragdb")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

NAMESPACE = os.getenv("NAMESPACE", "prodv1")

CHUNK_CHARS = int(os.getenv("CHUNK_CHARS", "900"))
CHUNK_OVERLAP_CHARS = int(os.getenv("CHUNK_OVERLAP_CHARS", "150"))

FETCH_K = int(os.getenv("FETCH_K", "30"))       # candidates from Pinecone
TOP_K = int(os.getenv("TOP_K", "6"))           # final context count
RERANK_TOP_N = int(os.getenv("RERANK_TOP_N", "6"))

USE_LANGSMITH = os.getenv("USE_LANGSMITH", "false").lower() == "true"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "youtube-rag")
