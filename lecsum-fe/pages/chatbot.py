import streamlit as st
from services.api_client import APIClient

def render_chatbot_page():
    # API 클라이언트 초기화
    api_client = APIClient()

    if "selected_document_id" not in st.session_state:
        st.session_state.selected_document_id = None
    if "selected_document_name" not in st.session_state:
        st.session_state.selected_document_name = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.title("📚 공부 챗봇")
    st.markdown("업로드한 강의 자료를 바탕으로 질문하고 답변을 받아보세요!")

    # 문서 선택 (메인 화면)
    st.subheader("📄 문서 선택")

    try:
        response = api_client.get_documents(limit=50, offset=0)
        documents = response.get("data", [])
    except Exception:
        documents = []

    if not documents:
        st.warning("업로드된 문서가 없습니다. 먼저 문서를 업로드해주세요.")
        return

    # 문서 이름 -> ID 매핑
    doc_options = {doc["name"]: doc["id"] for doc in documents}

    selected_name = st.selectbox(
        "요약/질문할 문서를 선택하세요",
        list(doc_options.keys())
    )

    selected_id = doc_options[selected_name]

    if st.session_state.selected_document_id != selected_id:
        st.session_state.selected_document_id = selected_id
        st.session_state.selected_document_name = selected_name
        st.session_state.chat_history = []

    st.info(f"선택된 문서: {selected_name}")

    # 추천 자료 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 추천 자료 보기", key="recommend_btn"):
            with st.spinner("추천 자료를 찾는 중..."):
                try:
                    response = api_client.recommend_resources(st.session_state.selected_document_id)
                    rec_data = response.get("data", {})
                    
                    st.subheader("📚 추천 자료")
                    
                    # 추천 이유 요약 표시
                    if rec_data.get("summary"):
                        st.markdown(f"**추천 이유:** {rec_data['summary']}")
                    
                    # 추천 자료 목록 표시
                    if rec_data.get("recommendations"):
                        for idx, item in enumerate(rec_data["recommendations"], 1):
                            with st.expander(f"{idx}. {item.get('title', '제목 없음')}"):
                                st.write(f"**유형:** {item.get('type', 'N/A')}")
                                st.write(f"**설명:** {item.get('description', '')}")
                                st.markdown(f"[바로가기]({item.get('url', '#')})")
                except Exception as e:
                    st.error(f"❌ 추천 자료를 불러올 수 없습니다: {str(e)}")

    # 대화 기록 표시
    st.subheader("💬 대화")
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["question"])
        
        with st.chat_message("assistant"):
            # 추천 자료인 경우 마크다운으로 표시
            if chat.get("is_recommendation"):
                st.markdown(chat["answer"])
            else:
                st.write(chat["answer"])
    
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

if __name__ == "__main__":
    render_chatbot_page()