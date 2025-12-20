import streamlit as st
from datetime import datetime

def render_summary_card(
    filename: str,
    summary_text: str,
    keywords: list[str],
    concept_cnt: int,
    keyword_cnt: int,
    review_time: int,
    created_at: str | None = None,
):
    """스트림릿 네이티브 컴포넌트로 요약 카드 렌더링"""
    
    # 날짜 포맷팅
    if created_at:
        try:
            dt = datetime.fromisoformat(created_at)
            formatted_date = dt.strftime("%Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후")
        except Exception:
            formatted_date = datetime.now().strftime("%Y년 %m월 %d일 오후 %I:%M")
    else:
        formatted_date = datetime.now().strftime("%Y년 %m월 %d일 오후 %I:%M")
    
    # 카드 컨테이너
    with st.container():
        # 헤더 (보라색 배경)
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #7c3aed, #2563eb); 
                        padding: 32px; border-radius: 24px 24px 0 0; color: white;">
                <div style="font-weight: 700; opacity: 0.9; margin-bottom: 8px;">✨ AI 요약</div>
                <div style="font-size: 28px; font-weight: 800;">{filename}</div>
                <div style="opacity: 0.85; margin-top: 6px;">📅 {formatted_date}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("### 📝 요약 내용")
        with st.expander("요약 보기", expanded=True):
            st.markdown(summary_text)
        
        # 통계 (3열)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                f"""
                <div style="background: #eff6ff; padding: 20px; border-radius: 16px; text-align: center;">
                    <div style="font-size: 32px; font-weight: 800; color: #2563eb;">{concept_cnt}</div>
                    <div style="font-size: 13px; font-weight: 600; color: #2563eb; opacity: 0.8;">개념 수</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div style="background: #faf5ff; padding: 20px; border-radius: 16px; text-align: center;">
                    <div style="font-size: 32px; font-weight: 800; color: #7c3aed;">{keyword_cnt}</div>
                    <div style="font-size: 13px; font-weight: 600; color: #7c3aed; opacity: 0.8;">키워드 수</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f"""
                <div style="background: #fdf2f8; padding: 20px; border-radius: 16px; text-align: center;">
                    <div style="font-size: 32px; font-weight: 800; color: #db2777;">{review_time}분</div>
                    <div style="font-size: 13px; font-weight: 600; color: #db2777; opacity: 0.8;">예상 복습 시간</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # 키워드
        st.markdown("### 🔑 핵심 키워드")
        if keywords:
            # 키워드를 pills 형태로 표시
            keywords_html = " ".join([
                f'<span style="display: inline-block; background: #ede9fe; color: #7c3aed; '
                f'padding: 8px 16px; border-radius: 999px; font-weight: 600; font-size: 14px; '
                f'margin: 4px; border: 1px solid #ddd6fe;">{kw}</span>'
                for kw in keywords
            ])
            st.markdown(f'<div style="margin-top: 12px;">{keywords_html}</div>', unsafe_allow_html=True)
        else:
            st.info("키워드가 없습니다.")
        
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)