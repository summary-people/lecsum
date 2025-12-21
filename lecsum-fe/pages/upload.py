# pages/upload.py
import streamlit as st
import requests
from pathlib import Path
from datetime import datetime
import html as _html
import markdown as _markdown

API_BASE_URL = "http://localhost:8000"

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


def render_upload_page():
    # CSS 로드
    css_dir = Path(__file__).parent.parent / "styles"
    upload_css = (css_dir / "upload.css").read_text()
    
    # 인라인 CSS 추가
    inline_css = """
    <style>
    .summary-card-v2 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 1rem;
        padding: 2rem;
        color: white;
        margin: 2rem 0;
    }
    
    .summary-top {
        margin-bottom: 2rem;
    }
    
    .summary-badge-v2 {
        background: rgba(255, 255, 255, 0.2);
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .summary-title-v2 {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .summary-date-v2 {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .summary-section-v2 {
        margin-bottom: 2rem;
    }
    
    .summary-section-title-v2 {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .summary-box-v2 {
        background: rgba(255, 255, 255, 0.95);
        color: #333;
        padding: 1.5rem;
        border-radius: 0.75rem;
        line-height: 1.8;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .summary-box-v2 h1, 
    .summary-box-v2 h2, 
    .summary-box-v2 h3 {
        color: #667eea;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .summary-box-v2 ul, 
    .summary-box-v2 ol {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .summary-box-v2 li {
        margin-bottom: 0.5rem;
    }
    
    .summary-stats-v2 {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-v2 {
        background: rgba(255, 255, 255, 0.2);
        padding: 1.5rem;
        border-radius: 0.75rem;
        text-align: center;
    }
    
    .stat-v2.blue .stat-number-v2 {
        color: #60a5fa;
    }
    
    .stat-v2.purple .stat-number-v2 {
        color: #c084fc;
    }
    
    .stat-v2.pink .stat-number-v2 {
        color: #f472b6;
    }
    
    .stat-number-v2 {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .stat-label-v2 {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .summary-keywords-v2 {
        margin-top: 2rem;
    }
    
    .summary-keywords-title-v2 {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .keyword-list-v2 {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .kw-chip {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        font-size: 0.9rem;
    }
    </style>
    """
    
    st.markdown(f"<style>{upload_css}</style>", unsafe_allow_html=True)

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

                    # 키워드 HTML
                    kw_html = "".join(
                        f'<span class="kw-chip">{_html.escape(k)}</span>'
                        for k in keywords
                    ) or '<span style="color: rgba(255,255,255,0.7);">키워드가 없습니다.</span>'

                    card_html = f"""
                    {inline_css}
                    <div class="summary-card-v2">
                        
                        <div class="summary-top">
                            <div class="summary-header-left">
                                <div class="summary-badge-v2">✨ AI 요약</div>
                                <div class="summary-title-v2">{_html.escape(uploaded_file.name)}</div>
                                <div class="summary-date-v2">업로드: {created_at_text}</div>
                            </div>
                        </div>

                        <div class="summary-section-v2">
                            <h3 class="summary-section-title-v2">요약 내용</h3>
                            <div class="summary-box-v2">
                                {summary_html}
                            </div>
                        </div>

                        <div class="summary-stats-v2">
                            <div class="stat-v2 blue">
                                <div class="stat-number-v2">{concept_cnt}</div>
                                <div class="stat-label-v2">주요 개념</div>
                            </div>
                            <div class="stat-v2 purple">
                                <div class="stat-number-v2">{keyword_cnt}</div>
                                <div class="stat-label-v2">참고 자료</div>
                            </div>
                            <div class="stat-v2 pink">
                                <div class="stat-number-v2">{review_time}</div>
                                <div class="stat-label-v2">예상 복습 시간</div>
                            </div>
                        </div>

                        <div class="summary-keywords-v2">
                            <h4 class="summary-keywords-title-v2">핵심 키워드</h4>
                            <div class="keyword-list-v2">{kw_html}</div>
                        </div>

                    </div>
                    """

                    st.components.v1.html(card_html, height=1200, scrolling=True)

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