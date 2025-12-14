# 문제 생성, 채점, 해설 생성 로직
from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import quiz_crud, file_crud
from db.quiz_schemas import *
from services import vector_service
from core.llm_client import final_reflection_chain , grade_chain

async def generate_and_save_quiz(db: Session, request: QuizRequest) -> QuizResponse:
    # 1. [MySQL] pdf_id로 PDF 정보(UUID) 조회
    pdf = file_crud.get_pdf_by_id(db, request.pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF를 찾을 수 없습니다.")
    
    # UUID 추출 (VectorDB 검색용)
    file_uuid = pdf.uuid 

    # 2. [VectorDB] 관련 문서 검색
    # file_id 필터에 찾아낸 UUID를 넣습니다.
    retriever = vector_service.get_retriever(file_uuid)
    context_text = await vector_service.get_relevant_documents(retriever, request.query)

    if not context_text:
        raise HTTPException(status_code=400, detail="관련된 내용을 찾을 수 없어 퀴즈를 생성할 수 없습니다.")

    # 3. [LLM] 퀴즈 생성 (Invoke)
    # result는 QuizResponse Pydantic 객체 (quizzes=[QuizItem, ...])
    result = final_reflection_chain.invoke({"context": context_text})

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

async def grade_quiz_set(db: Session, request: GradeRequest) -> GradeResponse:
    # 1. 퀴즈 데이터 조회
    quizzes = quiz_crud.get_quizzes_by_ids(db, request.quiz_id_list)
    
    # 퀴즈 ID 순서대로 정렬 (DB 조회 시 순서가 보장되지 않을 수 있으므로)
    quiz_map = {q.id: q for q in quizzes}
    ordered_quizzes = []
    for q_id in request.quiz_id_list:
        if q_id not in quiz_map:
            raise HTTPException(status_code=404, detail=f"Quiz ID {q_id} not found")
        ordered_quizzes.append(quiz_map[q_id])

    # 2. LLM 입력용 문자열 포맷팅
    formatted_block = ""
    for idx, (quiz, user_ans) in enumerate(zip(ordered_quizzes, request.user_answer_list)):
        formatted_block += f"""
        [문제 {idx + 1}]
        - 유형: {quiz.type}
        - 문제: {quiz.question}
        - 실제 정답: {quiz.correct_answer}
        - 기존 해설: {quiz.explanation}
        - 사용자 답: {user_ans}
        \n"""

    # 3. LLM 호출
    chain = grade_chain
    llm_result: GradeResultList = await chain.ainvoke({"formatted_quiz_block": formatted_block})
    
    # 결과 개수 검증
    if len(llm_result.results) != len(ordered_quizzes):
        raise HTTPException(status_code=500, detail="채점 결과의 개수가 문제 개수와 일치하지 않습니다.")

    # 4. DB 저장을 위한 데이터 준비 및 계산
    correct_count = 0
    save_data_list = []
    
    for i, result in enumerate(llm_result.results):
        if result.is_correct:
            correct_count += 1
            
        save_data_list.append({
            "quiz_id": ordered_quizzes[i].id,
            "user_answer": request.user_answer_list[i],
            "is_correct": result.is_correct
        })

    total_count = len(ordered_quizzes)
    score = int((correct_count / total_count) * 100) if total_count > 0 else 0

    # 5. DB 트랜잭션 처리
    try:
        # Attempt 생성
        attempt = quiz_crud.create_attempt(db, request.quiz_set_id)
        
        # 상세 결과 저장
        quiz_crud.create_quiz_results(db, attempt.id, save_data_list)
        
        # 점수 업데이트
        quiz_crud.update_attempt_score(db, attempt.id, total_count, correct_count, score)
        
        db.commit()
        db.refresh(attempt)
        
        return GradeResponse(
            attempt_id=attempt.id,
            score=score,
            results=llm_result.results
        )
        
    except Exception as e:
        db.rollback()
        raise e