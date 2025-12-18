import streamlit as st

def render_header(title, subtitle=None):
    """헤더와 구분선을 렌더링하여 앱의 일관성을 높임"""
    st.title(title)
    if subtitle:
        st.markdown(f"#### {subtitle}")
    st.divider()

def render_grade_result(grade_data):
    """채점 결과를 시각적으로 풍부하게 표현 (점수, 상태, 문항별 피드백)"""
    
    # 1. 상단 점수 및 애니메이션
    score = grade_data.get("score", 0)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 점수에 따른 아이콘 및 색상 변경
        if score >= 90:
            st.metric(label="최종 등급", value="🏆 Excellent", delta="Perfect!")
            st.balloons()
        elif score >= 70:
            st.metric(label="최종 등급", value="✅ Good", delta="Great job!")
            st.snow()
        else:
            st.metric(label="최종 등급", value="✍️ Study More", delta="- Try again", delta_color="inverse")

    with col2:
        st.markdown(f"### 📊 최종 점수: `{score}` / 100")
        st.progress(score / 100) # 점수 시각화

    st.markdown("---")
    st.subheader("📝 상세 문항 분석")

    # 2. 개별 문제 피드백 렌더링
    for i, detail in enumerate(grade_data.get("results", [])):
        is_correct = detail.get("is_correct", False)
        label = "✅ 정답" if is_correct else "❌ 오답"
        
        # Expander의 테두리 색상은 직접 바꿀 수 없으므로, 내부 컨텐츠에 색상 적용
        with st.expander(f"문제 {i+1} : {label}", expanded=not is_correct):            

            # AI 피드백
            st.markdown("**💡 AI 해설**")
            if is_correct:
                st.info(detail["feedback"])
            else:
                st.error(detail["feedback"])

    # 다시 시도 버튼 등 추가 액션 제안
    if st.button("🔄 처음부터 다시 풀기", use_container_width=True):
        st.session_state.grade_result = None
        st.session_state.current_quiz = None
        st.rerun()