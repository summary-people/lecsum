import streamlit as st
from services.api_client import APIClient
from utils.ui_components import render_sidebar
from datetime import datetime

api_client = APIClient()

def format_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y년 %m월 %d일 %H:%M')
    except:
        return date_str
    
# 1. 페이지 설정 및 스타일 커스텀
st.set_page_config(page_title="Quiz Archive", page_icon="🗄️", layout="wide")
render_sidebar()

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; }
    .quiz-card { 
        padding: 20px; 
        border-radius: 10px; 
        border: 1px solid #e0e0e0; 
        background-color: white;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
if "loaded_attempts" not in st.session_state:
    st.session_state.loaded_attempts = {}

st.title("🗄️ 퀴즈 보관함")
st.markdown("과거에 생성한 퀴즈와 응시 기록을 한눈에 확인하세요.")


# --- 메인 로직 ---
if st.session_state.get("selected_pdf_id"):
    try:
        response = api_client.get_quiz_sets(st.session_state.selected_pdf_id)
        quiz_sets = response.get("data", [])

        if not quiz_sets:
            st.empty()
            st.info("💡 해당 문서에 생성된 퀴즈가 없습니다. 먼저 퀴즈를 생성해 주세요.")
        else:
            # 상단 요약 정보
            st.subheader(f"📚 총 {len(quiz_sets)}개의 퀴즈 세트")
            
            for idx, qs in enumerate(quiz_sets, start=1):
                qs_id = qs['id']
                
                # 퀴즈 세트 카드 시작
                with st.container(border=True):
                    header_col, btn_col = st.columns([4, 1])
                    formatted_qs_date = format_date(qs['created_at'])
                    
                    with header_col:
                        st.markdown(f"### 🧩 퀴즈 #{idx}")
                        st.caption(f"📅 **생성일**: {formatted_qs_date} | 📝 **문항**: {len(qs.get('quizs', []))}개")
                    
                    with btn_col:
                        st.write("") # 간격 조정
                        if st.button("📊 응시 기록 확인", key=f"btn_{qs_id}"):
                            with st.spinner("기록 조회 중..."):
                                attempt_res = api_client.get_quiz_attempts(qs_id)
                                st.session_state.loaded_attempts[qs_id] = attempt_res.get("data", [])

                    # 퀴즈 문항 내용 표시 (Expander)
                    with st.expander("📝 문제 내용 확인", expanded=False):
                        for q in qs.get('quizs', []):
                            st.markdown(f"#### Q{q['number']}. {q['question']}")
                            
                            if q['options']:
                                # 보기를 4행 1열(세로)로 나열
                                for idx, opt in enumerate(q['options']):
                                    st.markdown(
                                        f"""
                                        <div style="
                                            background-color: #ffffff; 
                                            padding: 12px 15px; 
                                            border-radius: 8px; 
                                            border: 1px solid #ececf1; 
                                            margin-bottom: 8px;
                                            display: flex;
                                            align-items: center;
                                            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                                        ">
                                            <span style="
                                                background-color: #4A90E2; 
                                                color: white; 
                                                font-weight: bold; 
                                                border-radius: 4px; 
                                                padding: 2px 8px; 
                                                margin-right: 12px;
                                                font-size: 0.9em;
                                            ">
                                                {idx+1}
                                            </span>
                                            <span style="color: #374151; font-size: 1em;">{opt}</span>
                                        </div>
                                        """, 
                                        unsafe_allow_html=True
                                    )
                            
                            elif q['type'] in ['short_answer', 'fill_in_blank']:
                                st.info("", icon="✍️")
                            
                            st.write("") # 문항 간 간격 조절

                    # 응시 결과 표시
                    if qs_id in st.session_state.loaded_attempts:
                        attempts = st.session_state.loaded_attempts[qs_id]
                        
                        if not attempts:
                            st.warning("➖ 아직 이 퀴즈에 대한 응시 기록이 없습니다.")
                        else:
                            st.divider()
                            st.markdown("#### 📜 응시 히스토리")
                            
                            
                            for att in attempts:
                                score = att['score']
                                # 점수에 따른 색상 및 이모지 결정
                                if score >= 80:
                                    status_icon, color = "🌟", "green"
                                elif score >= 50:
                                    status_icon, color = "⚡", "orange"
                                else:
                                    status_icon, color = "💡", "red"
                                
                                with st.expander(f"{status_icon} {att['created_at']} — 점수: :{color}[{score}점]"):
                                    # 메트릭으로 요약 정보 표시
                                    m1, m2, m3 = st.columns(3)
                                    m1.metric("최종 점수", f"{score}점")
                                    m2.metric("정답 수", f"{sum(1 for r in att.get('results', []) if r['is_correct'])}개")
                                    m3.metric("오답 수", f"{sum(1 for r in att.get('results', []) if not r['is_correct'])}개")
                                    
                                    st.markdown("---")
                                    for res in att.get("results", []):
                                        icon = "✅" if res['is_correct'] else "❌"
                                        st.write(f"{icon} **Q{res['quiz']['number']}.** {res['quiz']['question']}")
                                        st.info(f"**내 답변:** {res['user_answer']}")
    
    except Exception as e:
        st.error(f"❌ 데이터를 가져오는 중 오류가 발생했습니다: {e}")
else:
    # 초기 진입 화면
    st.container()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("👈 왼쪽 사이드바에서 **문서 ID**를 입력하고 **기록 불러오기** 버튼을 클릭해 주세요.")