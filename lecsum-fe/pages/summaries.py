# pages/summaries.py
import os
import streamlit as st
from datetime import datetime
from services.api_client import APIClient
import html as html_module
import markdown as md_module

def _md_to_html(md_text: str) -> str:
    """마크다운을 HTML로 변환"""
    if not md_text:
        return ""
    try:
        return md_module.markdown(
            md_text,
            extensions=["fenced_code", "tables", "nl2br"],
            output_format="html5",
        )
    except Exception:
        return md_text.replace("\n", "<br/>")


def render_summary_card_html_inline(
    filename: str,
    summary_html: str,
    keywords: list[str],
    concept_cnt: int,
    keyword_cnt: int,
    review_time: int,
    created_at: str,
):
    """요약 카드 HTML 생성 (인라인)"""
    
    # 날짜 포맷팅
    try:
        dt = datetime.fromisoformat(created_at)
        formatted_date = dt.strftime("%Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후")
    except Exception:
        formatted_date = datetime.now().strftime("%Y년 %m월 %d일 오후 %I:%M")
    
    # 키워드 HTML
    kw_html = "".join(
        f'<span class="kw-chip">{html_module.escape(k)}</span>'
        for k in keywords
    ) or '<span style="color: #6b7280;">키워드가 없습니다.</span>'
    
    return f"""
    <div class="summary-card">
        <div class="summary-header">
            <div class="summary-badge">✨ AI 요약</div>
            <div class="summary-title">{html_module.escape(filename)}</div>
            <div class="summary-date">📅 {formatted_date}</div>
        </div>
        
        <div class="summary-section">
            <h3>📝 요약 내용</h3>
            <div class="summary-box">{summary_html}</div>
        </div>
        
        <div class="summary-stats">
            <div class="stat blue">
                <div class="stat-value">{concept_cnt}</div>
                <div>개념 수</div>
            </div>
            <div class="stat purple">
                <div class="stat-value">{keyword_cnt}</div>
                <div>키워드 수</div>
            </div>
            <div class="stat pink">
                <div class="stat-value">{review_time}분</div>
                <div>예상 복습 시간</div>
            </div>
        </div>
        
        <div class="summary-keywords">
            <h4>🔑 핵심 키워드</h4>
            <div class="keyword-list">{kw_html}</div>
        </div>
    </div>
    """


def render_summaries_page():
    # CSS 로드
    css_dir = os.path.join(os.path.dirname(__file__), "..", "styles")
    for css_name in ["summary.css", "upload.css", "summary_list.css"]:
        css_path = os.path.join(css_dir, css_name)
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

    st.markdown("<div class='summary-list'>", unsafe_allow_html=True)

    for doc in documents:
        name = doc.get("name", "")
        name_escaped = html_module.escape(name)
        created_at = doc.get("created_at", "")

        try:
            created_at_display = datetime.fromisoformat(created_at).strftime("%Y년 %m월 %d일")
        except Exception:
            created_at_display = "날짜 정보 없음"

        keywords = doc.get("keywords", [])
        raw_summary = doc.get("summary", "")
        
        # 기본값 처리
        concept_cnt = doc.get("concept_cnt", doc.get("concept_count", 0))
        keyword_cnt = doc.get("keyword_cnt", len(keywords))
        review_time = doc.get("review_time", 5)

        # 마크다운을 HTML로 변환
        summary_html = _md_to_html(raw_summary)

        # 카드 HTML 생성
        card_html = render_summary_card_html_inline(
            filename=name,
            summary_html=summary_html,
            keywords=keywords,
            concept_cnt=concept_cnt,
            keyword_cnt=keyword_cnt,
            review_time=review_time,
            created_at=created_at,
        )

        # 토글 카드 시작 부분 렌더링
        st.markdown(
            f"""
            <details class="summary-item">
              <summary class="summary-toggle">
                <div class="file-left">
                  <div class="file-icon">📄</div>
                </div>
                <div class="file-meta">
                  <div class="file-name">{name_escaped}</div>
                  <div class="file-sub">📅 {created_at_display} · PDF</div>
                </div>
              </summary>
              <div class="summary-content">
            """,
            unsafe_allow_html=True
        )
        
        # 카드 HTML 별도 렌더링 (이스케이프 방지)
        st.markdown(card_html, unsafe_allow_html=True)
        
        # 닫는 태그
        st.markdown("</div></details>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)