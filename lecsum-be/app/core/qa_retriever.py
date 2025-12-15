# RAG 검색 로직 (문서 기반 Q&A)
import chromadb
from langchain_openai import OpenAIEmbeddings
from app.core.enums import ChromaDB, CHROMA_PERSIST_DIR


embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIR,
    settings=chromadb.Settings(anonymized_telemetry=False)
)

collection = client.get_or_create_collection(ChromaDB.COLLECTION_NAME.value)

def save_chunks(document_id: int, chunks: list[str]):
    vectors = embeddings.embed_documents(chunks)
    for idx, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"{document_id}_{idx}"],
            metadatas=[{"document_id": document_id, "chunk_index": idx}],
            embeddings=[vectors[idx]]
        )