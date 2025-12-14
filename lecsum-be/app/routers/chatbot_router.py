# 공부 챗봇 API (VectorStore 기반, MySQL 없음)
from fastapi import APIRouter

# ============================================================
# [MySQL 통합 시 추가할 import]
# from fastapi import Depends
# from sqlalchemy.orm import Session
# from app.db.database import get_db
# ============================================================

from app.db.mentor_schemas import ChatRequest, ChatResponse, RecommendRequest, RecommendResponse
from app.db.schemas import CommonResponse
from app.services import chatbot_service

router = APIRouter(
    prefix="/api/chatbot",
    tags=["chatbot"]
)

# Q&A 챗봇 API
@router.post("/chat", response_model=CommonResponse[ChatResponse])
async def chat_with_lecture(
    request: ChatRequest,
    # db: Session = Depends(get_db)  # [MySQL 통합 시] DB 의존성 추가
):
    """
    강의 자료 기반 Q&A 챗봇 (VectorStore 검색)
    - 사용자의 질문에 대해 벡터 DB에서 관련 자료를 검색하여 답변합니다.
    - 대화 히스토리를 포함하여 맥락 있는 답변을 제공합니다.
    """
    # [MySQL 통합 시] chatbot_service에 db 전달: result = await chatbot_service.chat_with_documents(request, db)
    result = await chatbot_service.chat_with_documents(request)
    
    return CommonResponse(
        message="답변이 생성되었습니다.",
        data=result
    )

# 오픈소스 자료 추천 API
@router.post("/recommend", response_model=CommonResponse[RecommendResponse])
async def recommend_learning_resources(request: RecommendRequest):
    """
    강의 내용 기반 오픈소스 학습 자료 추천 (VectorStore + 웹 검색)
    - 강의 내용과 관련된 GitHub 저장소, 문서, 튜토리얼 등을 추천합니다.
    - 특정 주제를 지정하면 해당 주제에 맞는 자료를 추천합니다.
    """
    result = await chatbot_service.recommend_resources(request)
    
    return CommonResponse(
        message="추천 자료가 생성되었습니다.",
        data=result
    )
