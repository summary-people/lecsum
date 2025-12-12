# vector_service.py
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from typing import List

from core.enums import ChromaDB


chroma = Chroma(
    persist_directory=ChromaDB.PERSIST_DIRECTORY,
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_name=ChromaDB.COLLECTION_NAME
)