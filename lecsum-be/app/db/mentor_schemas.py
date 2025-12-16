# 챗봇 Q&A 요청/응답 스키마
from pydantic import BaseModel, Field
from typing import List, Optional

# 챗봇 질문 요청 (VectorStore 기반, pdf_id는 file_uuid prefix로 사용)
class ChatRequest(BaseModel):
    pdf_id: Optional[str] = Field(default=None, description="PDF 파일 UUID (file_id prefix로 필터링, 없으면 전체 검색)")
    question: str = Field(description="사용자의 질문")
    chat_history: Optional[List[dict]] = Field(
        default=[],
        description="이전 대화 히스토리 [{'role': 'user'/'assistant', 'content': '...'}]"
    )

# 챗봇 응답
class ChatResponse(BaseModel):
    answer: str = Field(description="챗봇의 답변")
    sources: List[str] = Field(
        default=[],
        description="답변의 근거가 된 문서 출처"
    )

# 오픈소스 자료 추천 요청 (VectorStore 기반, pdf_id는 file_uuid prefix로 사용)
class RecommendRequest(BaseModel):
    pdf_id: str = Field(description="PDF 파일 UUID (해당 PDF 내용을 분석하여 자동으로 관련 자료 추천)")

# 추천 자료 아이템
class RecommendItem(BaseModel):
    title: str = Field(description="자료 제목")
    description: str = Field(description="자료 설명")
    url: str = Field(description="자료 URL")
    type: str = Field(description="자료 유형 (예: GitHub, Documentation, Tutorial, Video)")

# 자료 추천 응답
class RecommendResponse(BaseModel):
    recommendations: List[RecommendItem] = Field(description="추천 자료 목록")
    summary: str = Field(description="추천 이유 요약")
