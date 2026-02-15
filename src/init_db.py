from src.db import engine
from src.models import Base

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
