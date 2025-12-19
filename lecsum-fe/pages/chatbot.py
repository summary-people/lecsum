import streamlit as st
from services.api_client import APIClient

# API 클라이언트 초기화
api_client = APIClient()

st.title("📚 공부 챗봇")
st.markdown("업로드한 강의 자료를 바탕으로 질문하고 답변을 받아보세요!")

# 세션 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_document_id" not in st.session_state:
    st.session_state.selected_document_id = None
if "selected_document_name" not in st.session_state:
    st.session_state.selected_document_name = None

# 사이드바: Document 선택
with st.sidebar:
    st.header("📄 문서 선택")
    
    # Document ID 입력 (임시로 직접 입력 방식)
    document_id = st.number_input("Document ID", min_value=1, value=1, step=1)
    
    if st.button("문서 선택"):
        st.session_state.selected_document_id = document_id
        st.session_state.chat_history = []
    
    if st.session_state.selected_document_id:
        st.info(f"현재 문서 ID: {st.session_state.selected_document_id}")
        
        # 관련 자료 보기 버튼
        if st.button(f"📚 document: {st.session_state.selected_document_id}번의 관련 자료 보기", use_container_width=True):
            with st.spinner("자료 검색 중..."):
                try:
                    response = api_client.recommend_resources(
                        document_id=st.session_state.selected_document_id
                    )
                    
                    data = response.get("data", {})
                    recommendations = data.get("recommendations", [])
                    summary = data.get("summary", "")
                    
                    # 채팅 히스토리에 추천 자료 추가
                    recommend_content = f"**💡 추천 이유:** {summary}\n\n"
                    if recommendations:
                        recommend_content += f"**✅ {len(recommendations)}개의 자료를 찾았습니다!**\n\n"
                        for idx, rec in enumerate(recommendations, 1):
                            recommend_content += f"**{idx}. {rec.get('title', 'N/A')}**\n"
                            recommend_content += f"- 유형: {rec.get('type', 'N/A')}\n"
                            recommend_content += f"- 링크: {rec.get('url', 'N/A')}\n"
                            recommend_content += f"- 설명: {rec.get('description', 'N/A')}\n\n"
                    else:
                        recommend_content += "관련 자료를 찾지 못했습니다."
                    
                    st.session_state.chat_history.append({
                        "question": f"document: {st.session_state.selected_document_id}번의 관련 자료 보기",
                        "answer": recommend_content,
                        "sources": [],
                        "is_recommendation": True
                    })
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")
    
    # 대화 기록 초기화
    if st.button("🗑️ 대화 기록 초기화"):
        st.session_state.chat_history = []
        st.rerun()

# 메인 영역: 채팅
if not st.session_state.selected_document_id:
    st.warning("⚠️ 왼쪽 사이드바에서 문서를 먼저 선택해주세요.")
else:
    # 대화 기록 표시
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["question"])
        
        with st.chat_message("assistant"):
            # 추천 자료인 경우 마크다운으로 표시
            if chat.get("is_recommendation"):
                st.markdown(chat["answer"])
            else:
                st.write(chat["answer"])
            
            # 출처 표시 (추천 자료가 아닌 경우만)
            if chat.get("sources") and not chat.get("is_recommendation"):
                with st.expander("📌 출처 보기"):
                    for idx, source in enumerate(chat["sources"], 1):
                        st.markdown(f"""
                        **{idx}. {source['filename']}**
                        - 페이지: {source.get('page', 'N/A')}
                        - 내용: _{source['snippet']}_
                        """)
    
    # 질문 입력
    question = st.chat_input("질문을 입력하세요...")
    
    if question:
        # 사용자 질문 표시
        with st.chat_message("user"):
            st.write(question)
        
        # API 호출 및 답변 표시
        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                try:
                    # 대화 히스토리를 LLM 메시지 포맷으로 변환
                    chat_history = []
                    for chat in st.session_state.chat_history:
                        chat_history.append({"role": "user", "content": chat["question"]})
                        chat_history.append({"role": "assistant", "content": chat["answer"]})
                    
                    response = api_client.chat(
                        document_id=st.session_state.selected_document_id,
                        question=question,
                        chat_history=chat_history
                    )
                    
                    data = response.get("data", {})
                    answer = data.get("answer", "답변을 생성할 수 없습니다.")
                    sources = data.get("sources", [])
                    
                    st.write(answer)
                    
                    # 출처 표시
                    if sources:
                        with st.expander("📌 출처 보기"):
                            for idx, source in enumerate(sources, 1):
                                st.markdown(f"""
                                **{idx}. {source['filename']}**
                                - 페이지: {source.get('page', 'N/A')}
                                - 내용: _{source['snippet']}_
                                """)
                    
                    # 대화 기록에 추가
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "sources": sources
                    })
                    
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")