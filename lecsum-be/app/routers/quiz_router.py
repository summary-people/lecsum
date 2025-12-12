# 모의시험 생성 및 채점 API
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from db.quiz_schemas import *
from db.schemas import CommonResponse
from db.database import get_db
from services import quiz_service

router = APIRouter(
    prefix="/api/quizs",
    tags=["quizs"]
    
)

# 퀴즈 생성 API
@router.post("/generate", response_model=CommonResponse[QuizResponse])
async def generate_quiz(
    request: QuizRequest, 
    db: Session = Depends(get_db)
):
    """
    pdf_id를 받아 퀴즈를 생성하고 DB에 저장 후 반환합니다.
    """
    # Service 호출
    result = await quiz_service.generate_and_save_quiz(db, request)
    
    return CommonResponse(data=result)