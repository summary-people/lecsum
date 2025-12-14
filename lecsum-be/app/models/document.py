# 업로드 문서 DB 모델
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


# PDF 파일 정보
class PdfFile(Base):
    __tablename__ = "pdf"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # 1:N 관계
    quiz_sets = relationship("QuizSet", back_populates="pdf")