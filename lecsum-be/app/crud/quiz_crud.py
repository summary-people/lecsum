from sqlalchemy.orm import Session
from app.models import quiz
from app.db.quiz_schemas import *

# 퀴즈 세트(시험지) 생성
def create_quiz_set(db: Session, pdf_id: int):
    db_quiz_set = quiz.QuizSet(pdf_id=pdf_id)
    db.add(db_quiz_set)
    db.commit()
    db.refresh(db_quiz_set)
    return db_quiz_set

# 문제들 저장
def create_quiz_list(db: Session, quiz_set_id: int, quizzes: list[QuizItem]):
    db_quizzes = []
    
    for index, q in enumerate(quizzes):
        db_quiz = quiz.Quiz(
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

def get_quizzes_by_ids(db: Session, quiz_ids: List[int]) -> List[quiz.Quiz]:
    return db.query(quiz.Quiz).filter(quiz.Quiz.id.in_(quiz_ids)).all()

# 응시 기록(Attempt) 생성
def create_attempt(db: Session, quiz_set_id: int) -> quiz.Attempt:
    
    attempt = quiz.Attempt(
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
        quiz.QuizResult(
            attempt_id=attempt_id,
            quiz_id=item['quiz_id'],
            user_answer=item['user_answer'],
            is_correct=item['is_correct']
        ) for item in grade_data
    ]
    db.add_all(results)

# 최종 점수 업데이트
def update_attempt_score(db: Session, attempt_id: int, total_count: int, correct_count: int, score: int):
    attempt = db.query(quiz.Attempt).filter(quiz.Attempt.id == attempt_id).first()
    if attempt:
        attempt.quiz_count = total_count
        attempt.correct_count = correct_count
        attempt.score = score
