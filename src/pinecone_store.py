from pinecone import Pinecone, ServerlessSpec
from src.config import PINECONE_API_KEY, PINECONE_INDEX, PINECONE_CLOUD, PINECONE_REGION

def pc() -> Pinecone:
    return Pinecone(api_key=PINECONE_API_KEY)

def ensure_index(dimension: int, metric: str = "cosine"):
    p = pc()
    existing = [i["name"] for i in p.list_indexes()]
    if PINECONE_INDEX not in existing:
        p.create_index(
            name=PINECONE_INDEX,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
        )
    return p.Index(PINECONE_INDEX)
