import os
from enum import Enum

# 프로젝트 기준 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "vectorstore", "chroma")

class ChromaDB(str, Enum):
    COLLECTION_NAME = "lecture_docs"