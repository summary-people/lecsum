# 업로드 문서 DB 모델
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

# PDF 파일 정보
class PdfFile(Base):
    __tablename__ = "pdf_files"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    keywords = Column(Text)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # PDF 1 : N QuizSet
    quiz_sets = relationship(
        "QuizSet",
        back_populates="pdf",
        cascade="all, delete-orphan"
    )