import streamlit as st
from datetime import datetime
from services.api_client import APIClient
from utils.ui_components import render_header

# --- 유틸리티 함수 ---
def format_date(date_str: str) -> str:
    """ISO 포맷 날짜 문자열을 보기 좋은 형식으로 변환"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y년 %m월 %d일 %H:%M')
    except Exception:
        return date_str

def init_session_state():
    """세션 상태 초기화"""
    if "loaded_attempts" not in st.session_state:
        st.session_state.loaded_attempts = {}
    if "attempt_details" not in st.session_state:
        st.session_state.attempt_details = {}
    if "selected_document_id" not in st.session_state:
        st.session_state.selected_document_id = None

# --- UI 렌더링 함수 ---
def render_quiz_result_page():
    # 1. 초기 설정
    # 주의: set_page_config는 app.py에서 한 번만 호출되므로 여기서는 제거합니다.
    api = APIClient()
    init_session_state()

    # 2. 헤더 렌더링
    render_header("🗄️ 퀴즈 보관함", "지금까지 생성한 퀴즈와 응시 기록을 한눈에 확인하세요.")

    # 3. 스타일 주입 (퀴즈 카드 및 보기 스타일)
    st.markdown("""
        <style>
        .quiz-card { 
            padding: 20px; 
            border-radius: 10px; 
            border: 1px solid #e0e0e0; 
            background-color: white;
            margin-bottom: 15px;
        }
        .option-box {
            background-color: #ffffff; 
            padding: 12px 15px; 
            border-radius: 8px; 
            border: 1px solid #ececf1; 
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .option-badge {
            background-color: #4A90E2; 
            color: white; 
            font-weight: bold; 
            border-radius: 4px; 
            padding: 2px 8px; 
            margin-right: 12px;
            font-size: 0.9em;
        }
        .option-text {
            color: #374151; 
            font-size: 1em;
        }
        </style>
    """, unsafe_allow_html=True)

    # 4. 문서 선택 로직 (quiz.py와 동일한 UX 제공)
    st.markdown("### 📂 문서 선택")
    
    try:
        res = api.get_documents(limit=20, offset=0)
        documents = res.get("data", [])
    except Exception as e:
        st.error(f"문서 목록 조회 실패: {e}")
        return

    if not documents:
        st.info("📂 저장된 문서가 없습니다.")
        return

    # 문서 선택 SelectBox
    doc_map = {f"{doc['name']} ({doc['created_at'][:10]})": doc["id"] for doc in documents}
    
    # 세션에 저장된 ID가 목록에 있다면 default로 설정
    current_index = 0
    if st.session_state.selected_document_id in doc_map.values():
        current_id = st.session_state.selected_document_id
        # ID로 키(Key) 찾기
        current_label = next((k for k, v in doc_map.items() if v == current_id), None)
        if current_label:
            current_index = list(doc_map.keys()).index(current_label)

    selected_doc_label = st.selectbox(
        "기록을 조회할 문서를 선택하세요",
        list(doc_map.keys()),
        index=current_index
    )
    
    # 선택된 문서 ID 업데이트
    if selected_doc_label:
        st.session_state.selected_document_id = doc_map[selected_doc_label]

    # 5. 메인 로직: 선택된 문서의 퀴즈 세트 조회
    if st.session_state.selected_document_id:
        doc_id = st.session_state.selected_document_id
        
        try:
            # APIClient에 get_quiz_sets 메소드가 있다고 가정 (없다면 추가 필요)
            response = api.get_quiz_sets(doc_id) 
            quiz_sets = response.get("data", [])

            st.divider()

            if not quiz_sets:
                st.info("💡 해당 문서에 생성된 퀴즈가 없습니다.")
            else:
                st.subheader(f"📚 총 {len(quiz_sets)}개의 퀴즈 세트")
                
                for idx, qs in enumerate(quiz_sets, start=1):
                    qs_id = qs['id']
                    
                    with st.container(border=True):
                        # --- 카드 헤더 ---
                        header_col, btn_col = st.columns([4, 1])
                        formatted_qs_date = format_date(qs['created_at'])
                        
                        with header_col:
                            st.markdown(f"### 🧩 퀴즈 세트 #{idx}")
                            st.caption(f"📅 **생성일**: {formatted_qs_date} | 📝 **문항수**: {len(qs.get('quizs', []))}개")
                        
                        with btn_col:
                            st.write("")
                            if st.button("📊 응시 기록 확인", key=f"btn_view_{qs_id}", use_container_width=True):
                                with st.spinner("기록 조회 중..."):
                                    # APIClient에 get_attempts 메소드가 있다고 가정
                                    att_res = api.get_attempts(quiz_set_id=qs_id)
                                    st.session_state.loaded_attempts[qs_id] = att_res.get("data", [])

                        # --- 문제 내용 (Expander) ---
                        with st.expander("📝 문제 및 보기 확인", expanded=False):
                            for q in qs.get('quizs', []):
                                st.markdown(f"**Q{q['number']}. {q['question']}**")
                                
                                # 객관식 보기 렌더링 (4행 1열)
                                if q.get('options'):
                                    for opt_idx, opt in enumerate(q['options']):
                                        st.markdown(
                                            f"""
                                            <div class="option-box">
                                                <span class="option-badge">{opt_idx+1}</span>
                                                <span class="option-text">{opt}</span>
                                            </div>
                                            """, 
                                            unsafe_allow_html=True
                                        )
                                
                                elif q['type'] in ['short_answer', 'fill_in_blank']:
                                    st.info("✍️ 주관식 문항입니다.", icon="ℹ️")
                                
                                st.write("") # 간격

                        # --- 응시 기록 표시 (하단 영역) ---
                        if qs_id in st.session_state.loaded_attempts:
                            attempts = st.session_state.loaded_attempts[qs_id]
                            
                            st.markdown("#### 📜 응시 히스토리")
                            if not attempts:
                                st.warning("➖ 아직 응시 기록이 없습니다.")
                            
                            for att in attempts:
                                att_id = att['id']
                                score = att['score']
                                # 점수별 색상
                                color = "green" if score >= 80 else "orange" if score >= 50 else "red"
                                icon = "🌟" if score >= 80 else "⚡" if score >= 50 else "💡"

                                # Expander 라벨 구성
                                exp_label = f"{icon} {format_date(att['created_at'])} — 점수: :{color}[{score}점] ({att.get('correct_count', 0)}/{len(qs.get('quizs', []))})"
                                
                                with st.expander(exp_label):
                                    # 상세 조회 로직
                                    is_loaded = att_id in st.session_state.attempt_details
                                    
                                    if not is_loaded:
                                        if st.button("상세 결과 보기", key=f"det_{att_id}"):
                                            try:
                                                # APIClient에 get_attempt_detail 메소드가 있다고 가정
                                                detail_res = api.get_attempt_detail(att_id)
                                                st.session_state.attempt_details[att_id] = detail_res.get("data", {})
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"상세 정보 로드 실패: {e}")
                                    
                                    # 상세 데이터 렌더링
                                    if att_id in st.session_state.attempt_details:
                                        detail = st.session_state.attempt_details[att_id]
                                        
                                        # 메트릭
                                        m1, m2, m3 = st.columns(3)
                                        m1.metric("최종 점수", f"{detail['score']}점")
                                        m2.metric("정답 수", f"{detail.get('correct_count', 0)}개")
                                        m3.metric("오답 수", f"{detail.get('quiz_count', 0) - detail.get('correct_count', 0)}개")
                                        
                                        st.divider()
                                        
                                        # 문항별 결과
                                        for res in detail.get("results", []):
                                            q_status = "✅" if res['is_correct'] else "❌"
                                            st.markdown(f"**{q_status} Q. {res['question']}**")
                                            
                                            col_a, col_b = st.columns(2)
                                            with col_a:
                                                if res['is_correct']:
                                                    st.success(f"내 답변: {res['user_answer']}")
                                                else:
                                                    st.error(f"내 답변: {res['user_answer']}")
                                            with col_b:
                                                if not res['is_correct']:
                                                    st.info(f"정답: {res['correct_answer']}")
                                            st.write("")

        except Exception as e:
            st.error(f"❌ 데이터 조회 중 오류가 발생했습니다: {e}")

# 직접 실행 시 (테스트 용도)
if __name__ == "__main__":
    render_quiz_result_page()