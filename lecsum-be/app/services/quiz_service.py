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
    # [MySQL] pdf_id로 PDF 정보(UUID) 조회
    pdf = file_crud.get_pdf_by_id(db, request.pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF를 찾을 수 없습니다.")
    
    # UUID 추출 (VectorDB 검색용)
    file_uuid = pdf.uuid 

    # [VectorDB] 관련 문서 검색
    # file_id 필터에 찾아낸 UUID를 넣습니다.
    retriever = vector_service.get_retriever(file_uuid)
    context_text = await vector_service.get_relevant_documents(retriever, "핵심 내용")

    if not context_text:
        raise HTTPException(status_code=400, detail="관련된 내용을 찾을 수 없어 퀴즈를 생성할 수 없습니다.")
    
    # 최근 생성된 퀴즈 20개 조회
    recent_questions = quiz_crud.get_recent_quiz_questions(db, request.pdf_id, limit=20)
    
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
    quiz_set = quiz_crud.create_quiz_set(db, pdf.id)
    
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

def get_quiz_sets(db: Session, pdf_id: int):
    quiz_sets = quiz_crud.get_quiz_sets_by_pdf(db, pdf_id)
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
    for result, quiz_obj in results:

        items.append(WrongAnswerItem(
            quiz_id=quiz_obj.id,
            question=quiz_obj.question,
            type=quiz_obj.type,
            options=quiz_obj.options or [],
            correct_answer=quiz_obj.correct_answer,
            explanation=quiz_obj.explanation,
            user_answer=result.user_answer,
            attempt_id=result.attempt_id,
            created_at=result.created_at
        ))

    return items

async def create_retry_quiz(db: Session, request: RetryQuizRequest) -> RetryQuizResponse:
    """
    틀린 문제 기반 재시험 생성
    각 틀린 문제당 유사한 문제 3개씩 생성
    각 문제는 원본 PDF에 개별적으로 연결됨
    """
    # 틀린 문제들 조회
    quizzes = quiz_crud.get_quizzes_by_ids(db, request.quiz_ids)

    if not quizzes:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")

    # 전체 생성된 문제 및 QuizSet ID 리스트
    all_saved_quizzes = []
    quiz_set_ids = []

    # 각 틀린 문제마다 처리
    for original_quiz in quizzes:
        # 각 문제의 원본 PDF ID 조회
        quiz_set = db.query(quiz_crud.QuizSet).filter(
            quiz_crud.QuizSet.id == original_quiz.quiz_set_id
        ).first()

        if not quiz_set:
            raise HTTPException(
                status_code=404,
                detail=f"문제 세트를 찾을 수 없습니다. (quiz_id={original_quiz.id})"
            )

        # 해당 PDF에 대한 새 QuizSet 생성
        new_quiz_set = quiz_crud.create_quiz_set(db, quiz_set.pdf_id)
        quiz_set_ids.append(new_quiz_set.id)

        # 원본 문제 정보를 문자열로 포맷팅
        original_quiz_info = f"""
문제 유형: {original_quiz.type}
질문: {original_quiz.question}
보기: {original_quiz.options if original_quiz.options else "없음"}
정답: {original_quiz.correct_answer}
해설: {original_quiz.explanation}
        """

        # LLM 호출하여 유사 문제 3개 생성
        retry_result: QuizResponse = await retry_quiz_chain.ainvoke({
            "original_quiz": original_quiz_info
        })

        # 생성된 문제가 3개가 아니면 에러
        if len(retry_result.quizzes) != 3:
            raise HTTPException(
                status_code=500,
                detail=f"문제 생성 오류: {len(retry_result.quizzes)}개 생성됨 (예상: 3개)"
            )

        # 생성된 문제들을 해당 QuizSet에 저장
        saved_quizzes = quiz_crud.create_quiz_list(db, new_quiz_set.id, retry_result.quizzes)
        all_saved_quizzes.extend(saved_quizzes)

    # 응답 구성
    response_items = []
    for q in all_saved_quizzes:
        response_items.append(QuizItem(
            id=q.id,
            question=q.question,
            type=q.type,
            options=q.options if q.options else [],
            correct_answer=q.correct_answer,
            explanation=q.explanation
        ))

    return RetryQuizResponse(
        quiz_set_ids=quiz_set_ids,  # 여러 QuizSet ID 반환
        total_questions=len(response_items),
        quizzes=response_items
    )

# 응시기록 조회
def get_quiz_set_attempt_history(db: Session, quiz_set_id: int):
    attempts = quiz_crud.get_attempts_by_quiz_set(db, quiz_set_id)
    if not attempts:
         return []
    return attempts