import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("틀린 문제 모아보기")
st.markdown("---")

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

# 데이터 가져오기
wrong_answers = fetch_wrong_answers(limit=100)

if not wrong_answers:
    st.info("🎉 축하합니다! 틀린 문제가 없습니다.")
    st.balloons()
else:
    st.success(f"총 **{len(wrong_answers)}개**의 틀린 문제가 있습니다.")

    # 각 틀린 문제를 expander로 표시
    for idx, item in enumerate(wrong_answers, 1):
        # 문제 제목 (질문 내용)
        question_preview = item['question'][:80] + "..." if len(item['question']) > 80 else item['question']

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

            # 재시험 생성 버튼
            st.markdown("---")
            if st.button(f"🔄 재시험 시작하기", key=f"retry_btn_{item['attempt_id']}_{idx}"):
                # attempt_id를 세션 스테이트에 저장하고 바로 생성 모드로
                st.session_state['retry_attempt_id'] = item['attempt_id']
                st.session_state['auto_create_retry'] = True
                st.success("✅ 재시험이 준비되었습니다!")
                st.info("👉 왼쪽 사이드바에서 **Retry Exam** 메뉴를 클릭하세요. 자동으로 재시험이 생성됩니다.")
                st.stop()  # 추가 렌더링 중지

            # 구분선
            if idx < len(wrong_answers):
                st.markdown("<br>", unsafe_allow_html=True)

# 페이지 하단 정보
st.markdown("---")
st.caption("💡 Tip: 문제를 클릭하면 상세 내용을 볼 수 있습니다.")
