# 모의고사 요청/응답 DTO
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime

class QuizRequest(BaseModel):
    document_id: int

# 퀴즈 하나의 구조
class QuizItem(BaseModel):
    id: Optional[int] = None
    question: str = Field(description="문제 지문")
    type: Literal["multiple_choice", "true_false", "short_answer", "fill_in_blank"] = Field(description="문제 유형")
    options: List[str] = Field(description="객관식일 경우 보기 (없으면 빈 리스트)", default=[])
    correct_answer: str = Field(description="정답")
    explanation: str = Field(description="해설")

# [New] LLM 생성 전용 출력 (quiz_set_id 제거 버전)
class QuizGenerationOutput(BaseModel):
    quizzes: List[QuizItem] = Field(description="생성된 퀴즈 리스트")

# 퀴즈 세트 구조
class QuizResponse(BaseModel):
    quiz_set_id: int
    quizzes: List[QuizItem]

    # [Request] 채점 요청
class GradeRequest(BaseModel):
    quiz_set_id: int             # 시험지 ID (Attempt 생성용)
    quiz_id_list: List[int]      # 문제 ID 리스트 (순서 중요)
    user_answer_list: List[str]  # 사용자 답안 리스트 (문제 ID 순서와 대응)

# [Request] 재시험 채점 요청
class RetryGradeRequest(BaseModel):
    retry_quiz_set_id: int       # 재시험 세트 ID (Attempt 생성용)
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

# Quiz (개별 문제) DTO
class QuizDto(BaseModel):
    id: int
    number: int
    type: Optional[str] = None
    question: str
    options: Optional[list | dict] = None  # JSON 필드 대응
    
    class Config:
        from_attributes = True # ORM 객체(SQLAlchemy)를 Pydantic 모델로 변환 허용

# QuizSet (문제지) DTO
class QuizSetDto(BaseModel):
    id: int
    document_id: int
    created_at: datetime
    quizs: List[QuizDto] = [] 

    class Config:
        from_attributes = True
# [Response] 오답 노트 응답
class WrongAnswerItem(BaseModel):
    quiz_id: int
    question: str
    type: str
    options: List[str]
    correct_answer: str
    explanation: str
    user_answer: str          # 내가 틀린 답
    attempt_id: int           # 어느 시험에서 틀렸는지 (응시 기록)
    document_name: Optional[str] = None  # 원본 PDF 파일명

# [Request] 오답 재시험 생성 요청
class RetryQuizRequest(BaseModel):
    quiz_ids: List[int] = Field(description="재시험을 생성할 틀린 문제 ID 리스트")

# [Response] 오답 재시험 생성 응답
class RetryQuizResponse(BaseModel):
    retry_quiz_set_id: int = Field(description="생성된 재시험 세트 ID")
    total_questions: int
    quizzes: List[QuizItem]


# [DTO] 재시험 세트 조회용
class RetryQuizSetDto(BaseModel):
    id: int
    original_attempt_id: int
    created_at: datetime
    quizzes: List[QuizItem]

    class Config:
        from_attributes = True


# [DTO] 응시 기록 조회용
class AttemptDto(BaseModel):
    id: int
    quiz_set_id: Optional[int] = None
    retry_quiz_set_id: Optional[int] = None
    score: int
    quiz_count: int
    correct_count: int
    created_at: datetime

    class Config:
        from_attributes = True

# [Response] 응시 기록 상세 조회 (문제 결과 포함)
class AttemptDetailDto(BaseModel):
    id: int
    quiz_set_id: Optional[int] = None
    retry_quiz_set_id: Optional[int] = None
    score: int
    quiz_count: int
    correct_count: int
    created_at: datetime
    results: List["QuizResultDto"]

    class Config:
        from_attributes = True

# [DTO] 문제별 답안 결과
class QuizResultDto(BaseModel):
    id: int
    quiz_id: int
    user_answer: Optional[str] = None
    is_correct: bool
    question: str  # Quiz 정보 포함
    correct_answer: str  # Quiz 정보 포함

    class Config:
        from_attributes = True
