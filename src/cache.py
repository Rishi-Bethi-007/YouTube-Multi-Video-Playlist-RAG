import json
import hashlib
from typing import Any, Optional
import redis
from src.config import REDIS_URL

_r = redis.Redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL else None

def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def get_json(key: str) -> Optional[Any]:
    if not _r:
        return None
    v = _r.get(key)
    return json.loads(v) if v else None

def set_json(key: str, value: Any, ttl_seconds: int) -> None:
    if not _r:
        return
    _r.setex(key, ttl_seconds, json.dumps(value, ensure_ascii=False))

def get_text(key: str) -> Optional[str]:
    if not _r:
        return None
    return _r.get(key)

def set_text(key: str, value: str, ttl_seconds: int) -> None:
    if not _r:
        return
    _r.setex(key, ttl_seconds, value)
