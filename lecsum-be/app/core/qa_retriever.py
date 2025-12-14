# RAG 검색 로직 (문서 기반 Q&A)
from typing import List
from chromadb import Client
from chromadb.config import Settings

from app.core.llm_client import embed_text
from app.utils.logger import get_logger

logger = get_logger(__name__)


class QARetriever:
    """
    RAG(Retrieval-Augmented Generation)에서 Retrieval 역할만 담당하는 클래스

    역할:
    - 사용자 질문을 embedding
    - ChromaDB에서 유사한 문서 chunk 검색
    - LLM에 전달할 context 문자열 생성

    ❌ LLM 호출 금지
    ❌ DB Insert / Update 금지
    """

    def __init__(
        self,
        persist_directory: str = "vectorstore",
        collection_name: str = "lecture_chunks",
    ):
        self.client = Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False,
            )
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

        logger.info(
            f"QARetriever initialized (collection={collection_name})"
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> str:
        """
        사용자 질문을 기반으로 ChromaDB에서 관련 문서 context를 조회

        :param query: 사용자 질문
        :param top_k: 검색할 문서 chunk 개수
        :return: LLM 입력용 context 문자열
        """

        if not query or not query.strip():
            logger.warning("Empty query received")
            return ""

        try:
            # 1. 질문 embedding 생성
            query_embedding = embed_text(query)

            # 2. similarity search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )

            # 3. 검색 결과 추출
            documents: List[str] = results.get("documents", [[]])[0]

            if not documents:
                logger.info("No related documents found")
                return ""

            # 4. context 정제
            context_chunks = [
                doc.strip()
                for doc in documents
                if doc and doc.strip()
            ]

            context = "\n\n".join(context_chunks)

            logger.debug(
                f"Retrieved {len(context_chunks)} context chunks"
            )

            return context

        except Exception as e:
            logger.exception("Error occurred during retrieval")
            return ""