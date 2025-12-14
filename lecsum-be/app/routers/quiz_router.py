# 모의시험 생성 및 채점 API
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.db.quiz_schemas import *
from app.db.schemas import CommonResponse
from app.db.database import get_db
from app.services import quiz_service

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

# 채점 API
@router.post("/grade", response_model=CommonResponse[GradeResponse])
async def grade_batch_quiz(
    request: GradeRequest, 
    db: Session = Depends(get_db)
):
    """
    퀴즈 답안을 받아 일괄 채점하고 결과를 저장합니다.
    """
    result = await quiz_service.grade_quiz_set(db, request)
    
    return CommonResponse(
        message="채점이 완료되었습니다.",
        data=result
    )