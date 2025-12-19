import streamlit as st
import requests

API_URL = "http://localhost:8000"

def render_wrong_notes_page():
    st.title("틀린 문제 모아보기")
    st.markdown("---")

    # 세션 스테이트 초기화
    if 'selected_quiz_ids' not in st.session_state:
        st.session_state['selected_quiz_ids'] = []

    # API에서 틀린 문제 조회
    @st.cache_data(ttl=60)
    def fetch_wrong_answers(limit=50, offset=0):
        """오답노트 API 호출"""
        try:
            response = requests.get(
                f"{API_URL}/api/quizzes/wrong-answers",
                params={"limit": limit, "offset": offset}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            elif response.status_code == 404:
                return []
            else:
                st.error(f"오류 발생: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"서버 연결 실패: {e}")
            return []

    def create_retry_quiz(quiz_ids):
        """재시험 생성 API 호출"""
        try:
            response = requests.post(
                f"{API_URL}/api/quizzes/wrong-answers/retry",
                json={"quiz_ids": quiz_ids}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("data")
            else:
                st.error(f"재시험 생성 실패: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            st.error(f"서버 연결 실패: {e}")
            return None

    # 데이터 가져오기
    wrong_answers = fetch_wrong_answers(limit=100)

    if not wrong_answers:
        st.info("🎉 축하합니다! 틀린 문제가 없습니다.")
        st.balloons()
    else:
        st.success(f"총 **{len(wrong_answers)}개**의 틀린 문제가 있습니다.")

        # 선택된 문제 수 표시 및 재시험 생성 버튼
        selected_count = len(st.session_state['selected_quiz_ids'])

        if selected_count > 0:
            st.info(f"📝 선택된 문제: **{selected_count}개** → 재시험 문제: **{selected_count * 3}개** 생성 예정")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 선택한 문제로 재시험 생성", type="primary", use_container_width=True):
                    with st.spinner("재시험 문제를 생성하는 중..."):
                        retry_data = create_retry_quiz(st.session_state['selected_quiz_ids'])

                        if retry_data:
                            # 생성된 재시험 데이터를 세션에 저장
                            st.session_state['current_retry_quiz'] = retry_data
                            st.session_state['retry_quiz_set_id'] = retry_data['retry_quiz_set_id']

                            # 선택 초기화
                            st.session_state['selected_quiz_ids'] = []

                            # 성공 메시지와 함께 페이지 이동 안내
                            st.success(f"✅ 재시험이 생성되었습니다! (총 {retry_data['total_questions']}문제)")
                            st.balloons()

                            # 자동으로 Retry Exam 페이지로 전환
                            st.info("🚀 잠시 후 재시험 페이지로 자동 이동합니다...")
                            import time
                            time.sleep(1.5)
                            st.switch_page("pages/retry_exam.py")

        st.markdown("---")

        # 콜백 함수 정의 - 함수는 루프 밖에 정의
        def toggle_selection(qid):
            """체크박스 상태 변경 시 호출"""
            if st.session_state[f"cb_{qid}"]:  # 체크됨
                if qid not in st.session_state['selected_quiz_ids']:
                    st.session_state['selected_quiz_ids'].append(qid)
            else:  # 체크 해제됨
                if qid in st.session_state['selected_quiz_ids']:
                    st.session_state['selected_quiz_ids'].remove(qid)

        # 각 틀린 문제를 체크박스와 함께 표시
        for idx, item in enumerate(wrong_answers, 1):
            quiz_id = item['quiz_id']

            # 문제 제목 (질문 내용)
            question_preview = item['question'][:80] + "..." if len(item['question']) > 80 else item['question']

            # 체크박스와 expander를 같은 줄에 배치
            col_checkbox, col_expander = st.columns([0.5, 9.5])

            with col_checkbox:
                # 체크박스로 문제 선택 - on_change 콜백 사용
                st.checkbox(
                    "",
                    value=quiz_id in st.session_state['selected_quiz_ids'],
                    key=f"cb_{quiz_id}",
                    label_visibility="collapsed",
                    on_change=toggle_selection,
                    args=(quiz_id,)
                )

            with col_expander:
                with st.expander(f"{question_preview}", expanded=False):
                    # PDF 출처 표시
                    if item.get('pdf_name'):
                        st.caption(f"📄 원본 PDF : {item['pdf_name']}")

                    st.markdown("---")

                    # 문제 유형 배지
                    type_labels = {
                        "multiple_choice": "객관식",
                        "true_false": "O/X",
                        "short_answer": "주관식",
                        "fill_in_blank": "빈칸 채우기"
                    }
                    quiz_type = type_labels.get(item.get('type', ''), item.get('type', ''))
                    st.markdown(f"**문제 유형**: `{quiz_type}`")

                    # 문제 내용
                    st.markdown("### 📋 문제")
                    st.write(item['question'])

                    # 객관식 보기 표시
                    if item.get('options') and len(item['options']) > 0:
                        st.markdown("**보기:**")
                        for i, option in enumerate(item['options'], 1):
                            st.write(f"{i}. {option}")

                    st.markdown("---")

                    # 답안 비교 (2열 레이아웃)
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### ❌ 내가 쓴 답")
                        st.error(item.get('user_answer', '(답안 없음)'))

                    with col2:
                        st.markdown("### ✅ 정답")
                        st.success(item['correct_answer'])

                    st.markdown("---")

                    # 해설
                    st.markdown("### 💡 해설")
                    st.info(item['explanation'])

    # 페이지 하단 정보
    st.markdown("---")
    st.caption("💡 Tip: 체크박스로 문제를 선택하고 '선택한 문제로 재시험 생성' 버튼을 클릭하세요. 각 문제당 3개씩 유사 문제가 생성됩니다.")

if __name__ == "__main__":
    render_wrong_notes_page()
