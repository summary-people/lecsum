from sqlalchemy.orm import Session
from models import quiz
from db.quiz_schemas import *

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
