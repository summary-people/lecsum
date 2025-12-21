import streamlit as st
import os
from pages.upload import render_upload_page
from pages.quiz import render_quiz_page
from pages.summaries import render_summaries_page
from pages.wrong_answer import render_wrong_notes_page
from pages.chatbot import render_chatbot_page
from pages.quiz_result import render_quiz_result_page

page = st.query_params.get("page", "home")

st.set_page_config(
    page_title="Lecsum",
    page_icon="📘",
    layout="wide"
)

# CSS 주입 (외부 파일)
def inject_base_css():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(base_dir, "styles", "main.css")

    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_top_header():
    st.markdown(
        """
        <div class="top-header">
            <a class="header-logo" href="/?page=home">
                📘 Lecsum
            </a>
            <div class="header-nav">
                <a href="/?page=upload">문서 업로드</a>
                <a href="/?page=summaries">요약 문서</a>
                <a href="/?page=mentor">AI 멘토</a>
                <a href="/?page=quiz">AI 퀴즈</a>
                <a href="/?page=wrong-notes">오답노트</a>
                <a href="/?page=quiz-result">퀴즈 보관함</a>
            </div>
        </div>
        <div class="page-offset"></div>
        """,
        unsafe_allow_html=True
    )

def render_hero():
    st.markdown("<div class='main-title'>📖 Lecsum</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>강의 자료를 스마트하게 학습하세요</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='desc'>AI 기반 요약, 멘토링, 그리고 퀴즈로 효율적인 학습을 지원합니다</div>",
        unsafe_allow_html=True
    )

def render_cards():
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown(
            """
            <div class="card">
                <div class="card-icon">⬆️</div>
                <div class="card-title purple">문서 요약</div>
                <div class="card-desc">
                    PDF/PPT 파일을 업로드하면 AI가 자동으로 핵심 내용을 요약해드립니다.
                </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="card-action">', unsafe_allow_html=True)
        if st.button("시작하기 →", key="upload_button"):
            st.query_params.update(page="upload")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div class="card">
                <div class="card-icon">💬</div>
                <div class="card-title blue">AI 멘토</div>
                <div class="card-desc">
                    업로드한 문서를 기반으로 질문하고 답변을 받을 수 있습니다.
                </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="card-action">', unsafe_allow_html=True)
        if st.button("대화하기 →", key="mentor_button"):
            st.query_params.update(page="mentor")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown(
            """
            <div class="card">
                <div class="card-icon">📝</div>
                <div class="card-title pink">AI 퀴즈</div>
                <div class="card-desc">
                    문서 내용을 분석해 자동 생성된 문제로 학습 효과를 확인하세요.
                </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="card-action">', unsafe_allow_html=True)
        if st.button("문제 풀기 →", key="quiz_button"):
            st.query_params.update(page="quiz")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3, gap="large")

    with col4:
        st.markdown(
            '''
            <div class="card">
                <div class="card-icon">📚</div>
                <div class="card-title purple">요약 문서</div>
                <div class="card-desc">
                    지금까지 요약된 문서를 한눈에 확인하고 다시 학습할 수 있습니다.
                </div>
            ''',
            unsafe_allow_html=True
        )
        st.markdown('<div class="card-action">', unsafe_allow_html=True)
        if st.button("문서 보기 →", key="summaries_button"):
            st.query_params.update(page="summaries")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown(
            '''
            <div class="card">
                <div class="card-icon">📝</div>
                <div class="card-title pink">오답노트</div>
                <div class="card-desc">
                    틀린 문제를 모아 다시 학습하고 약점을 보완하세요.
                </div>
            ''',
            unsafe_allow_html=True
        )
        st.markdown('<div class="card-action">', unsafe_allow_html=True)
        if st.button("오답노트 →", key="wrong_notes_button"):
            st.query_params.update(page="wrong-notes")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col6:
        st.markdown(
            '''
            <div class="card">
                <div class="card-icon">🗄️</div>
                <div class="card-title pink">퀴즈 보관함</div>
                <div class="card-desc">
                    지금까지 생성된 퀴즈와 응시 기록을 한눈에 확인하고 관리하세요.
                </div>
            ''',
            unsafe_allow_html=True
        )
        st.markdown('<div class="card-action">', unsafe_allow_html=True)
        if st.button("기록 보기 →", key="quiz_result_button"):
            st.query_params.update(page="quiz-result")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    

def render_features():
    st.markdown(
        """
        <div class="feature-box">
            <h3>✨ 주요 기능</h3>
            <ul>
                <li><b>GPT-4o-mini 기반</b> — 정확하고 빠른 요약 및 분석</li>
                <li><b>다양한 파일 형식 지원</b> — PDF, PPT 등 주요 문서 형식</li>
                <li><b>자동 문제 생성</b> — 문서 기반 맞춤형 모의고사</li>
                <li><b>실시간 Q&A</b> — AI 멘토에게 바로 질문</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

inject_base_css()
render_top_header()

if page == "home":
    render_hero()
    render_cards()
    render_features()

elif page == "upload":
    render_upload_page()

elif page == "mentor":
    render_chatbot_page()

elif page == "quiz":
    render_quiz_page()

elif page == "summaries":
    render_summaries_page()

elif page == "wrong-notes":
    render_wrong_notes_page()

elif page == "quiz-result":
    render_quiz_result_page()