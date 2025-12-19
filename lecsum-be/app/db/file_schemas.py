from datetime import datetime
from pydantic import BaseModel
from typing import List

# 문서 목록 조회
class DocumentSummaryItem(BaseModel):
    id: int
    uuid: str
    name: str
    summary: str
    keywords: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

# 문서 상세 조회
class DocumentSummaryDetail(BaseModel):
    id: int
    uuid: str
    name: str
    summary: str
    keywords: List[str]
    created_at: datetime

    class Config:
        from_attributes = True