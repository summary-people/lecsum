# 챗봇 Q&A 요청/응답 스키마
from pydantic import BaseModel, Field
from typing import List, Optional

# 챗봇 질문 요청 (Chroma 기반, pdf_id는 MySQL 문서 id)
class ChatRequest(BaseModel):
    document_id: Optional[int] = Field(default=None, description="PDF 문서 ID (MySQL id, 없으면 전체 검색)")
    question: str = Field(description="사용자의 질문")
    chat_history: Optional[List[dict]] = Field(
        default=[],
        description="이전 대화 히스토리 [{'role': 'user'/'assistant', 'content': '...'}]"
    )

# 출처 정보 아이템
class SourceItem(BaseModel):
    filename: str = Field(description="파일명")
    page: Optional[int] = Field(default=None, description="페이지 번호 (있는 경우)")
    snippet: str = Field(description="답변 근거가 된 문서 발췌 내용 (최대 150자)")

# 챗봇 응답
class ChatResponse(BaseModel):
    answer: str = Field(description="챗봇의 답변")
    sources: List[SourceItem] = Field(
        default=[],
        description="답변의 근거가 된 문서 출처 (파일명, 페이지, 스니펫)"
    )

# 오픈소스 자료 추천 요청 (MySQL 기반, pdf_id는 MySQL 문서 id)
class RecommendRequest(BaseModel):
    document_id: int = Field(description="PDF 문서 ID (MySQL id, 해당 PDF 내용을 분석하여 자동으로 관련 자료 추천)")

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
