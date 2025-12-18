import streamlit as st

st.set_page_config(
    page_title="강의 요약 시스템",
    page_icon="📚",
    layout="wide"
)

st.title("📚 강의 요약 시스템")
st.markdown("""
### 환영합니다!

이 시스템은 강의 자료를 업로드하고 다양한 기능을 사용할 수 있습니다:

- **📄 업로드**: PDF 강의 자료 업로드
- **💬 챗봇**: 강의 자료 기반 Q&A
- **📝 요약**: 강의 내용 요약
- **🔍 검색**: 키워드 검색
- **📝 시험**: 문제 생성 및 풀이

왼쪽 사이드바에서 원하는 페이지를 선택하세요!
""")