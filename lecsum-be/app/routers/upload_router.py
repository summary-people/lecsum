# 파일 업로드 API (VectorStore 기반, MySQL 없음)
from fastapi import UploadFile, File, APIRouter

# ============================================================
# [MySQL 통합 시 추가할 import]
# from fastapi import Depends
# from sqlalchemy.orm import Session
# from app.db.database import get_db
# ============================================================

from dotenv import load_dotenv
load_dotenv()
from app.db.schemas import CommonResponse
from app.services import file_service

router = APIRouter(
    prefix="/api/upload",
    tags=["upload"]
)


# PDF 업로드 및 임베딩 (ChromaDB VectorStore에 저장)
@router.post("/pdfs", response_model=CommonResponse[dict])
async def upload_pdf(
    file: UploadFile = File(...),
    # db: Session = Depends(get_db)  # [MySQL 통합 시] DB 의존성 추가
):
    """
    PDF 파일을 업로드하여 텍스트 추출, 청킹, 벡터 임베딩 후 ChromaDB에 저장합니다.
    
    Returns:
        file_id: 업로드된 파일의 UUID
        file_name: 파일명
        num_chunks: 저장된 청크 개수
    """
    # [MySQL 통합 시] file_service에 db 전달: result = await file_service.register_pdf(file, db)
    result = await file_service.register_pdf(file=file)
    
    return CommonResponse(
        message="PDF가 성공적으로 업로드되고 벡터화되었습니다.",
        data=result
    )