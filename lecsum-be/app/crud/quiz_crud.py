from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, desc
from app.models.quiz import *
from app.db.quiz_schemas import *

# 퀴즈 세트(시험지) 생성
def create_quiz_set(db: Session, pdf_id: int):
    db_quiz_set = QuizSet(pdf_id=pdf_id)
    db.add(db_quiz_set)
    db.commit()
    db.refresh(db_quiz_set)
    return db_quiz_set

# 문제들 저장
def create_quiz_list(db: Session, quiz_set_id: int, quizzes: list[QuizItem]):
    db_quizzes = []
    
    for index, q in enumerate(quizzes):
        db_quiz = Quiz(
            quiz_set_id=quiz_set_id,
            number=index + 1,       # 문제 번호 (1번부터 시작)
            type=q.type,
            question=q.question,    
            options=q.options,      
            correct_answer=q.correct_answer,
            explanation=q.explanation
        )
        db_quizzes.append(db_quiz)
    
    db.add_all(db_quizzes)
    db.commit()
    
    return db_quizzes

def get_quizzes_by_ids(db: Session, quiz_ids: List[int]) -> List[Quiz]:
    return db.query(Quiz).filter(Quiz.id.in_(quiz_ids)).all()

# 응시 기록(Attempt) 생성
def create_attempt(db: Session, quiz_set_id: int) -> Attempt:
    
    attempt = Attempt(
        quiz_set_id=quiz_set_id,
        score=0,
        quiz_count=0,
        correct_count=0
    )
    db.add(attempt)
    db.flush()  # ID 생성을 위해 flush
    return attempt

# 채점 결과(QuizResult) 저장
def create_quiz_results(db: Session, attempt_id: int, grade_data: List[dict]):
   
    results = [
        QuizResult(
            attempt_id=attempt_id,
            quiz_id=item['quiz_id'],
            user_answer=item['user_answer'],
            is_correct=item['is_correct']
        ) for item in grade_data
    ]
    db.add_all(results)

# 최종 점수 업데이트
def update_attempt_score(db: Session, attempt_id: int, total_count: int, correct_count: int, score: int):
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if attempt:
        attempt.quiz_count = total_count
        attempt.correct_count = correct_count
        attempt.score = score

# 최근 생성된 퀴즈 20개 반환
def get_recent_quiz_questions(db: Session, pdf_id: int, limit: int = 20) -> List[str]:
    stmt = (
        select(Quiz.question)
        .join(QuizSet, Quiz.quiz_set_id == QuizSet.id)
        .where(QuizSet.pdf_id == pdf_id)
        .order_by(desc(Quiz.id))
        .limit(limit)
    )
    
    # [question1, question2, ...] 형태의 리스트 반환
    return db.execute(stmt).scalars().all()

def get_quiz_sets_by_pdf(db: Session, pdf_id: int):
    return db.query(QuizSet)\
        .options(joinedload(QuizSet.quizs))\
        .filter(QuizSet.pdf_id == pdf_id)\
        .all()

def remove_quiz_set(db: Session, quiz_set_id: int) -> bool:
    target_set = db.query(QuizSet).filter(QuizSet.id == quiz_set_id).first()
    
    if target_set:
        db.delete(target_set)
        db.commit()
        return True # 삭제 성공
        
    return False # 삭제 대상 없음

# 틀린 문제 조회
def get_wrong_answers(db: Session, limit: int, offset: int):
    """
    is_correct = False인 QuizResult 조회 + Quiz 정보 조인
    """
    return (
        db.query(QuizResult, Quiz)
        .join(Quiz, QuizResult.quiz_id == Quiz.id)
        .filter(QuizResult.is_correct == False)
        .order_by(QuizResult.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
