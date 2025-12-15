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

    # [Request] 채점 요청
class GradeRequest(BaseModel):
    quiz_set_id: int             # 시험지 ID (Attempt 생성용)
    quiz_id_list: List[int]      # 문제 ID 리스트 (순서 중요)
    user_answer_list: List[str]  # 사용자 답안 리스트 (문제 ID 순서와 대응)

# [LLM Output] 개별 문제 채점 결과 (LLM이 뱉어낼 구조)
class SingleGradeResult(BaseModel):
    is_correct: bool = Field(description="정답 여부")
    feedback: str = Field(description="정답/오답에 대한 해설 및 피드백")

# [LLM Output] 전체 채점 결과 리스트
class GradeResultList(BaseModel):
    results: List[SingleGradeResult]

# [Response] 최종 클라이언트 응답
class GradeResponse(BaseModel):
    attempt_id: int
    score: int
    results: List[SingleGradeResult]

# [Response] 오답 노트 응답
class WrongAnswerItem(BaseModel):
    quiz_id: int
    question: str
    type: str
    options: List[str]
    correct_answer: str
    explanation: str
    user_answer: str          # 내가 틀린 답
    attempt_id: int           # 어느 시험에서 틀렸는지

# [Request] 오답 재시험 생성 요청
class RetryQuizRequest(BaseModel):
    quiz_ids: List[int] = Field(description="틀린 문제 ID 리스트")

# [Response] 오답 재시험 생성 응답
class RetryQuizResponse(BaseModel):
    quiz_set_ids: List[int] = Field(description="생성된 퀴즈 세트 ID 리스트 (각 문제가 원본 PDF에 연결)")
    total_questions: int
    quizzes: List[QuizItem]