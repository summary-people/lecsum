# 공부 챗봇 API (VectorStore 기반)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

from app.db.mentor_schemas import ChatRequest, ChatResponse, RecommendRequest, RecommendResponse
from app.db.schemas import CommonResponse
from app.services import chatbot_service

router = APIRouter(
    prefix="/api/chatbot",
    tags=["Chatbot"]
)

# Q&A 챗봇 API
@router.post("/chat", response_model=CommonResponse[ChatResponse])
async def chat_with_lecture(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    강의 자료 기반 Q&A 챗봇 (Chroma 검색)
    - 사용자의 질문에 대해 벡터 DB에서 관련 자료를 검색하여 답변합니다.
    - 대화 히스토리를 포함하여 맥락 있는 답변을 제공합니다.
    - pdf_id는 MySQL 문서 id(정수)를 사용합니다.
    """
    result = await chatbot_service.chat_with_documents(request, db)
    
    return CommonResponse(
        message="답변이 생성되었습니다.",
        data=result
    )

# 오픈소스 자료 추천 API
@router.post("/recommend", response_model=CommonResponse[RecommendResponse])
async def recommend_learning_resources(
    request: RecommendRequest,
    db: Session = Depends(get_db)
):
    """
    강의 내용 기반 오픈소스 학습 자료 추천 (MySQL 키워드 + 웹 검색)
    - 강의 내용과 관련된 GitHub 저장소, 문서, 튜토리얼 등을 추천합니다.
    - MySQL에 저장된 키워드를 사용하여 효율적으로 검색합니다.
    """
    result = await chatbot_service.recommend_resources(request, db)
    
    return CommonResponse(
        message="추천 자료가 생성되었습니다.",
        data=result
    )
