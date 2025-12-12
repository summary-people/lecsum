# PDF/PPT 처리 로직
import os
import shutil
import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session

# LangChain 관련 임포트
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# 내부 모듈 임포트
from crud import file_crud
from core.enums import ChromaDB 

async def register_pdf(db: Session, file: UploadFile):
    # 1. UUID 생성
    file_uuid = str(uuid.uuid4())
    
    # 2. 임시 파일 경로 생성
    temp_file_path = f"temp_{file.filename}"
    
    try:
        # 파일 디스크에 임시 저장
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # VectorDB 저장
        loader = PyPDFLoader(temp_file_path)
        docs = loader.load()

        # 메타데이터 주입
        for doc in docs:
            doc.metadata["file_id"] = file_uuid     # UUID
            doc.metadata["file_name"] = file.filename

        # 청킹 (Chunking)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = splitter.split_documents(docs)

        # ChromaDB 저장
        Chroma.from_documents(
            documents=splits,
            embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
            persist_directory=ChromaDB.PERSIST_DIRECTORY,
            collection_name=ChromaDB.COLLECTION_NAME 
        )

        # MySQL 저장 (CRUD 호출)
        # VectorDB 저장이 성공했을 때만 실행됨
        saved_pdf = file_crud.create_pdf(db=db, uuid=file_uuid, name=file.filename)
        
        return saved_pdf

    finally:
        #  임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
