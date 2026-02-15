import os
from dotenv import load_dotenv

# Load local .env (for local development only)
load_dotenv()

def _get(key: str, default: str = "") -> str:
    """
    Priority:
    1. Streamlit Cloud secrets
    2. Environment variables (.env locally)
    3. Default value
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass

    return os.getenv(key, default)


# =========================
# Core API Keys
# =========================

OPENAI_API_KEY = _get("OPENAI_API_KEY")
PINECONE_API_KEY = _get("PINECONE_API_KEY")

# =========================
# Models
# =========================

EMBED_MODEL = _get("EMBED_MODEL", "text-embedding-3-small")
CHAT_MODEL = _get("CHAT_MODEL", "gpt-4o-mini")

# =========================
# Pinecone
# =========================

PINECONE_INDEX = _get("PINECONE_INDEX", "youtube-rag")
PINECONE_CLOUD = _get("PINECONE_CLOUD", "aws")
PINECONE_REGION = _get("PINECONE_REGION", "us-east-1")

# =========================
# Database (NO localhost fallback on cloud)
# =========================

DATABASE_URL = _get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL not configured. "
        "Set it in .env (local) or Streamlit Cloud Secrets."
    )

# =========================
# Redis (optional but recommended)
# =========================

REDIS_URL = _get("REDIS_URL", "")

# =========================
# App Config
# =========================

NAMESPACE = _get("NAMESPACE", "prodv1")

CHUNK_CHARS = int(_get("CHUNK_CHARS", "900"))
CHUNK_OVERLAP_CHARS = int(_get("CHUNK_OVERLAP_CHARS", "150"))

FETCH_K = int(_get("FETCH_K", "30"))
TOP_K = int(_get("TOP_K", "6"))
RERANK_TOP_N = int(_get("RERANK_TOP_N", "6"))

# =========================
# Optional: LangSmith
# =========================

USE_LANGSMITH = _get("USE_LANGSMITH", "false").lower() == "true"
LANGSMITH_API_KEY = _get("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = _get("LANGSMITH_PROJECT", "youtube-rag")
