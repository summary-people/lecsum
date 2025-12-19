# pages/summaries.py
import os
import streamlit as st
from datetime import datetime
from services.api_client import APIClient
import html
from components.summary_card import render_summary_card_html
from pages.upload import _md_to_html

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
        name = html.escape(doc.get("name", ""))
        created_at = doc.get("created_at", "")

        try:
            created_at = datetime.fromisoformat(created_at).strftime("%Y년 %m월 %d일")
        except Exception:
            pass

        keywords = doc.get("keywords", [])
        raw_summary = doc.get("summary", "")

        card_html = render_summary_card_html(
            filename=name,
            summary_html=_md_to_html(raw_summary),
            keywords=keywords,
            created_at=doc.get("created_at"),
        )

        st.markdown(
            f"""
            <details class="summary-item">
              <summary class="summary-toggle">
                <div class="file-left">
                  <div class="file-icon">📄</div>
                </div>
                <div class="file-meta">
                  <div class="file-name">{name}</div>
                  <div class="file-sub">📅 {created_at} · PDF</div>
                </div>
              </summary>

              <div class="summary-content">
                {card_html}
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)