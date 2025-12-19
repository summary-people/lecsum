import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

st.title("📊 재시험 기록")
st.markdown("---")

# 세션 스테이트 초기화
if 'selected_retry_attempt' not in st.session_state:
    st.session_state['selected_retry_attempt'] = None


def fetch_retry_attempts(limit=50):
    """재시험 응시 기록 조회 (retry_quiz_set_id가 있는 것만)"""
    try:
        response = requests.get(
            f"{API_URL}/api/quizzes/attempts",
            params={"limit": limit, "offset": 0}
        )
        if response.status_code == 200:
            data = response.json()
            # retry_quiz_set_id가 있는 것만 필터링
            attempts = data.get("data", [])
            return [a for a in attempts if a.get('retry_quiz_set_id')]
        else:
            st.error(f"응시 기록 조회 실패: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"서버 연결 실패: {e}")
        return []


def fetch_attempt_detail(attempt_id):
    """특정 응시 기록의 상세 정보 조회"""
    try:
        response = requests.get(f"{API_URL}/api/quizzes/attempts/{attempt_id}")
        if response.status_code == 200:
            data = response.json()
            return data.get("data")
        else:
            st.error(f"상세 정보 조회 실패: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"서버 연결 실패: {e}")
        return None


# ==================== 화면 1: 재시험 기록 목록 ====================
def show_attempt_list():
    st.info("💡 재시험을 본 기록을 확인할 수 있습니다.")

    retry_attempts = fetch_retry_attempts(limit=100)

    if not retry_attempts:
        st.warning("재시험 응시 기록이 없습니다.")
        st.markdown("""
        ### 재시험 응시 방법
        1. **틀린 문제 모아보기** 페이지로 이동
        2. 틀린 문제 클릭 후 **🔄 재시험 보러가기** 버튼 클릭
        3. **재시험** 페이지에서 재시험 생성 및 응시
        """)
        return

    st.success(f"총 **{len(retry_attempts)}개**의 재시험 기록이 있습니다.")
    st.markdown("---")

    # 재시험 기록을 카드 형태로 표시
    for idx, attempt in enumerate(retry_attempts, 1):
        # 점수에 따른 색상
        score = attempt['score']
        if score >= 80:
            score_color = "#28a745"  # 초록
            emoji = "🎉"
        elif score >= 60:
            score_color = "#17a2b8"  # 파랑
            emoji = "👍"
        else:
            score_color = "#ffc107"  # 노랑
            emoji = "💪"

        # 날짜 포맷팅
        created_at = attempt['created_at']
        if isinstance(created_at, str):
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                date_str = dt.strftime('%Y-%m-%d %H:%M')
            except:
                date_str = created_at
        else:
            date_str = str(created_at)

        # 카드 UI
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px;
                        margin-bottom: 15px; border-left: 4px solid {score_color};">
                <h3 style="color: black;">{emoji} 재시험 #{attempt['id']}</h3>
                <p style="color: gray; font-size: 14px;">📅 {date_str}</p>
                <p style="color: black;">
                    <strong>점수:</strong> <span style="color: {score_color}; font-size: 20px; font-weight: bold;">{score}점</span> |
                    <strong>정답률:</strong> {attempt['correct_count']}/{attempt['quiz_count']}문제
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.write("")  # 위치 조정
            st.write("")
            if st.button("상세보기 →", key=f"detail_{attempt['id']}", use_container_width=True):
                st.session_state['selected_retry_attempt'] = attempt['id']
                st.rerun()


# ==================== 화면 2: 재시험 상세 결과 ====================
def show_attempt_detail(attempt_id):
    detail = fetch_attempt_detail(attempt_id)

    if not detail:
        st.error("상세 정보를 불러올 수 없습니다.")
        if st.button("← 목록으로"):
            st.session_state['selected_retry_attempt'] = None
            st.rerun()
        return

    # 헤더
    score = detail['score']
    if score >= 80:
        st.success(f"### 🎉 점수: {score}점")
    elif score >= 60:
        st.info(f"### 👍 점수: {score}점")
    else:
        st.warning(f"### 💪 점수: {score}점")

    # 날짜 정보
    created_at = detail['created_at']
    if isinstance(created_at, str):
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y년 %m월 %d일 %H:%M')
        except:
            date_str = created_at
    else:
        date_str = str(created_at)

    st.caption(f"📅 응시 일시: {date_str}")
    st.caption(f"📝 정답률: {detail['correct_count']}/{detail['quiz_count']}문제")

    st.markdown("---")

    # 뒤로가기 버튼
    if st.button("← 목록으로 돌아가기"):
        st.session_state['selected_retry_attempt'] = None
        st.rerun()

    st.markdown("---")

    # 문제별 결과
    results = detail.get('results', [])

    if not results:
        st.warning("문제 결과가 없습니다.")
        return

    for idx, result in enumerate(results, 1):
        # 정답/오답 여부
        is_correct = result['is_correct']
        title_emoji = "✅" if is_correct else "❌"
        title_text = "정답" if is_correct else "오답"

        with st.expander(
            f"문제 {idx}: {title_emoji} {title_text}",
            expanded=not is_correct  # 오답만 자동으로 펼침
        ):
            # 문제 내용
            st.markdown(f"**문제:** {result['question']}")

            st.markdown("---")

            # 답안 비교
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**내가 쓴 답:**")
                if is_correct:
                    st.success(result.get('user_answer', '(답안 없음)'))
                else:
                    st.error(result.get('user_answer', '(답안 없음)'))

            with col2:
                st.markdown("**정답:**")
                st.info(result['correct_answer'])


# ==================== 메인 로직 ====================
if st.session_state['selected_retry_attempt'] is None:
    # 목록 화면
    show_attempt_list()
else:
    # 상세 화면
    show_attempt_detail(st.session_state['selected_retry_attempt'])
