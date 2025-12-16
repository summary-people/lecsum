# 모의시험 생성 및 채점 API
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List


from app.db.quiz_schemas import (
    QuizRequest,
    QuizResponse,
    GradeRequest,
    GradeResponse,
    QuizSetDto,
    WrongAnswerItem,
    RetryQuizRequest,
    RetryQuizResponse,
)
from app.db.schemas import CommonResponse
from app.db.database import get_db
from app.services import quiz_service

router = APIRouter(
    prefix="/api/quizzes",
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
   - 퀴즈 생성 - 비평 - 수정 MultiChain
4. 생성된 퀴즈를 DB에 저장
5. 생성된 퀴즈 세트 반환

### 활용 기술
- VectorDB 검색 (RAG)
- LLM 기반 문제 생성
- 퀴즈 생성 - 비평 - 수정 MultiChain
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
    summary="모의고사 채점",
    description="""
생성된 퀴즈 세트에 대해 사용자의 답안을 받아 채점합니다.

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
async def grade_quiz(
    request: GradeRequest,
    db: Session = Depends(get_db),
):
    """
    퀴즈 답안을 받아 채점하고 결과를 저장합니다.
    """
    result = await quiz_service.grade_quiz_set(db, request)

    return CommonResponse(
        message="채점이 완료되었습니다.",
        data=result,
    )


@router.get(
    "/quiz-sets",
    response_model=CommonResponse[List[QuizSetDto]],
    summary="파일별 퀴즈 세트 목록 조회",
    description="""
    특정 파일(pdf_id)에 연관된 모든 퀴즈 세트(문제지) 목록을 조회합니다.

    ### 처리 내용
    1. 요청받은 `pdf_id`로 생성된 퀴즈 세트를 DB에서 조회
    2. 각 퀴즈 세트에 포함된 문제(Quiz) 정보도 함께 로딩
    3. 생성일자 기준 내림차순 정렬하여 반환

    ### 반환 데이터
    - 퀴즈 세트 ID
    - 생성 일자
    - 포함된 문제 개수 및 미리보기
    """,
    responses={
        200: {
            "description": "조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "id": 10,
                                "pdf_id": 3,
                                "created_at": "2024-05-20T14:30:00",
                                "quizs": [
                                    {"id": 101, "question": "문제 1번..."},
                                    {"id": 102, "question": "문제 2번..."}
                                ]
                            },
                            {
                                "id": 5,
                                "pdf_id": 3,
                                "created_at": "2024-05-19T09:00:00",
                                "quizs": []
                            }
                        ],
                        "message": None
                    }
                }
            }
        },
        404: {
            "description": "데이터 없음",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "message": "해당 파일에 대한 퀴즈 세트가 존재하지 않습니다."
                    }
                }
            }
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "message": "목록 조회 중 서버 오류가 발생했습니다."
                    }
                }
            }
        }
    }
)
async def get_quiz_list(pdf_id: int, db: Session = Depends(get_db)):
    """
    특정 파일에 생성된 퀴즈 세트 목록 조회
    """
    result = quiz_service.get_quiz_sets(db, pdf_id)
    
    return CommonResponse(        
        data=result
    )



@router.delete(
    "/quiz-sets/{quiz_set_id}",
    response_model=CommonResponse[None],
    summary="퀴즈 세트(문제지) 삭제",
    description="""
    특정 퀴즈 세트를 삭제합니다. 
    `Cascade` 설정에 따라 연관된 **개별 문제(Quiz)**와 **풀이 기록(Attempt)**도 함께 삭제됩니다.

    ### 주의사항
    - 삭제된 데이터는 복구할 수 없습니다.
    """,
    responses={
        200: {
            "description": "삭제 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": None,
                        "message": "퀴즈 세트 삭제가 완료되었습니다."
                    }
                }
            }
        },
        404: {
            "description": "삭제 대상 없음",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "message": "해당 ID의 퀴즈 세트를 찾을 수 없습니다."
                    }
                }
            }
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "message": "삭제 처리 중 오류가 발생했습니다."
                    }
                }
            }
        }
    }
)
async def delete_quiz_set(quiz_set_id: int, db: Session = Depends(get_db)):
    """
    특정 퀴즈 세트(문제지) 삭제
    """
    quiz_service.remove_quiz_sets(db, quiz_set_id)

    return CommonResponse(   
        message="퀴즈 세트 삭제가 완료되었습니다.",     
        data=None
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

@router.post(
    "/wrong-answers/retry",
    response_model=CommonResponse[RetryQuizResponse],
    summary="오답 재시험 생성",
    description="""
틀린 문제를 기반으로 유사한 문제들로 구성된 재시험을 생성합니다.

### 처리 절차
1. 틀린 문제 ID 리스트 입력
2. 각 문제의 핵심 개념 분석
3. LLM을 이용해 각 문제당 유사한 문제 3개 생성
4. 생성된 문제들을 새로운 퀴즈 세트로 저장
5. 재시험 반환

### 예시
- 틀린 문제 3개 선택 → 총 9개(3×3) 문제로 구성된 재시험 생성
- 틀린 문제 5개 선택 → 총 15개(5×3) 문제로 구성된 재시험 생성
"""
)
async def create_retry_quiz(
    request: RetryQuizRequest,
    db: Session = Depends(get_db)
):
    """
    틀린 문제 기반 재시험 생성
    """
    result = await quiz_service.create_retry_quiz(db, request)
    return CommonResponse(
        message="재시험이 생성되었습니다.",
        data=result
    )
