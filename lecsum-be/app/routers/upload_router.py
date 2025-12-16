# 파일 업로드 API
from fastapi import UploadFile, File, APIRouter, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.db.schemas import CommonResponse
from app.db.database import get_db
from app.services import file_service

from typing import List
from app.db.file_schemas import (DocumentSummaryItem, DocumentSummaryDetail)

load_dotenv()

router = APIRouter(
    prefix="/api/uploads",
    tags=["Upload"],
)

@router.post(
    "/documents",
    response_model=CommonResponse[str],
    summary="PDF / PPT 업로드 및 요약 생성",
    description="""
PDF 또는 PPT(PPTX) 파일을 업로드하면 다음 과정을 수행합니다.

### 처리 절차
1. 문서 파일(PDF/PPTX) 업로드
2. 파일 유형 판별
3. 문서 텍스트 추출
   - PDF: PDF 파서 사용
   - PPTX: 슬라이드 텍스트 추출
4. 문서 요약 생성 (LLM)
5. 문서 chunk 분할
6. VectorDB(ChromaDB)에 임베딩 저장
7. 요약 결과 반환

### 지원 파일 형식
- PDF (.pdf)
- PowerPoint (.pptx)

### 저장 정보
- 요약 결과: MySQL 저장
- 문서 임베딩: ChromaDB 저장 (RAG / 퀴즈 생성용)
""",
    responses={
        200: {
            "description": "요약 생성 성공",
        },
        400: {
            "description": "지원하지 않는 파일 형식",
        },
        500: {
            "description": "문서 처리 중 서버 오류",
        },
    },
)
async def upload_document(
    file: UploadFile = File(
        ...,
        description="PDF(.pdf) 또는 PPT(.pptx) 파일",
    ),
    db: Session = Depends(get_db),
):
    summary = await file_service.register_document(
        db=db,
        file=file
    )
    return CommonResponse(data=summary)

@router.get(
    "/documents",
    response_model=CommonResponse[List[DocumentSummaryItem]],
    summary="업로드한 문서 요약 목록 조회",
    description="""
업로드된 PDF / PPT 문서들의 요약 목록을 조회합니다.

- 최신 업로드 순으로 정렬됩니다.
- RAG / 퀴즈 생성을 위한 uuid를 포함합니다.
""",
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
    "/documents/{uuid}",
    response_model=CommonResponse[DocumentSummaryDetail],
    summary="업로드한 문서 요약 상세 조회",
    description="""
특정 문서(PDF / PPT)의 요약 내용을 상세 조회합니다.

- uuid는 업로드 시 생성된 문서 고유 식별자입니다.
- RAG 질의 / 퀴즈 생성 시 사용됩니다.
""",
)
def get_document_detail(
    uuid: str,
    db: Session = Depends(get_db),
):
    document = file_service.get_document_detail(
        db=db,
        uuid=uuid,
    )
    return CommonResponse(data=document)
