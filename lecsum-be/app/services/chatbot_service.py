# 챗봇 응답, 자료 추천 로직 (VectorStore 기반, MySQL 없음)
from typing import List, Dict, Optional, Any
import os
import requests
import json
from fastapi import HTTPException

from app.db.mentor_schemas import ChatRequest, ChatResponse, RecommendRequest, RecommendResponse
from app.db.vector_store import get_vector_store
from app.core.llm_client import chatbot_llm, chatOpenAI
from app.core.prompt_templates.chatbot_prompt import (
    get_chatbot_system_prompt,
    get_recommendation_system_prompt,
    build_recommendation_prompt
)

async def chat_with_documents(request: ChatRequest) -> ChatResponse:
    """
    벡터 DB 기반 Q&A 챗봇 (MySQL 없음)
    - VectorStore에서 질문과 유사한 문서 검색 (file_id 필터 적용)
    - 대화 히스토리 포함하여 자연스러운 답변 생성
    """
    vector_store = get_vector_store()
    
    # 1. 벡터 검색 (file_id로 필터)
    vec_results = vector_store.query(request.question, top_k=5)
    
    # file_id(pdf_id) 필터링
    if request.pdf_id:
        vec_results = [d for d in vec_results if str(d.get("id", "")).startswith(str(request.pdf_id))]
    
    if not vec_results:
        raise HTTPException(
            status_code=400,
            detail="관련된 내용을 찾을 수 없습니다. 다른 질문을 시도해주세요."
        )
    
    # 2. 컨텍스트 구성
    context_parts = [
        f"[문서 {i+1}] {doc.get('title', '문서')}\n{doc.get('content', '')}"
        for i, doc in enumerate(vec_results)
    ]
    context_text = "\n\n".join(context_parts)
    
    # 3. 시스템 프롬프트 (템플릿에서 가져오기)
    system_prompt = get_chatbot_system_prompt(context_text)
    
    # 4. 대화 메시지 구성
    messages = [{"role": "system", "content": system_prompt}]
    
    # 대화 히스토리 추가 (최근 5개)
    if request.chat_history:
        messages.extend(request.chat_history[-5:])
    
    messages.append({"role": "user", "content": request.question})
    
    # 5. LLM 호출
    response = chatbot_llm.invoke(messages)
    
    return ChatResponse(
        answer=response.content,
        sources=[f"강의 자료 {i+1}번 문단" for i in range(len(vec_results))]
    )

async def recommend_resources(request: RecommendRequest) -> RecommendResponse:
    """
    벡터 DB + 웹 검색 기반 자료 추천 (MySQL 없음)
    - PDF 내용을 자동 분석하여 핵심 키워드 추출
    - 추출된 키워드로 Google Custom Search 실행
    - LLM으로 구조화된 추천 생성
    """
    vector_store = get_vector_store()
    
    # ============================================================
    # [MySQL 통합 시 추가할 코드]
    # PDF 존재 여부 검증 및 메타데이터 조회
    # ============================================================
    # from app.db.database import get_db
    # from app.db.models import PDFDocument
    # 
    # db = next(get_db())
    # pdf = db.query(PDFDocument).filter(PDFDocument.file_id == request.pdf_id).first()
    # if not pdf:
    #     raise HTTPException(status_code=404, detail="PDF 파일을 찾을 수 없습니다.")
    # ============================================================
    
    # 1. PDF 전체 내용 샘플링 (주요 키워드 추출용)
    vec_results = vector_store.query(
        query="핵심 개념 주요 내용",  # 일반적인 쿼리로 대표 문서 추출
        top_k=5, 
        file_id=request.pdf_id
    )
    
    if not vec_results:
        raise HTTPException(
            status_code=400,
            detail="강의 자료를 찾을 수 없습니다."
        )
    
    # 2. PDF 내용 요약
    context_text = "\n\n".join([
        f"{doc.get('content', '')[:500]}"
        for doc in vec_results
    ])
    
    # 3. LLM으로 핵심 키워드 추출
    keyword_prompt = f"""
다음 강의 자료에서 핵심 키워드 3-5개를 추출해주세요.
오픈소스 학습 자료를 검색할 때 사용할 키워드입니다.
쉼표로 구분하여 키워드만 간단히 나열하세요.

강의 내용:
{context_text[:2000]}

키워드 (예: 딥러닝, 신경망, RNN):
"""
    
    keyword_response = chatbot_llm.invoke([{"role": "user", "content": keyword_prompt}])
    keywords = keyword_response.content.strip()
    
    # 4. 웹 검색 (추출된 키워드 사용)
    search_results = _search_web(keywords)
    
    # 5. 프롬프트 구성
    topic_instruction = f"'{keywords}' 관련 학습 자료를 추천해주세요."
    
    web_context = ""
    if search_results:
        web_context = "\n\n[웹 검색 결과]\n" + "\n".join([
            f"- {item.get('title', '제목 없음')}\n  URL: {item.get('link', '')}\n  설명: {item.get('snippet', '')}"
            for item in search_results[:5]
        ])
    
    user_prompt = build_recommendation_prompt(context_text, web_context, topic_instruction)
    
    # 5. LLM 호출 (구조화된 출력)
    structured_llm = chatOpenAI.with_structured_output(RecommendResponse)
    result = structured_llm.invoke([
        {"role": "system", "content": get_recommendation_system_prompt()},
        {"role": "user", "content": user_prompt}
    ])
    
    return result


def _search_web(query: str) -> Optional[List[Dict[str, Any]]]:
    """
    Google Custom Search JSON API를 사용한 웹 검색
    환경변수: GOOGLE_CSE_API_KEY(또는 GOOGLE_CSE_KEY), GOOGLE_CSE_CX(또는 GOOGLE_CSE_ID)
    """
    api_key = os.getenv("GOOGLE_CSE_API_KEY") or os.getenv("GOOGLE_CSE_KEY")
    cx = os.getenv("GOOGLE_CSE_CX") or os.getenv("GOOGLE_CSE_ID")
    if not api_key or not cx:
        return None
    try:
        params = {
            "key": api_key,
            "cx": cx,
            "q": query,
            "num": 8,
            "hl": "ko"
        }
        resp = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        items = data.get("items", [])
        return [
            {
                "title": it.get("title"),
                "link": it.get("link"),
                "snippet": it.get("snippet")
            }
            for it in items
        ]
    except Exception:
        return None
