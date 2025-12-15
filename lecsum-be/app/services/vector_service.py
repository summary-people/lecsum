# vector_service.py
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.enums import ChromaDB, CHROMA_PERSIST_DIR


def get_vectorstore() -> Chroma:
    """
    Chroma VectorStore 인스턴스 반환
    """
    return Chroma(
        collection_name=ChromaDB.COLLECTION_NAME.value,
        embedding_function=OpenAIEmbeddings(
            model="text-embedding-3-small"
        ),
        persist_directory=CHROMA_PERSIST_DIR,
    )


def get_retriever(document_id: str):
    """
    특정 PDF(document_id)에 대한 retriever 생성
    """
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 3,
            "filter": {"document_uuid": document_id}
        },
    )

async def get_relevant_documents(retriever, query: str) -> str:
    """
    Retriever를 통해 관련 문서 검색
    """
    documents = await retriever.ainvoke(query)
    return "\n\n".join(doc.page_content for doc in documents)