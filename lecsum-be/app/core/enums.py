from enum import Enum
import os

os.environ["USER_AGENT"]="myDB/1.0"

class ChromaDB(str, Enum):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # file_path = os.path.join(base_dir, "../database/products.txt")

    COLLECTION_NAME = "lecture_docs"
    PERSIST_DIRECTORY = os.path.abspath(os.path.join(base_dir, "../database/chroma"))

