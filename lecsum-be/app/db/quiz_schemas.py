# 모의고사 요청/응답 DTO
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class QuizRequest(BaseModel):
    pdf_id: int
    query: str = Field(description="vectorDB 검색 키워드", default="핵심 내용")

# 퀴즈 하나의 구조
class QuizItem(BaseModel):
    id: Optional[int] = None
    question: str = Field(description="문제 지문")
    type: Literal["multiple_choice", "true_false", "short_answer", "fill_in_blank"] = Field(description="문제 유형")
    options: List[str] = Field(description="객관식일 경우 보기 (없으면 빈 리스트)", default=[])
    correct_answer: str = Field(description="정답")
    explanation: str = Field(description="해설")

# 퀴즈 세트 구조
class QuizResponse(BaseModel):
    quiz_set_id: int
    quizzes: List[QuizItem]