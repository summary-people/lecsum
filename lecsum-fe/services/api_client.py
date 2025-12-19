import requests
from typing import Optional, Dict, Any, List

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    

    def chat(self, document_id: int, question: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """챗봇 질문하기"""
        payload = {
            "document_id": document_id,
            "question": question,
            "chat_history": chat_history or []
        }
        response = requests.post(f"{self.base_url}/api/chatbot/chat", json=payload)
        response.raise_for_status()
        return response.json()
    
    def recommend_resources(self, document_id: int) -> Dict[str, Any]:
        """자료 추천받기"""
        payload = {
            "document_id": document_id
        }
        response = requests.post(f"{self.base_url}/api/chatbot/recommend", json=payload)
        response.raise_for_status()
        return response.json()
    
    # Quiz
    def generate_quiz(self, document_id: int) -> Dict[str, Any]:
        """퀴즈 생성하기"""
        payload = {"document_id": document_id, "query": "핵심 내용"}
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

    def get_quiz_sets(self, document_id: int) -> Dict[str, Any]:
        """퀴즈 목록 불러오기"""
        params = {"document_id": document_id}
        response = requests.get(f"{self.base_url}/api/quizzes/quiz-sets", params=params)
        response.raise_for_status()
        return response.json()

    def get_attempts(self, quiz_set_id: Optional[int] = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """응시 기록 목록 조회"""
        params = {
            "quiz_set_id": quiz_set_id,
            "limit": limit,
            "offset": offset
        }
        response = requests.get(f"{self.base_url}/api/quizzes/attempts", params=params)
        response.raise_for_status()
        return response.json()

    def get_attempt_detail(self, attempt_id: int) -> Dict[str, Any]:
        """응시 기록 상세 조회 (문제별 결과 포함)"""
        response = requests.get(f"{self.base_url}/api/quizzes/attempts/{attempt_id}")
        response.raise_for_status()
        return response.json()
