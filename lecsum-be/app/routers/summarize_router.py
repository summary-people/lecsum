# app/routers/summarize_router.py

from fastapi import UploadFile, File, APIRouter, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from typing import List

from app.db.schemas import CommonResponse
from app.db.database import get_db
from app.services import file_service
from app.db.file_schemas import (
    DocumentSummaryItem,
    DocumentSummaryDetail,
)

load_dotenv()

router = APIRouter(
    prefix="/api/uploads",
    tags=["Summarize"],
)

@router.post(
    "/documents",
    response_model=CommonResponse[DocumentSummaryDetail],
    summary="PDF / PPT 업로드 및 요약 생성",
    description="""
PDF 또는 PPT(PPTX) 파일을 업로드하여 문서를 요약합니다.
- 요약 스타일은 summary_type으로 제어합니다. 예: lecture | bullet | exam
- 핵심 문장은 내부 기준 Top-5로 고정됩니다.
""",
)
async def upload_document(
    file: UploadFile = File(...),
    summary_type: str = "lecture",
    db: Session = Depends(get_db),
):
    document = await file_service.register_document(
        db=db,
        file=file,
        summary_type=summary_type
    )
    return CommonResponse(data=document)


@router.get(
    "/documents",
    response_model=CommonResponse[List[DocumentSummaryItem]],
    summary="업로드한 문서 요약 목록 조회",
)
def list_documents(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    documents = file_service.list_documents(
        db=db,
        limit=limit,
        offset=offset,
    )
    return CommonResponse(data=documents)


@router.get(
    "/documents/{id}",
    response_model=CommonResponse[DocumentSummaryDetail],
    summary="업로드한 문서 요약 상세 조회",
)
def get_document_detail(
    id: int,
    db: Session = Depends(get_db),
):
    document = file_service.get_document_detail(
        db=db,
        document_id=id,
    )
    return CommonResponse(data=document)