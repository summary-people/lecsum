"""
간단한 Chroma 기반 벡터 스토어 래퍼.
- 원본 텍스트와 요약본을 함께 임베딩 저장
- 질문/추천 시 유사도 검색 제공
"""
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from openai import OpenAI

load_dotenv()

class VectorStore:
    """문서 임베딩을 저장/조회하는 벡터 스토어"""

    def __init__(
        self,
        persist_dir: str = "./data/chroma",
        collection_name: str = "documents",
        embedding_model: str = "text-embedding-3-small"
    ):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env를 확인하세요.")

        os.makedirs(persist_dir, exist_ok=True)
        self.client = Client(Settings(persist_directory=persist_dir, is_persistent=True))
        self.collection = self.client.get_or_create_collection(collection_name)
        self.embedding_model = embedding_model
        self._openai = OpenAI(api_key=self.api_key)

    def _embed(self, text: str) -> List[float]:
        """OpenAI 임베딩 생성"""
        resp = self._openai.embeddings.create(model=self.embedding_model, input=text)
        return resp.data[0].embedding

    def add_documents(self, docs: List[Dict]):
        """
        문서를 벡터 스토어에 업서트.
        docs: [{"id": str, "title": str, "text": str, "summary": Optional[str], "file_id": Optional[str]}]
        raw/summary 두 개의 벡터를 저장합니다.
        """
        ids, embeddings, metadatas, documents = [], [], [], []
        for doc in docs:
            base_id = str(doc["id"])
            title = doc.get("title", "제목 없음")
            text = doc.get("text", "") or ""
            summary = doc.get("summary")
            file_id = doc.get("file_id")  # file_id 추출

            # 공통 메타데이터
            base_meta = {"doc_id": base_id, "title": title}
            if file_id:
                base_meta["file_id"] = file_id

            # 원본 텍스트
            ids.append(f"{base_id}::raw")
            embeddings.append(self._embed(text))
            metadatas.append({**base_meta, "kind": "raw"})
            documents.append(text)

            # 요약 텍스트가 있으면 별도로 저장
            if summary:
                ids.append(f"{base_id}::summary")
                embeddings.append(self._embed(summary))
                metadatas.append({**base_meta, "kind": "summary"})
                documents.append(summary)

        if ids:
            self.collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    def query(self, query: str, top_k: int = 3, file_id: Optional[str] = None) -> List[Dict]:
        """유사 문서 검색 (file_id 필터 지원)"""
        if not query.strip():
            return []
        emb = self._embed(query)
        
        # file_id 필터 적용
        where_filter = {"file_id": file_id} if file_id else None
        
        res = self.collection.query(
            query_embeddings=[emb], 
            n_results=top_k,
            where=where_filter
        )
        results = []
        for idx in range(len(res.get("ids", [[]])[0])):
            metadata = res["metadatas"][0][idx]
            results.append({
                "id": metadata.get("doc_id"),
                "file_id": metadata.get("file_id"),
                "title": metadata.get("title", "제목 없음"),
                "kind": metadata.get("kind", "raw"),
                "content": res["documents"][0][idx],
                "score": res.get("distances", [[None]])[0][idx]
            })
        return results

    def all_docs_sample(self, top_k: int = 3) -> List[Dict]:
        """
        임의로 상위 몇 개 문서를 가져와 주제 추출 등에 사용.
        (Chroma는 전체 fetch API가 없어 간단히 get과 slicing 조합.)
        """
        if self.collection.count() == 0:
            return []
        # get으로 전부 가져오지 않고, ids를 제한적으로 요청 (여기서는 100개 limit)
        data = self.collection.get(limit=min(100, self.collection.count()))
        docs = []
        for doc_id, meta, doc_text in zip(data.get("ids", []), data.get("metadatas", []), data.get("documents", [])):
            docs.append({
                "id": meta.get("doc_id"),
                "title": meta.get("title", "제목 없음"),
                "kind": meta.get("kind", "raw"),
                "content": doc_text
            })
        # 단순 상위 top_k 반환
        return docs[:top_k]


_vector_store_instance: Optional[VectorStore] = None

def get_vector_store() -> VectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
