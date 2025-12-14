# 파일 업로드 API
from fastapi import UploadFile, File, APIRouter, Depends

from dotenv import load_dotenv
load_dotenv()
from app.db.schemas import CommonResponse
from app.db.database import get_db
from app.services import file_service
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/upload",
    tags=["upload"]
)


# PDF 업로드 및 임베딩
@router.post("/pdfs", response_model=CommonResponse[None])
async def upload_pdf(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db) # DB 세션 주입
):
    
    await file_service.register_pdf(db=db, file=file)
    
    return CommonResponse(data=None)