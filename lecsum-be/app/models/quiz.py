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
    pdf_id = Column(Integer, ForeignKey("pdf_files.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # N:1
    pdf = relationship("PdfFile", back_populates="quiz_sets")    
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
    quiz_set_id = Column(Integer, ForeignKey("quiz_set.id"), nullable=False)
    
    score = Column(Integer, default=0)
    quiz_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    # N:1 관계
    quiz_set = relationship("QuizSet", back_populates="attempts")
    
    # 1:N 관계
    results = relationship("QuizResult", back_populates="attempt", cascade="all, delete-orphan")

# 상세 답안
class QuizResult(Base):
    __tablename__ = "quiz_result"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("attempt.id"), nullable=False)
    
    quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable=False) 
    
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    # N:1 관계
    attempt = relationship("Attempt", back_populates="results")
    
    # N:1 관계
    quiz = relationship("Quiz", back_populates="results")