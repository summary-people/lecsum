# 문제 생성, 채점, 해설 생성 로직
from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import quiz_crud, file_crud
from db.quiz_schemas import *
from vector_service import get_retriever, get_relevant_documents 
from core.llm_client import quiz_chain

async def generate_and_save_quiz(db: Session, request: QuizRequest) -> QuizResponse:
    # 1. [MySQL] pdf_id로 PDF 정보(UUID) 조회
    pdf = file_crud.get_pdf_by_id(db, request.pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF를 찾을 수 없습니다.")
    
    # UUID 추출 (VectorDB 검색용)
    file_uuid = pdf.uuid 

    # 2. [VectorDB] 관련 문서 검색
    # file_id 필터에 찾아낸 UUID를 넣습니다.
    retriever = get_retriever(file_uuid)
    context_text = await get_relevant_documents(retriever, request.query)

    if not context_text:
        raise HTTPException(status_code=400, detail="관련된 내용을 찾을 수 없어 퀴즈를 생성할 수 없습니다.")

    # 3. [LLM] 퀴즈 생성 (Invoke)
    # result는 QuizResponse Pydantic 객체 (quizzes=[QuizItem, ...])
    result = quiz_chain.invoke({"context": context_text})

    for quiz in result.quizzes:
        if quiz.type == "true_false":
            # options가 비어있거나 없으면 강제로 설정
            if not quiz.options:
                quiz.options = ["O", "X"]

    
    # 4. [MySQL] 생성된 퀴즈 저장
    # 4-1. 퀴즈 세트 생성
    quiz_set = quiz_crud.create_quiz_set(db, pdf.id)
    
    # 4-2. 개별 문제 저장
    saved_quizzes = quiz_crud.create_quiz_list(db, quiz_set.id, result.quizzes)

    # 5. [수정] 저장된 데이터(ID 포함)로 Response 구성하여 반환
    response_items = []
    for q in saved_quizzes:
        response_items.append(QuizItem(
            id=q.id,  # DB에서 생성된 ID 할당
            question=q.question,
            type=q.type,
            options=q.options if q.options else [], # JSON 파싱 필요할 수 있음
            correct_answer=q.correct_answer,
            explanation=q.explanation
        ))

    return QuizResponse(
        quiz_set_id=quiz_set.id,
        quizzes=response_items
    )