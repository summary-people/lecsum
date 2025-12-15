# 모의시험 생성 및 채점 API
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.quiz_schemas import (
    QuizRequest,
    QuizResponse,
    GradeRequest,
    GradeResponse,
    WrongAnswerItem,
)
from app.db.schemas import CommonResponse
from app.db.database import get_db
from app.services import quiz_service

router = APIRouter(
    prefix="/api/quizs",
    tags=["Quiz"],
)

# 퀴즈 생성 API
@router.post(
    "/generate",
    response_model=CommonResponse[QuizResponse],
    summary="PDF 기반 모의고사(퀴즈) 생성",
    description="""
PDF 문서를 기반으로 모의고사 문제를 자동 생성합니다.

### 처리 절차
1. PDF 식별자(pdf_id) 입력
2. VectorDB(ChromaDB)에서 관련 문서 검색 (RAG)
3. LLM을 이용해 문제 자동 생성
   - 빈칸 채우기 / 단어 맞추기 유형
   - 기본 5문제 생성
4. 생성된 퀴즈를 DB에 저장
5. 생성된 퀴즈 세트 반환

### 활용 기술
- VectorDB 검색 (RAG)
- LLM 기반 문제 생성
""",
    responses={
        200: {
            "description": "퀴즈 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "quiz_set_id": 1,
                            "questions": [
                                {
                                    "question_id": 1,
                                    "question": "머신러닝의 주요 학습 방식은 ____이다.",
                                    "answer": "지도학습",
                                }
                            ],
                        },
                        "message": None,
                    }
                }
            },
        },
        400: {
            "description": "잘못된 요청",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "message": "존재하지 않는 PDF입니다.",
                    }
                }
            },
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "message": "퀴즈 생성 중 오류가 발생했습니다.",
                    }
                }
            },
        },
    },
)
async def generate_quiz(
    request: QuizRequest,
    db: Session = Depends(get_db),
):
    """
    pdf_id를 받아 퀴즈를 생성하고 DB에 저장 후 반환합니다.
    """
    result = await quiz_service.generate_and_save_quiz(db, request)
    return CommonResponse(data=result)


# 채점 API
@router.post(
    "/grade",
    response_model=CommonResponse[GradeResponse],
    summary="모의고사 일괄 채점",
    description="""
생성된 퀴즈 세트에 대해 사용자의 답안을 받아 일괄 채점합니다.

### 처리 절차
1. 퀴즈 세트 ID 및 사용자 답안 입력
2. 정답과 비교하여 채점
3. 문제별 정답 여부 및 점수 계산
4. 채점 결과를 DB에 저장
5. 채점 결과 반환
""",
    responses={
        200: {
            "description": "채점 완료",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "quiz_set_id": 1,
                            "score": 80,
                            "results": [
                                {
                                    "question_id": 1,
                                    "correct": True,
                                },
                                {
                                    "question_id": 2,
                                    "correct": False,
                                }
                            ],
                        },
                        "message": "채점이 완료되었습니다.",
                    }
                }
            },
        },
        400: {
            "description": "잘못된 요청",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "message": "채점할 퀴즈가 존재하지 않습니다.",
                    }
                }
            },
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "message": "채점 처리 중 오류가 발생했습니다.",
                    }
                }
            },
        },
    },
)
async def grade_batch_quiz(
    request: GradeRequest,
    db: Session = Depends(get_db),
):
    """
    퀴즈 답안을 받아 일괄 채점하고 결과를 저장합니다.
    """
    result = await quiz_service.grade_quiz_set(db, request)

    return CommonResponse(
        message="채점이 완료되었습니다.",
        data=result,
    )

@router.get(
    "/wrong-answers",
    response_model=CommonResponse[List[WrongAnswerItem]],
    summary="오답노트 조회",
    description="사용자가 틀린 문제들을 모아서 반환합니다."
)
async def get_wrong_answers(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    오답만 필터링해서 반환
    """
    result = quiz_service.get_wrong_answer_list(db, limit, offset)
    return CommonResponse(data=result)