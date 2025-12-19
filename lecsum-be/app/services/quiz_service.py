# 문제 생성, 채점, 해설 생성 로직
import asyncio
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud import quiz_crud, file_crud
from app.db.quiz_schemas import *
from app.services import vector_service
from app.core.llm_client import quiz_critic_refiner_chain , grade_chain, enrich_chain, retry_quiz_chain
from app.core.searches import search_and_format_run


async def generate_and_save_quiz(db: Session, request: QuizRequest) -> QuizResponse:
    # [MySQL] document_id로 PDF 정보(UUID) 조회
    document = file_crud.get_document_by_id(db, request.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document를 찾을 수 없습니다.")
    
    # UUID 추출 (VectorDB 검색용)
    file_uuid = document.uuid 

    # [VectorDB] 관련 문서 검색
    # file_id 필터에 찾아낸 UUID를 넣습니다.
    retriever = vector_service.get_retriever(file_uuid)
    context_text = await vector_service.get_relevant_documents(retriever, "핵심 내용")

    if not context_text:
        raise HTTPException(status_code=400, detail="관련된 내용을 찾을 수 없어 퀴즈를 생성할 수 없습니다.")
    
    # 최근 생성된 퀴즈 20개 조회
    recent_questions = quiz_crud.get_recent_quiz_questions(db, request.document_id, limit=20)
    
    # 프롬프트용 문자열로 포맷팅
    if not recent_questions:
        recent_quizzes_str = "없음 (이 PDF에서 생성되는 첫 퀴즈입니다.)"
    else:
        # 리스트를 줄바꿈 문자열로 변환
        recent_quizzes_str = "\n".join([f"- {q}" for q in recent_questions])

    # [LLM] 퀴즈 생성
    # result는 QuizResponse Pydantic 객체 (quizzes=[QuizItem, ...])
    result = quiz_critic_refiner_chain.invoke({
        "context": context_text,
        "recent_quizzes": recent_quizzes_str
    })

    for quiz in result.quizzes:
        if quiz.type == "true_false":
            # options가 비어있거나 없으면 강제로 설정
            if not quiz.options:
                quiz.options = ["O", "X"]

    
    # [MySQL] 생성된 퀴즈 저장
    # 퀴즈 세트 생성
    quiz_set = quiz_crud.create_quiz_set(db, document.id)
    
    # 개별 문제 저장
    saved_quizzes = quiz_crud.create_quiz_list(db, quiz_set.id, result.quizzes)

    # 저장된 데이터로 Response 구성하여 반환
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

    # 3. 채점 및 해설 보강 LLM 호출
    llm_result: GradeResultList = await grade_and_enrich_pipeline(
        formatted_block,
        ordered_quizzes,
        request.user_answer_list
    )

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

async def grade_retry_quiz_set(db: Session, request) -> GradeResponse:
    """
    재시험 채점 (retry_quiz_set_id 사용)
    기존 채점 로직과 동일하지만 Attempt 생성 시 retry_quiz_set_id를 사용
    """
    # 1. 퀴즈 데이터 조회
    quizzes = quiz_crud.get_quizzes_by_ids(db, request.quiz_id_list)

    # 퀴즈 ID 순서대로 정렬
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

    # 3. 채점 및 해설 보강 LLM 호출
    llm_result: GradeResultList = await grade_and_enrich_pipeline(
        formatted_block,
        ordered_quizzes,
        request.user_answer_list
    )

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

    # 5. DB 트랜잭션 처리 (재시험용 Attempt 생성)
    try:
        # 재시험 Attempt 생성
        attempt = quiz_crud.create_retry_attempt(db, request.retry_quiz_set_id)

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
    


async def run_enrichment_task(quiz, user_ans, original_feedback):
    """개별 오답에 대해 검색을 수행하고 해설을 생성하는 비동기 태스크"""
    formatted_search = "" # 초기값 빈 문자열
    
    # Google Search (비동기 호출)
    try:
        search_query = f"{quiz.question} 개념 및 예시"
        formatted_search = await asyncio.wait_for(
            search_and_format_run(search_query), 
            timeout=7.0  # 7초 초과 시 TimeoutError 발생
        )
    except asyncio.TimeoutError:
        print(f"⌛ Search Timeout for quiz {quiz.id}: 검색 시간이 너무 오래 걸려 건너뜁니다.")
        formatted_search = ""
    except Exception as e:
        print(f"⚠️ Search Failed for quiz {quiz.id}: {e}")
        # 검색 실패 시 빈 값 유지
        formatted_search = ""

    # Enrichment Chain 실행
    try:
        enriched_text = await enrich_chain.ainvoke({
            "question": quiz.question,
            "user_answer": user_ans,
            "correct_answer": quiz.correct_answer,
            "explanation": quiz.explanation,
            "search_results": formatted_search
        })
        return enriched_text
        
    except Exception as e:
        print(f"⚠️ Enrichment Chain Failed for quiz {quiz.id}: {e}")
        # LLM 자체가 실패 시
        return f"아쉽네요! 정답은 **{quiz.correct_answer}**입니다.\n\n**📘 강의 포인트**\n{quiz.explanation}"

async def grade_and_enrich_pipeline(formatted_block: str, quizzes: list, user_answers: list) -> GradeResultList:
    """
    [MultiChain Pipeline]
    1. Grade Chain 실행 (일괄 채점)
    2. 오답 필터링 (Router)
    3. Enrichment Chain 병렬 실행 (Parallel Execution)
    4. 결과 병합 (Merge)
    """
    
    # Step 1: 1차 채점 (Batch Grading)
    print("running grading chain...")
    grading_result: GradeResultList = await grade_chain.ainvoke({"formatted_quiz_block": formatted_block})

    # 결과 개수 검증
    if len(grading_result.results) != len(quizzes):
        raise ValueError("채점 결과의 개수가 문제 개수와 일치하지 않습니다.")

    # Step 2: 오답에 대한 보강 작업 준비
    enrich_tasks = []
    target_indices = []

    for i, result in enumerate(grading_result.results):
        if not result.is_correct: # 오답 -> Enrichment 대상
            target_indices.append(i)
            quiz = quizzes[i]
            user_ans = user_answers[i]
            
            # 태스크 예약
            enrich_tasks.append(
                run_enrichment_task(quiz, user_ans, result.feedback)
            )

    # Step 3: 병렬 실행 (RAG Enrichment)
    if enrich_tasks:
        print(f"⚠️ {len(enrich_tasks)}개의 오답에 대해 심화 해설 생성 중...")
        enriched_feedbacks = await asyncio.gather(*enrich_tasks)
        
        # 결과 덮어쓰기
        for idx, new_feedback in zip(target_indices, enriched_feedbacks):
            grading_result.results[idx].feedback = new_feedback
            
    return grading_result

def get_quiz_sets(db: Session, document_id: int):
    quiz_sets = quiz_crud.get_quiz_sets_by_document(db, document_id)
    if not quiz_sets:
         return []
         
    return quiz_sets

def remove_quiz_sets(db: Session, quiz_set_id: int):
    is_deleted = quiz_crud.remove_quiz_set(db, quiz_set_id)
    
    if not is_deleted:        
        raise HTTPException(
            status_code=404, 
            detail="해당 퀴즈 세트를 찾을 수 없습니다."
        )
    return None
def get_wrong_answer_list(db: Session, limit: int, offset: int):
    """
    오답 노트 목록 반환
    """
    results = quiz_crud.get_wrong_answers(db, limit, offset)

    # 틀린 문제가 없는 경우 예외 처리
    if not results:
        raise HTTPException(
            status_code=404,
            detail="틀린 문제가 없습니다. 모든 문제를 정답으로 맞추셨습니다!"
        )

    items = []
    for result, quiz_obj, document_obj in results:

        items.append(WrongAnswerItem(
            quiz_id=quiz_obj.id,
            question=quiz_obj.question,
            type=quiz_obj.type,
            options=quiz_obj.options or [],
            correct_answer=quiz_obj.correct_answer,
            explanation=quiz_obj.explanation,
            user_answer=result.user_answer,
            attempt_id=result.attempt_id,
            pdf_name=pdf_obj.name if pdf_obj else None
        ))

    return items

async def create_retry_quiz(db: Session, request: RetryQuizRequest) -> RetryQuizResponse:
    """
    선택한 틀린 문제들로 재시험 생성
    1. quiz_ids로 문제들 조회
    2. 각 문제당 유사한 문제 3개씩 LLM 생성
    3. 생성된 문제들을 새 QuizSet에 저장

    예시: 선택한 문제 2개 → 총 6개 재시험 문제 생성
    """
    # 1. 선택한 문제들 조회
    selected_quizzes = quiz_crud.get_quizzes_by_ids(db, request.quiz_ids)

    if not selected_quizzes:
        raise HTTPException(status_code=404, detail="선택한 문제를 찾을 수 없습니다.")

    if len(selected_quizzes) != len(request.quiz_ids):
        raise HTTPException(status_code=404, detail="일부 문제를 찾을 수 없습니다.")

    # 2. 원본 QuizSet의 PDF ID 찾기 (첫 번째 문제 기준)
    first_quiz = selected_quizzes[0]
    original_quiz_set = db.query(quiz_crud.QuizSet).filter(
        quiz_crud.QuizSet.id == first_quiz.quiz_set_id
    ).first()

    if not original_quiz_set:
        raise HTTPException(status_code=404, detail="원본 퀴즈 세트를 찾을 수 없습니다.")

    # 3. 각 선택한 문제당 유사 문제 3개씩 생성
    all_generated_quizzes = []

    for original_quiz in selected_quizzes:
        # 원본 문제 정보를 문자열로 포맷팅
        original_quiz_info = f"""
문제 유형: {original_quiz.type}
질문: {original_quiz.question}
보기: {original_quiz.options if original_quiz.options else "없음"}
정답: {original_quiz.correct_answer}
해설: {original_quiz.explanation}
        """

        # LLM 호출하여 유사 문제 3개 생성
        retry_result: QuizGenerationOutput = await retry_quiz_chain.ainvoke({
            "original_quiz": original_quiz_info
        })

        # 생성된 문제가 3개가 아니면 경고 (하지만 계속 진행)
        if len(retry_result.quizzes) != 3:
            print(f"⚠️ 경고: {len(retry_result.quizzes)}개 생성됨 (예상: 3개)")

        # 생성된 문제들을 리스트에 추가
        all_generated_quizzes.extend(retry_result.quizzes)

    # 5. 새로운 QuizSet 생성 (재시험용)
    new_quiz_set = quiz_crud.create_quiz_set(db, original_quiz_set.document_id)

    # 생성된 문제들 저장
    saved_quizzes = quiz_crud.create_quiz_list(db, new_quiz_set.id, all_generated_quizzes)

    # 6. RetryQuizSet 생성 및 연결
    from app.models.quiz import RetryQuizSet, RetryQuizItem

    retry_quiz_set = RetryQuizSet(
        quiz_set_id=new_quiz_set.id  # 생성된 QuizSet 연결
    )
    db.add(retry_quiz_set)
    db.flush()  # ID 생성

    # 7. RetryQuizItem으로 원본 Quiz와 생성된 Quiz 연결 정보 저장
    retry_items = []
    saved_quiz_idx = 0

    for original_quiz in selected_quizzes:
        # 이 원본 문제에서 생성된 3개 문제
        for _ in range(3):
            if saved_quiz_idx < len(saved_quizzes):
                retry_item = RetryQuizItem(
                    retry_quiz_set_id=retry_quiz_set.id,
                    original_quiz_id=original_quiz.id,  # 원본 문제 참조
                    order=saved_quiz_idx + 1
                )
                retry_items.append(retry_item)
                saved_quiz_idx += 1

    db.add_all(retry_items)
    db.commit()
    db.refresh(retry_quiz_set)

    # 8. 응답 구성 (생성된 Quiz 정보 반환)
    response_items = []
    for q in saved_quizzes:
        response_items.append(QuizItem(
            id=q.id,
            question=q.question,
            type=q.type,
            options=q.options if q.options else [],
            correct_answer=q.correct_answer,
            explanation=q.explanation
        ))

    return RetryQuizResponse(
        retry_quiz_set_id=retry_quiz_set.id,
        total_questions=len(response_items),
        quizzes=response_items
    )

def get_attempt_list(db: Session, quiz_set_id: int = None, limit: int = 50, offset: int = 0):
    """
    응시 기록 목록 조회
    quiz_set_id가 주어지면 해당 퀴즈 세트의 응시 기록만 조회
    없으면 전체 응시 기록 조회
    """
    attempts = quiz_crud.get_attempts(db, quiz_set_id, limit, offset)

    if not attempts:
        return []

    return [AttemptDto.model_validate(attempt) for attempt in attempts]

def get_attempt_detail(db: Session, attempt_id: int):
    """
    응시 기록 상세 조회 (문제별 결과 포함)
    """
    attempt = quiz_crud.get_attempt_by_id(db, attempt_id)

    if not attempt:
        raise HTTPException(status_code=404, detail="응시 기록을 찾을 수 없습니다.")

    # QuizResult와 Quiz 정보를 함께 조회
    results_with_quiz = quiz_crud.get_quiz_results_with_quiz(db, attempt_id)

    # QuizResultDto로 변환
    result_dtos = []
    for result, quiz in results_with_quiz:
        result_dtos.append(QuizResultDto(
            id=result.id,
            quiz_id=result.quiz_id,
            user_answer=result.user_answer,
            is_correct=result.is_correct,
            question=quiz.question,
            correct_answer=quiz.correct_answer
        ))

    return AttemptDetailDto(
        id=attempt.id,
        quiz_set_id=attempt.quiz_set_id,
        retry_quiz_set_id=attempt.retry_quiz_set_id,
        score=attempt.score,
        quiz_count=attempt.quiz_count,
        correct_count=attempt.correct_count,
        created_at=attempt.created_at,
        results=result_dtos
    )
