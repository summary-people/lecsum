import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

# 세션 스테이트 초기화
if 'retry_quiz_set_id' not in st.session_state:
    st.session_state['retry_quiz_set_id'] = None
if 'retry_quizzes' not in st.session_state:
    st.session_state['retry_quizzes'] = []
if 'retry_answers' not in st.session_state:
    st.session_state['retry_answers'] = {}
if 'retry_result' not in st.session_state:
    st.session_state['retry_result'] = None
if 'retry_step' not in st.session_state:
    st.session_state['retry_step'] = 'list'  # list, history_detail, creating, taking, result
if 'auto_create_retry' not in st.session_state:
    st.session_state['auto_create_retry'] = False
if 'selected_retry_attempt' not in st.session_state:
    st.session_state['selected_retry_attempt'] = None

# wrong_answer 페이지에서 재시험을 생성한 경우 자동으로 응시 화면으로 이동
if 'current_retry_quiz' in st.session_state:
    retry_data = st.session_state['current_retry_quiz']
    st.session_state['retry_quiz_set_id'] = retry_data['retry_quiz_set_id']
    st.session_state['retry_quizzes'] = retry_data['quizzes']
    st.session_state['retry_answers'] = {}
    st.session_state['retry_result'] = None
    st.session_state['retry_step'] = 'taking'
    # 처리 후 삭제
    del st.session_state['current_retry_quiz']


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


def submit_retry_quiz(retry_quiz_set_id, quiz_id_list, user_answer_list):
    """재시험 채점 API 호출"""
    try:
        response = requests.post(
            f"{API_URL}/api/quizzes/retry/grade",
            json={
                "retry_quiz_set_id": retry_quiz_set_id,
                "quiz_id_list": quiz_id_list,
                "user_answer_list": user_answer_list
            }
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("data")
        else:
            st.error(f"채점 실패: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"서버 연결 실패: {e}")
        return None


def fetch_retry_attempts(limit=50):
    """재시험 응시 기록 조회"""
    try:
        response = requests.get(
            f"{API_URL}/api/quizzes/attempts",
            params={"limit": limit, "offset": 0}
        )
        if response.status_code == 200:
            data = response.json()
            attempts = data.get("data", [])
            return [a for a in attempts if a.get('retry_quiz_set_id')]
        else:
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


# ==================== 화면 1: 재시험 목록 ====================
def show_list_screen():
    st.title("🔄 재시험")
    st.markdown("---")

    retry_attempts = fetch_retry_attempts(limit=100)

    if not retry_attempts:
        st.info("💡 아직 재시험 기록이 없습니다.")
        st.markdown("""
        ### 재시험 시작 방법
        1. **틀린 문제 모아보기** 페이지로 이동
        2. 틀린 문제를 클릭하여 상세 내용 확인
        3. **🔄 재시험 시작하기** 버튼 클릭
        """)
        return

    st.success(f"📝 총 **{len(retry_attempts)}개**의 재시험 기록이 있습니다.")
    st.markdown("---")

    # 재시험 기록 카드
    for idx, attempt in enumerate(retry_attempts, 1):
        score = attempt['score']
        if score >= 80:
            score_color = "#28a745"
            emoji = "🎉"
        elif score >= 60:
            score_color = "#17a2b8"
            emoji = "👍"
        else:
            score_color = "#ffc107"
            emoji = "💪"

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
                st.session_state['retry_step'] = 'history_detail'
                st.rerun()


# ==================== 화면 2: 재시험 기록 상세 ====================
def show_history_detail_screen():
    st.title("📊 재시험 기록 상세")
    st.markdown("---")

    attempt_id = st.session_state.get('selected_retry_attempt')
    if not attempt_id:
        st.error("오류: 선택된 재시험 기록이 없습니다.")
        st.session_state['retry_step'] = 'list'
        st.rerun()
        return

    detail = fetch_attempt_detail(attempt_id)

    if not detail:
        st.error("상세 정보를 불러올 수 없습니다.")
        if st.button("← 목록으로"):
            st.session_state['selected_retry_attempt'] = None
            st.session_state['retry_step'] = 'list'
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
        st.session_state['retry_step'] = 'list'
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


# ==================== 화면 3: 재시험 자동 생성 중 ====================
def show_creating_screen():
    st.title("🔄 재시험 생성 중...")
    st.markdown("---")

    # quiz_ids가 세션에 있으면 사용, 없으면 빈 리스트
    quiz_ids = st.session_state.get('retry_quiz_ids', [])

    if not quiz_ids:
        st.error("오류: 선택된 문제가 없습니다.")
        st.session_state['retry_step'] = 'list'
        st.rerun()
        return

    st.info(f"📝 선택된 문제: {len(quiz_ids)}개 → 재시험 문제: {len(quiz_ids) * 3}개 생성 중...")

    with st.spinner("📝 틀린 문제를 분석하고 유사한 문제를 생성하는 중... (문제당 3개씩)"):
        retry_data = create_retry_quiz(quiz_ids)

        if retry_data:
            st.session_state['retry_quiz_set_id'] = retry_data['retry_quiz_set_id']
            st.session_state['retry_quizzes'] = retry_data['quizzes']
            st.session_state['retry_answers'] = {}
            st.session_state['retry_result'] = None
            st.session_state['retry_step'] = 'taking'
            st.success(f"✅ 재시험이 생성되었습니다! (총 {retry_data['total_questions']}문제)")
            st.rerun()
        else:
            st.error("재시험 생성에 실패했습니다.")
            if st.button("← 목록으로"):
                st.session_state['retry_step'] = 'list'
                st.session_state.pop('retry_quiz_ids', None)
                st.rerun()


# ==================== 화면 4: 재시험 응시 ====================
def show_taking_screen():
    st.title("🔄 재시험 응시")
    st.markdown("---")

    quizzes = st.session_state['retry_quizzes']
    st.success(f"📝 총 {len(quizzes)}문제입니다. 모든 문제를 풀고 제출하세요!")

    for idx, quiz in enumerate(quizzes, 1):
        st.markdown(f"### 문제 {idx}")

        type_labels = {
            "multiple_choice": "객관식",
            "true_false": "O/X",
            "short_answer": "주관식",
            "fill_in_blank": "빈칸 채우기"
        }
        quiz_type = type_labels.get(quiz.get('type', ''), quiz.get('type', ''))
        st.caption(f"문제 유형: {quiz_type}")

        st.write(quiz['question'])

        if quiz.get('options') and len(quiz['options']) > 0:
            st.markdown("**보기:**")
            for i, option in enumerate(quiz['options'], 1):
                st.write(f"{i}. {option}")

        answer_key = f"answer_{quiz['id']}"

        if quiz['type'] == 'multiple_choice':
            answer = st.text_input(
                f"답을 입력하세요 (보기 번호 또는 내용)",
                key=answer_key,
                placeholder="예: 1 또는 정답 내용"
            )
        elif quiz['type'] == 'true_false':
            answer = st.radio(
                "답을 선택하세요",
                options=["O", "X"],
                key=answer_key,
                horizontal=True
            )
        else:
            answer = st.text_area(
                "답을 입력하세요",
                key=answer_key,
                height=100
            )

        st.session_state['retry_answers'][quiz['id']] = answer
        st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("← 취소", use_container_width=True):
            st.session_state['retry_step'] = 'list'
            st.session_state['retry_quiz_set_id'] = None
            st.session_state['retry_quizzes'] = []
            st.session_state['retry_answers'] = {}
            st.session_state['retry_result'] = None
            st.session_state.pop('retry_quiz_ids', None)
            st.rerun()

    with col2:
        if st.button("📝 채점하기", type="primary", use_container_width=True):
            unanswered = []
            for idx, quiz in enumerate(quizzes, 1):
                answer = st.session_state['retry_answers'].get(quiz['id'], "").strip()
                if not answer:
                    unanswered.append(idx)

            if unanswered:
                st.error(f"⚠️ 답을 입력하지 않은 문제가 있습니다: 문제 {', '.join(map(str, unanswered))}")
            else:
                quiz_id_list = [q['id'] for q in quizzes]
                user_answer_list = [st.session_state['retry_answers'][q['id']] for q in quizzes]

                with st.spinner("채점 중..."):
                    result = submit_retry_quiz(
                        st.session_state['retry_quiz_set_id'],
                        quiz_id_list,
                        user_answer_list
                    )

                    if result:
                        st.session_state['retry_result'] = result
                        st.session_state['retry_step'] = 'result'
                        st.rerun()


# ==================== 화면 5: 결과 확인 ====================
def show_result_screen():
    st.title("🎯 재시험 결과")
    st.markdown("---")

    result = st.session_state['retry_result']
    score = result['score']

    if score >= 80:
        st.success(f"### 🎉 점수: {score}점")
        st.balloons()
    elif score >= 60:
        st.info(f"### 👍 점수: {score}점")
    else:
        st.warning(f"### 💪 점수: {score}점")

    st.markdown("---")

    quizzes = st.session_state['retry_quizzes']
    results = result['results']

    for idx, (quiz, res) in enumerate(zip(quizzes, results), 1):
        with st.expander(
            f"문제 {idx}: {'✅ 정답' if res['is_correct'] else '❌ 오답'}",
            expanded=not res['is_correct']
        ):
            st.markdown(f"**문제:** {quiz['question']}")

            if quiz.get('options') and len(quiz['options']) > 0:
                st.markdown("**보기:**")
                for i, option in enumerate(quiz['options'], 1):
                    st.write(f"{i}. {option}")

            st.markdown("---")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**내 답:**")
                if res['is_correct']:
                    st.success(st.session_state['retry_answers'][quiz['id']])
                else:
                    st.error(st.session_state['retry_answers'][quiz['id']])

            with col2:
                st.markdown("**정답:**")
                st.info(quiz['correct_answer'])

            st.markdown("**피드백:**")
            st.write(res['feedback'])

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ 완료", type="primary", use_container_width=True):
            st.session_state['retry_step'] = 'list'
            st.session_state['retry_quiz_set_id'] = None
            st.session_state['retry_quizzes'] = []
            st.session_state['retry_answers'] = {}
            st.session_state['retry_result'] = None
            st.session_state.pop('retry_quiz_ids', None)
            st.rerun()


# ==================== 메인 로직 ====================
# 틀린 문제 페이지에서 자동 생성 요청이 온 경우
if st.session_state.get('auto_create_retry'):
    st.session_state['retry_step'] = 'creating'
    st.session_state['auto_create_retry'] = False

# 현재 단계에 따라 화면 표시
if st.session_state['retry_step'] == 'list':
    show_list_screen()
elif st.session_state['retry_step'] == 'history_detail':
    show_history_detail_screen()
elif st.session_state['retry_step'] == 'creating':
    show_creating_screen()
elif st.session_state['retry_step'] == 'taking':
    show_taking_screen()
elif st.session_state['retry_step'] == 'result':
    show_result_screen()
