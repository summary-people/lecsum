# pages/summaries.py
import os
import streamlit as st
from datetime import datetime
from services.api_client import APIClient
import html as html_module
from pages.upload import _md_to_html


def render_summaries_page():
    css_dir = os.path.join(os.path.dirname(__file__), "..", "styles")
    
    all_css = ""
    for css_name in ["upload.css", "summary_list.css"]:
        css_path = os.path.join(css_dir, css_name)
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as f:
                all_css += f.read() + "\n"
    
    # 추가 인라인 CSS
    inline_css = """
    <style>
    .summary-inner-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 1rem;
        padding: 2rem;
        color: white;
    }
    
    .summary-header-simple {
        margin-bottom: 2rem;
    }
    
    .summary-badge-simple {
        background: rgba(255, 255, 255, 0.2);
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .summary-title-simple {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .summary-date-simple {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .summary-section-simple {
        margin-bottom: 2rem;
    }
    
    .summary-section-title {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .summary-box-simple {
        background: rgba(255, 255, 255, 0.95);
        color: #333;
        padding: 1.5rem;
        border-radius: 0.75rem;
        line-height: 1.8;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .summary-box-simple h1, 
    .summary-box-simple h2, 
    .summary-box-simple h3 {
        color: #667eea;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .summary-box-simple ul, 
    .summary-box-simple ol {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .summary-box-simple li {
        margin-bottom: 0.5rem;
    }
    
    .summary-stats-simple {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-item {
        background: rgba(255, 255, 255, 0.2);
        padding: 1.5rem;
        border-radius: 0.75rem;
        text-align: center;
    }
    
    .stat-item.blue .stat-number {
        color: #60a5fa;
    }
    
    .stat-item.purple .stat-number {
        color: #c084fc;
    }
    
    .stat-item.pink .stat-number {
        color: #f472b6;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .summary-keywords-simple {
        margin-top: 2rem;
    }
    
    .keyword-wrap-simple {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .keyword-chip {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        font-size: 0.9rem;
    }
    
    .summary-list {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .summary-item {
        background: white;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .summary-toggle {
        padding: 1.5rem;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        list-style: none;
    }
    
    .summary-toggle::-webkit-details-marker {
        display: none;
    }
    
    .summary-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .summary-icon {
        font-size: 2rem;
    }
    
    .summary-name {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
    }
    
    .summary-sub {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.25rem;
    }
    
    .summary-chevron {
        color: #999;
        transition: transform 0.3s;
    }
    
    details[open] .summary-chevron {
        transform: rotate(180deg);
    }
    
    .summary-content {
        padding: 0 1.5rem 1.5rem;
    }
    
    .page-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 2rem;
        text-align: center;
    }
    </style>
    """
    
    if all_css:
        st.markdown(f"<style>{all_css}</style>", unsafe_allow_html=True)

    st.markdown("<h1 class='page-title'>📚 업로드된 문서</h1>", unsafe_allow_html=True)

    api = APIClient()

    with st.spinner("요약 문서를 불러오는 중..."):
        res = api.get_documents(limit=10, offset=0)

    if not res or not res.get("status"):
        st.error(res.get("message", "문서를 불러오지 못했습니다."))
        return

    documents = res.get("data", [])
    if not documents:
        st.info("아직 업로드된 문서가 없습니다.")
        return

    for idx, doc in enumerate(documents):
        name = doc.get("name", "")
        name_escaped = html_module.escape(name)
        created_at = doc.get("created_at", "")

        # 토글 헤더용 날짜 포맷
        try:
            created_at_display = datetime.fromisoformat(created_at).strftime("%Y년 %m월 %d일")
        except Exception:
            created_at_display = "날짜 정보 없음"

        # 카드 내부용 날짜 포맷
        try:
            dt = datetime.fromisoformat(created_at)
            formatted_date = dt.strftime("%Y년 %m월 %d일 오전 %I:%M")
        except Exception:
            formatted_date = created_at_display

        keywords = doc.get("keywords", [])
        raw_summary = doc.get("summary", "")
        
        # 기본값 처리
        concept_cnt = doc.get("concept_cnt", doc.get("concept_count", 15))
        keyword_cnt = doc.get("keyword_cnt", len(keywords) if keywords else 8)
        review_time = doc.get("review_time", 5)

        # 마크다운을 HTML로 변환
        summary_html = _md_to_html(raw_summary)

        # 키워드 HTML 생성
        if keywords:
            keywords_html = "".join([
                f'<span class="keyword-chip">{html_module.escape(k)}</span>' 
                for k in keywords
            ])
        else:
            keywords_html = '<span style="color: rgba(255,255,255,0.7);">키워드가 없습니다.</span>'

        # Expander 사용
        with st.expander(f"📄 {name} (업로드: {created_at_display})", expanded=False):
            card_html = f"""
            {inline_css}
            <div class="summary-inner-card">
              <div class="summary-header-simple">
                <div class="summary-badge-simple">✨ AI 요약</div>
                <div class="summary-title-simple">{name_escaped}</div>
                <div class="summary-date-simple">업로드: {formatted_date}</div>
              </div>

              <div class="summary-section-simple">
                <div class="summary-section-title">요약 내용</div>
                <div class="summary-box-simple">
                  {summary_html}
                </div>
              </div>

              <div class="summary-stats-simple">
                <div class="stat-item blue">
                  <div class="stat-number">{concept_cnt}</div>
                  <div class="stat-label">주요 개념</div>
                </div>
                <div class="stat-item purple">
                  <div class="stat-number">{keyword_cnt}</div>
                  <div class="stat-label">핵심 키워드</div>
                </div>
                <div class="stat-item pink">
                  <div class="stat-number">{review_time}분</div>
                  <div class="stat-label">예상 복습 시간</div>
                </div>
              </div>

              <div class="summary-keywords-simple">
                <div class="summary-section-title">핵심 키워드</div>
                <div class="keyword-wrap-simple">
                  {keywords_html}
                </div>
              </div>
            </div>
            """
            
            st.components.v1.html(card_html, height=1200, scrolling=True)