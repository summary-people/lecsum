# 생성된 퀴즈 목록
import streamlit as st
from services.api_client import APIClient

# API 클라이언트 초기화
api_client = APIClient()

st.title("🗄️ 퀴즈 보관함")
st.markdown("이전에 생성된 퀴즈 목록을 확인하고 관리합니다.")

# 세션 상태 확인 (다른 페이지와 공유)
if "selected_pdf_id" not in st.session_state:
    st.session_state.selected_pdf_id = None

# 사이드바: PDF 선택 (보관함 조회용)
with st.sidebar:
    st.header("📄 문서 설정")
    pdf_id = st.number_input("조회할 PDF ID", min_value=1, value=st.session_state.selected_pdf_id or 1, step=1)
    
    if st.button("문서 선택"):
        st.session_state.selected_pdf_id = pdf_id
        st.success(f"{pdf_id}번 문서의 기록을 불러옵니다.")

# 메인 로직: 보관함 목록 표시
if not st.session_state.selected_pdf_id:
    st.warning("⚠️ 왼쪽 사이드바에서 문서를 먼저 선택해주세요.")
else:
    st.subheader(f"📌 PDF ID: {st.session_state.selected_pdf_id}의 저장된 기록")
    
    try:
        with st.spinner("목록을 불러오는 중..."):
            response = api_client.get_quiz_sets(st.session_state.selected_pdf_id)
            quiz_sets = response.get("data", [])
            
            if not quiz_sets:
                st.info("저장된 퀴즈 세트가 없습니다.")
            else:
                for qs in quiz_sets:
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"""
                            **퀴즈 ID:** {qs['id']}  
                            - 📅 생성일: {qs['created_at']}  
                            - 📝 문제 수: {len(qs['quizs'])}개
                            
                            {qs['quizs']}
                            """)
                        with col2:
                            # 삭제 시 고유 키 부여 (del_id)
                            if st.button("🗑️ 삭제", key=f"del_{qs['id']}", use_container_width=True):
                                if api_client.delete_quiz_set(qs['id']):
                                    st.success(f"ID {qs['id']} 삭제 완료")
                                    st.rerun()
                        st.divider()
                        
    except Exception as e:
        st.error(f"❌ 목록 호출 중 오류 발생: {str(e)}")