<<<<<<< HEAD
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
=======
# PDF / PPT 처리 로직
import os
import shutil
import uuid

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

# LangChain
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from app.core.llm_client import summary_chain, keyword_chain

from pptx import Presentation

from app.crud import file_crud
from app.core.enums import ChromaDB, CHROMA_PERSIST_DIR
from app.db.file_schemas import (DocumentSummaryItem, DocumentSummaryDetail)

def extract_text_from_pptx(file_path: str) -> str:
    """PPTX 파일에서 텍스트 추출"""
    prs = Presentation(file_path)
    texts: list[str] = []

    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                texts.append(shape.text)

    return "\n".join(texts)

async def register_document(db: Session, file: UploadFile) -> str:
    """
    PDF / PPT 업로드 → 요약 생성 → VectorDB 저장 → MySQL 저장
    """
    file_uuid = str(uuid.uuid4())
    filename_lower = file.filename.lower()
    temp_file_path = f"temp_{file.filename}"

    try:
        # 임시 파일 저장
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 파일 유형별 텍스트 로드
        if filename_lower.endswith(".pdf"):
            loader = PyPDFLoader(temp_file_path)
            docs = loader.load()

        elif filename_lower.endswith(".pptx"):
            text = extract_text_from_pptx(temp_file_path)
            docs = [Document(page_content=text, metadata={})]

        else:
            raise HTTPException(
                status_code=400,
                detail="지원하지 않는 파일 형식입니다. (PDF / PPTX만 가능)"
            )

        full_text = "\n".join(doc.page_content for doc in docs)

        # 요약 생성
        summary: str = summary_chain.invoke({
            "context": full_text
        })

        # 키워드 추출
        keyword_text: str = keyword_chain.invoke({
            "context": summary
        })

        keywords: list[str] = [
            k.strip() for k in keyword_text.split(",") if k.strip()
        ]

        keywords_str = ", ".join(keywords)

        # 문서 청킹
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = splitter.split_documents(docs)

        for doc in splits:
            doc.metadata.update({
                "document_uuid": file_uuid,
                "filename": file.filename,
                "keywords": keywords_str,
            })

        # ChromaDB 저장
        vectorstore = Chroma(
            collection_name=ChromaDB.COLLECTION_NAME.value,
            embedding_function=OpenAIEmbeddings(
                model="text-embedding-3-small"
            ),
            persist_directory=CHROMA_PERSIST_DIR,
        )
        vectorstore.add_documents(splits)

        # MySQL 저장
        file_crud.create_pdf(
            db=db,
            uuid=file_uuid,
            name=file.filename,
            summary=summary,
            keywords=keywords_str
        )

        return summary

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def list_documents(db: Session, limit: int, offset: int):
    """
    업로드된 문서 요약 목록 조회
    """
    pdf_files = file_crud.list_documents(
        db=db,
        limit=limit,
        offset=offset,
    )

    results: list[DocumentSummaryItem] = []

    for pdf in pdf_files:
        results.append(
            DocumentSummaryItem(
                uuid=pdf.uuid,
                name=pdf.name,
                summary=pdf.summary,
                keywords=pdf.keywords.split(", ") if pdf.keywords else [],
                created_at=pdf.created_at,
            )
        )

    return results

def get_document_detail(db: Session, uuid: str):
    """
    특정 문서 요약 상세 조회
    """
    document = file_crud.get_document_by_uuid(db, uuid)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="문서를 찾을 수 없습니다."
        )

    return DocumentSummaryDetail(
        uuid=document.uuid,
        name=document.name,
        summary=document.summary,
        keywords=document.keywords.split(", ") if document.keywords else [],
        created_at=document.created_at,
    )
>>>>>>> 76bd24bd7765d2349170d85f79950c39c9ca3713
