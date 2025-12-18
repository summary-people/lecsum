import streamlit as st
from services.api_client import APIClient
from utils.ui_components import render_header, render_grade_result

# 1. 페이지 설정 및 초기화
st.set_page_config(page_title="AI 모의고사", page_icon="📝", layout="wide")
api_client = APIClient()

def init_session_state():
    """세션 상태 초기화 함수"""
    if "selected_pdf_id" not in st.session_state:
        st.session_state.selected_pdf_id = None
    if "current_quiz" not in st.session_state:
        st.session_state.current_quiz = None
    if "grade_result" not in st.session_state:
        st.session_state.grade_result = None

init_session_state()

# UI: 헤더
render_header("📝 AI 모의고사", "강의 자료를 분석하여 맞춤형 문제를 생성합니다.")

# 2. 사이드바: 설정 및 정보
with st.sidebar:
    st.header("⚙️ 설정")
    with st.container(border=True):
        pdf_id = st.number_input(
            "📄 분석할 PDF ID", 
            min_value=1, 
            value=st.session_state.selected_pdf_id or 1, 
            step=1
        )
        if st.button("문서 확정", use_container_width=True, type="primary"):
            st.session_state.selected_pdf_id = pdf_id
            st.session_state.current_quiz = None
            st.session_state.grade_result = None
            st.toast(f"{pdf_id}번 문서가 로드되었습니다!", icon="✅")

    if st.session_state.selected_pdf_id:
        st.info(f"현재 선택된 문서: **{st.session_state.selected_pdf_id}번**")

# 3. 메인 화면 로직
if not st.session_state.selected_pdf_id:
    st.warning("👈 먼저 사이드바에서 PDF ID를 입력하고 '문서 확정'을 눌러주세요.")
else:
    # --- 퀴즈 생성 섹션 ---
    step_col1, step_col2 = st.columns([1, 1])
    
    with st.container(border=True):
        st.subheader("🚀 문제 생성")
        st.write("선택한 문서의 핵심 내용을 바탕으로 AI가 문제를 출제합니다.")
        
        if st.button("✨ 새로운 퀴즈 세트 생성", use_container_width=True):
            with st.spinner("AI가 문서를 읽고 문제를 구성하는 중입니다..."):
                try:
                    response = api_client.generate_quiz(st.session_state.selected_pdf_id)
                    st.session_state.current_quiz = response.get("data")
                    st.session_state.grade_result = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 퀴즈 생성 중 오류가 발생했습니다: {e}")

    # --- 퀴즈 풀이 섹션 ---
    if st.session_state.current_quiz:
        quiz_data = st.session_state.current_quiz
        st.divider()
        st.subheader(f"📝 퀴즈 세트: #{quiz_data['quiz_set_id']}")

        # st.form을 사용하여 입력 시마다 새로고침 방지
        with st.form(key="quiz_form"):
            user_answers = []
            
            for i, q in enumerate(quiz_data["quizzes"]):
                with st.container(border=True):
                    # 문제 헤더 (유형 표시)
                    type_label = "객관식" if q['type'] == "multiple_choice" else "OX 문제" if q['type'] == "true_false" else "주관식"
                    st.markdown(f"**Q{i+1}. {q['question']}**")
                    st.caption(f"유형: {type_label}")

                    # 입력 방식 분기
                    if q["type"] in ["multiple_choice", "true_false"]:
                        ans = st.radio("정답을 선택하세요", q["options"], key=f"ans_{q['id']}", index=None)
                    else:
                        ans = st.text_input("답안을 입력하세요", key=f"ans_{q['id']}", placeholder="내용을 작성해주세요.")
                    
                    user_answers.append(ans)
            
            submit_button = st.form_submit_button("✅ 채점 제출하기", use_container_width=True, type="primary")

        # --- 채점 로직 ---
        if submit_button:
            if None in user_answers or "" in user_answers:
                st.warning("⚠️ 모든 문제에 답해주세요!")
            else:
                with st.spinner("AI가 정답을 확인하고 피드백을 생성 중입니다..."):
                    try:
                        res = api_client.grade_quiz(
                            quiz_set_id=quiz_data['quiz_set_id'],
                            quiz_ids=[q["id"] for q in quiz_data["quizzes"]],
                            user_answers=user_answers
                        )
                        st.session_state.grade_result = res.get("data")
                    except Exception as e:
                        st.error(f"❌ 채점 중 오류가 발생했습니다: {e}")

    # --- 결과 표시 섹션 ---
    if st.session_state.grade_result:
        st.divider()
        render_grade_result(st.session_state.grade_result)