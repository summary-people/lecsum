# 챗봇 응답, 자료 추천 로직
from typing import List, Dict, Optional, Any
import os
import requests
import json
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.mentor_schemas import ChatRequest, ChatResponse, RecommendRequest, RecommendResponse
from app.db.vector_store import get_vector_store
from app.core.llm_client import chatbot_llm, chatOpenAI
from app.core.prompt_templates.chatbot_prompt import (
    get_chatbot_system_prompt,
    get_recommendation_system_prompt,
    build_recommendation_prompt
)
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from app.core.enums import ChromaDB, CHROMA_PERSIST_DIR
from app.crud import file_crud

async def chat_with_documents(request: ChatRequest, db: Session) -> ChatResponse:
    """
    벡터 DB 기반 Q&A 챗봇 (Chroma 사용)
    - Chroma에서 질문과 유사한 문서 검색 (document_uuid 필터 적용)
    - 대화 히스토리 포함하여 자연스러운 답변 생성
    """
    # Chroma 벡터 스토어 초기화
    vectorstore = Chroma(
        collection_name=ChromaDB.COLLECTION_NAME.value,
        embedding_function=OpenAIEmbeddings(
            model="text-embedding-3-small"
        ),
        persist_directory=CHROMA_PERSIST_DIR,
    )
    
    # 1. 벡터 검색 (document_id로 uuid 조회 후 필터)
    if request.document_id:
        # MySQL에서 uuid 조회
        document = file_crud.get_document_by_id(db, request.document_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail="문서를 찾을 수 없습니다."
            )
        # 특정 문서로 필터링 (UUID 사용)
        vec_results = vectorstore.similarity_search(
            request.question,
            k=5,
            filter={"document_uuid": document.uuid}
        )
    else:
        # 전체 문서 검색
        vec_results = vectorstore.similarity_search(request.question, k=5)
    
    if not vec_results:
        raise HTTPException(
            status_code=400,
            detail="관련된 내용을 찾을 수 없습니다. 다른 질문을 시도해주세요."
        )
    
    # 2. 컨텍스트 구성
    context_parts = [
        f"[문서 {i+1}] {doc.metadata.get('filename', '문서')}\n{doc.page_content}"
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
        sources=[]  # 출처 정보 제외
    )

async def recommend_resources(request: RecommendRequest, db: Session) -> RecommendResponse:
    """
    MySQL 키워드 + 웹 검색 기반 자료 추천
    - MySQL에 저장된 키워드를 사용하여 효율적으로 검색
    - Google Custom Search로 웹 자료 수집
    - LLM으로 구조화된 추천 생성
    """
    # 1. MySQL에서 문서 및 키워드 조회 (정수 ID 사용)
    document = file_crud.get_document_by_id(db, request.document_id)
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail="문서를 찾을 수 없습니다."
        )
    
    # 2. MySQL에서 저장된 키워드 사용
    keywords = document.keywords if document.keywords else "학습 자료"
    
    # 3. Chroma에서 문서 내용 샘플링 (컨텍스트용)
    vectorstore = Chroma(
        collection_name=ChromaDB.COLLECTION_NAME.value,
        embedding_function=OpenAIEmbeddings(
            model="text-embedding-3-small"
        ),
        persist_directory=CHROMA_PERSIST_DIR,
    )
    
    vec_results = vectorstore.similarity_search(
        "핵심 개념 주요 내용",
        k=3,
        filter={"document_uuid": document.uuid}
    )
    
    context_text = ""
    if vec_results:
        context_text = "\n\n".join([
            f"{doc.page_content[:500]}"
            for doc in vec_results
        ])
    else:
        # 벡터 DB에 없으면 요약본 사용
        context_text = document.summary[:2000] if document.summary else ""
    
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
    
    # 6. LLM 호출 (구조화된 출력)
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
