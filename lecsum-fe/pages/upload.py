# pages/upload.py
import streamlit as st
import requests
from pathlib import Path
from datetime import datetime
import html as _html
import markdown as _markdown

API_BASE_URL = "http://localhost:8000"  # 백엔드 주소

def _md_to_html(md_text: str) -> str:
    """
    Convert markdown text to HTML for Streamlit rendering.

    IMPORTANT:
    - Backend-provided HTML is trusted and rendered as-is.
    """
    if not md_text:
        return ""

    try:
        return _markdown.markdown(
            md_text,
            extensions=["fenced_code", "tables"],
            output_format="html5",
        )
    except Exception:
        return md_text.replace("\n", "<br/>")


def render_summary_card_inline(
    filename: str,
    summary_html: str,
    keywords: list[str],
    concept_cnt: int,
    keyword_cnt: int,
    review_time: str,
    created_at: str,
):
    """요약 카드 HTML 생성 (인라인)"""
    
    # 키워드 HTML
    kw_html = "".join(
        f'<span class="kw-chip">{_html.escape(k)}</span>'
        for k in keywords
    ) or '<span style="color: #6b7280;">키워드가 없습니다.</span>'
    
    return f"""
    <div class="summary-card">
        <div class="summary-header">
            <div class="summary-badge">✨ AI 요약</div>
            <div class="summary-title">{_html.escape(filename)}</div>
            <div class="summary-date">📅 {created_at}</div>
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
                <div class="stat-value">{review_time}</div>
                <div>예상 복습 시간</div>
            </div>
        </div>
        
        <div class="summary-keywords">
            <h4>🔑 핵심 키워드</h4>
            <div class="keyword-list">{kw_html}</div>
        </div>
    </div>
    """


def render_upload_page():
    # CSS 로드
    css_dir = Path(__file__).parent.parent / "styles"
    upload_css = (css_dir / "upload.css").read_text()
    summary_css = (css_dir / "summary.css").read_text()
    st.markdown(f"<style>{upload_css}\n{summary_css}</style>", unsafe_allow_html=True)

    # 헤더
    st.markdown("""
    <div class="upload-header">
        <h1>문서 업로드</h1>
        <p>PDF 또는 PPT 파일을 업로드하면 AI가 자동으로 핵심 내용을 요약합니다</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("upload_form"):
        # summary_type 선택
        summary_type = st.selectbox("요약 유형 선택", ["lecture", "bullet", "exam"])

        # 파일 업로드
        uploaded_file = st.file_uploader(
            "파일 업로드",
            type=["pdf", "ppt", "pptx"],
            label_visibility="collapsed"
        )

        submitted = st.form_submit_button("요약 시작하기")

    if submitted and uploaded_file:
        st.info(f"📄 선택된 파일: {uploaded_file.name}")

        with st.spinner("AI가 문서를 분석하고 있습니다..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/uploads/documents?summary_type={summary_type}",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    },
                    timeout=120
                )

                response.raise_for_status()
                result = response.json()

                if result.get("status"):
                    document_id = result["data"]["id"]
                    summary = result["data"]["summary"]

                    # 요약 결과 카드 UI
                    keywords = result["data"].get("keywords", [])

                    created_at_text = datetime.now().strftime("%Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후")
                    backend_created_at = result["data"].get("created_at")
                    if isinstance(backend_created_at, str) and backend_created_at.strip():
                        try:
                            dt = datetime.fromisoformat(backend_created_at)
                            created_at_text = dt.strftime("%Y년 %m월 %d일 %p %I:%M").replace("AM", "오전").replace("PM", "오후")
                        except Exception:
                            created_at_text = backend_created_at

                    summary_html = _md_to_html(summary)

                    concept_cnt = result["data"].get("concept_cnt", 0)
                    keyword_cnt = len(keywords)
                    review_time = f"{result['data'].get('review_time', 5)}분"

                    card_html = render_summary_card_inline(
                        filename=uploaded_file.name,
                        summary_html=summary_html,
                        keywords=keywords,
                        concept_cnt=concept_cnt,
                        keyword_cnt=keyword_cnt,
                        review_time=review_time,
                        created_at=created_at_text
                    )

                    st.markdown(card_html, unsafe_allow_html=True)

                    st.divider()

                    # 이후 페이지 이동용
                    st.session_state["document_id"] = document_id

                else:
                    st.error("❌ 요약 실패")
                    st.write(result)

            except requests.exceptions.RequestException as e:
                st.error("❌ 서버 요청 중 오류 발생")
                st.code(str(e))
    elif submitted and not uploaded_file:
        st.warning("⚠️ 파일을 업로드해주세요.")