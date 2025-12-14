# Pydantic 스키마
from pydantic import BaseModel
from typing import Optional, Generic, TypeVar

T = TypeVar('T')

# 응답 통일
class CommonResponse(BaseModel, Generic[T]):
    status: bool = True
    message: str = "요청이 성공적으로 처리되었습니다."
    data: Optional[T] = None