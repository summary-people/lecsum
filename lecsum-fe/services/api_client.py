import requests
from typing import Optional, Dict, Any, List

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    

    def chat(self, pdf_id: int, question: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """챗봇 질문하기"""
        payload = {
            "pdf_id": pdf_id,
            "question": question,
            "chat_history": chat_history or []
        }
        response = requests.post(f"{self.base_url}/api/chatbot/chat", json=payload)
        response.raise_for_status()
        return response.json()
    
    def recommend_resources(self, pdf_id: int) -> Dict[str, Any]:
        """자료 추천받기"""
        payload = {
            "pdf_id": pdf_id
        }
        response = requests.post(f"{self.base_url}/api/chatbot/recommend", json=payload)
        response.raise_for_status()
        return response.json()
    
    # Quiz
    def generate_quiz(self, pdf_id: int) -> Dict[str, Any]:
        """퀴즈 생성하기"""
        payload = {"pdf_id": pdf_id, "query": "핵심 내용"}
        response = requests.post(f"{self.base_url}/api/quizzes/generate", json=payload)
        response.raise_for_status()
        return response.json()

    def grade_quiz(self, quiz_set_id: int, quiz_ids: List[int], user_answers: List[str]) -> Dict[str, Any]:
        """퀴즈 채점하기"""
        payload = {
            "quiz_set_id": quiz_set_id,
            "quiz_id_list": quiz_ids,
            "user_answer_list": user_answers
        }
        response = requests.post(f"{self.base_url}/api/quizzes/grade", json=payload)
        response.raise_for_status()
        return response.json()

    def get_quiz_sets(self, pdf_id: int) -> Dict[str, Any]:
        """퀴즈 목록 불러오기"""
        params = {"pdf_id": pdf_id}
        response = requests.get(f"{self.base_url}/api/quizzes/quiz-sets", params=params)
        response.raise_for_status()
        return response.json()

    def delete_quiz_set(self, quiz_set_id: int) -> bool:
        """퀴즈 세트 삭제"""
        response = requests.delete(f"{self.base_url}/api/quizzes/quiz-sets/{quiz_set_id}")
        return response.status_code == 200
    
    def get_quiz_attempts(self, quiz_set_id: int) -> Dict[str, Any]:
        """특정 퀴즈 세트의 응시 기록 목록 조회"""
        response = requests.get(f"{self.base_url}/api/quizzes/quiz-sets/{quiz_set_id}/attempts")
        response.raise_for_status()
        return response.json()