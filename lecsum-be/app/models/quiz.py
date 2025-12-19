# 문제, 정답, 해설 저장 모델
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


# 퀴즈 세트 (시험지)
class QuizSet(Base):
    __tablename__ = "quiz_set"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document_files.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # N:1
    document = relationship("DocumentFile", back_populates="quiz_sets")    
    # 1:N
    quizs = relationship("Quiz", back_populates="quiz_set", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="quiz_set", cascade="all, delete-orphan")

# 개별 문제
class Quiz(Base):
    __tablename__ = "quiz"

    id = Column(Integer, primary_key=True, index=True)
    quiz_set_id = Column(Integer, ForeignKey("quiz_set.id"), nullable=False)
    
    number = Column(Integer)
    type = Column(String(50))
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=True) 
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # N:1 관계
    quiz_set = relationship("QuizSet", back_populates="quizs")
    
    # 1:N 관계
    results = relationship("QuizResult", back_populates="quiz", cascade="all, delete-orphan")

# 응시 기록
class Attempt(Base):
    __tablename__ = "attempt"

    id = Column(Integer, primary_key=True, index=True)
    quiz_set_id = Column(Integer, ForeignKey("quiz_set.id"), nullable=True)  # 일반 시험용
    retry_quiz_set_id = Column(Integer, ForeignKey("retry_quiz_set.id"), nullable=True)  # 재시험용

    score = Column(Integer, default=0)
    quiz_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    # N:1 관계 - 일반 시험
    quiz_set = relationship("QuizSet", back_populates="attempts")

    # N:1 관계 - 재시험
    retry_quiz_set = relationship("RetryQuizSet", foreign_keys=[retry_quiz_set_id], back_populates="attempts")

    # 1:N 관계
    results = relationship("QuizResult", back_populates="attempt", cascade="all, delete-orphan")

    # 1:N 관계 - 이 시험에서 틀린 문제로 만든 재시험들
    retry_sets = relationship("RetryQuizSet", foreign_keys="RetryQuizSet.original_attempt_id", back_populates="original_attempt")

# 상세 답안
class QuizResult(Base):
    __tablename__ = "quiz_result"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("attempt.id"), nullable=False, index=True)

    quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable=False, index=True)

    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.now)

    # N:1 관계
    attempt = relationship("Attempt", back_populates="results")

    # N:1 관계
    quiz = relationship("Quiz", back_populates="results")

# 오답 재시험 세트
class RetryQuizSet(Base):
    __tablename__ = "retry_quiz_set"

    id = Column(Integer, primary_key=True, index=True)
    original_attempt_id = Column(Integer, ForeignKey("attempt.id"), nullable=False, index=True)
    quiz_set_id = Column(Integer, ForeignKey("quiz_set.id"), nullable=False, index=True)  # 생성된 재시험 QuizSet
    created_at = Column(DateTime, default=datetime.now)

    # N:1 관계 - 어느 시험에서 틀린 문제들인지
    original_attempt = relationship("Attempt", foreign_keys=[original_attempt_id], back_populates="retry_sets")

    # N:1 관계 - 생성된 재시험 QuizSet (PDF 정보 접근용)
    quiz_set = relationship("QuizSet", foreign_keys=[quiz_set_id])

    # 1:N 관계
    retry_items = relationship("RetryQuizItem", back_populates="retry_set", cascade="all, delete-orphan")
    attempts = relationship("Attempt", foreign_keys="Attempt.retry_quiz_set_id", back_populates="retry_quiz_set")

# 재시험에 포함된 문제 (원본 Quiz 참조)
class RetryQuizItem(Base):
    __tablename__ = "retry_quiz_item"

    id = Column(Integer, primary_key=True, index=True)
    retry_quiz_set_id = Column(Integer, ForeignKey("retry_quiz_set.id"), nullable=False, index=True)
    original_quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable=False, index=True)
    order = Column(Integer)  # 재시험에서의 순서

    # N:1 관계
    retry_set = relationship("RetryQuizSet", back_populates="retry_items")
    original_quiz = relationship("Quiz")