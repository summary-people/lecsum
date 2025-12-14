# PDF 업로드 → 청킹 → ChromaDB(VectorStore) 저장 (MySQL 없음)
import os
import shutil
import uuid
from typing import Dict
from fastapi import UploadFile

# LangChain 관련 임포트 (PDF 로드/청킹만 활용)
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 내부 모듈: VectorStore 래퍼 사용
from app.db.vector_store import get_vector_store


async def register_pdf(file: UploadFile) -> Dict:
    """
    PDF를 받아 텍스트 청킹 후 VectorStore(Chroma)에 저장
    - MySQL은 사용하지 않음
    - 각 청크는 동일한 file_uuid 메타를 공유
    - 반환: 업로드 결과 메타 정보
    """
    # 1. UUID 생성
    file_uuid = str(uuid.uuid4())
    
    # 2. 임시 파일 경로 생성
    temp_file_path = f"temp_{file.filename}"
    
    try:
        # 파일 디스크에 임시 저장
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # PDF 로드
        loader = PyPDFLoader(temp_file_path)
        docs = loader.load()

        # 메타데이터 주입
        for doc in docs:
            doc.metadata["file_id"] = file_uuid
            doc.metadata["file_name"] = file.filename

        # 청킹 (Chunking)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = splitter.split_documents(docs)

        # VectorStore에 저장 (원문 조각)
        vs = get_vector_store()
        payload = []
        for i, chunk in enumerate(splits):
            payload.append({
                "id": f"{file_uuid}-{i}",
                "title": file.filename,
                "text": chunk.page_content,
                "summary": None,
                "file_id": file_uuid,  # file_id 명시적으로 추가
            })

        if payload:
            vs.add_documents(payload)

        # ============================================================
        # [MySQL 통합 시 추가할 코드]
        # PDF 메타데이터를 MySQL에 저장
        # ============================================================
        # from app.db.database import get_db
        # from app.db.models import PDFDocument
        # 
        # db = next(get_db())  # 또는 의존성 주입으로 받기
        # pdf_record = PDFDocument(
        #     file_id=file_uuid,
        #     file_name=file.filename,
        #     num_pages=len(docs),
        #     num_chunks=len(splits),
        #     upload_date=datetime.utcnow(),
        #     status="processed"
        # )
        # db.add(pdf_record)
        # db.commit()
        # db.refresh(pdf_record)
        # ============================================================

        return {
            "file_id": file_uuid,
            "file_name": file.filename,
            "num_pages": len(docs),
            "num_chunks": len(splits),
            "persist_dir": "./data/chroma",
            "collection": "documents",
            "status": "stored_in_chroma",
        }

    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
