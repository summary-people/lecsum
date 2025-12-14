# RAG 검색 로직 (문서 기반 Q&A)
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

client = chromadb.Client(
    Settings(
        persist_directory="vectorstore",
        anonymized_telemetry=False
    )
)

collection = client.get_or_create_collection("documents")

def save_chunks(document_id: int, chunks: list[str]):
    for idx, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"{document_id}_{idx}"],
            metadatas=[{"document_id": document_id, "chunk_index": idx}]
        )