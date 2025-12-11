# Lecture Summarize

## 🥔 NLP Lecture Summarize

> 업로드된 강의 자료(PDF/PPT)를 기반으로 핵심 내용을 자동 요약하는 AI 서비스  
> LLM 기반 강의 공부 멘토 챗봇 제공 (오픈소스 자료 추천 + 문서 기반 Q&A)  
> 파일 내용 기반으로 모의고사를 자동 생성하고 채점/해설까지 제공하는 학습 보조 도구

---

## 🎯 프로젝트의 목적(Purpose)

> AI를 활용해 학습자의 **강의 이해도 향상**, **개념 정리 자동화**, **학습 효율 최대화**를 지원  
> 강의 자료만 업로드하면 요약·설명·모의고사까지 자동 생성되는 All-in-One 학습 서비스
>
> 프로젝트 기간 : 2025/12/01 ~ 2025/12/22

---

## 🤩 팀원들(Team Members)

|                                     Lead/BE Developer                                    |                                               BE Developer                                               |                                       BE Developer                                      |                                     BE Developer                                    |
|:-------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------:|:--------------------------------------------------------------------------:|:------------------------------------------------------------------------------------:|
| [윤희준](https://github.com/uni-j-uni) | [박주용](https://github.com/imjuyongp) | [김종혁](https://github.com/kjh015) | [김준혁](https://github.com/nanchano0607) |
| <img src="https://avatars.githubusercontent.com/u/118972548?v=4" width="300" /> | <img src="https://avatars.githubusercontent.com/u/158154226?s=96&v=4" width="300" /> | <img src="https://avatars.githubusercontent.com/u/74913358?s=96&v=4" width="300" /> | <img src="https://avatars.githubusercontent.com/u/158154226?s=96&v=4" width="300" /> |

---

## 🛠️ 기술 스택(Tech)

### Backend

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-100000.svg?style=for-the-badge&logoColor=white)

### Frontend

![Streamlit](https://img.shields.io/badge/streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

### AI / LLM

![OpenAI](https://img.shields.io/badge/GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)

### 협업 툴 (Tools)

![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
![Notion](https://img.shields.io/badge/Notion-%23000000.svg?style=for-the-badge&logo=notion&logoColor=white)
![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)

---

## ⭐ 주요 기능

### 1) PDF/PPT 기반 강의 요약 기능

- 강의 자료 업로드 후 즉시 요약 생성
- 문서 Chunking + ChromaDB Embedding 저장
- LLM 기반 다단계 요약(Overview → 세부 요약 → 하이라이트)

### 2) 강의 공부 멘토(챗봇)

- 업로드 문서를 기반으로 한 RAG 기반 Q&A
- 학습자의 이해도에 따라 난이도 조절
- 외부 오픈소스 학습 자료 자동 추천
- 강의 내용 정리 / 질문 응답 / 개념 설명

### 3) 파일 내 내용 기반 모의고사 자동 생성 + 채점

- 강의 내용을 기반으로 5문제 자동 생성
- 빈칸 채우기, 단답형, 선택형 생성 가능
- 자동 채점 + 해설 생성
- 오답 노트 기능(후순위)

---

## GitHub Flow

![github-flow](https://i.ibb.co/p3Gfnvs/Kakao-Talk-20241115-230442579-01.png)

---

# 🎯 Branch Convention & Git Convention

## 🎯 Git Convention

- 🎉 **Start:** Start New Project [:tada:]
- ✨ **Feat:** 새로운 기능을 추가 [:sparkles:]
- 🐛 **Fix:** 버그 수정 [:bug:]
- 🎨 **Design:** CSS 등 사용자 UI 디자인 변경 [:art:]
- ♻️ **Refactor:** 코드 리팩토링 [:recycle:]
- 🔧 **Settings:** Changing configuration files [:wrench:]
- 🗃️ **Comment:** 필요한 주석 추가 및 변경 [:card_file_box:]
- ➕ **Dependency/Plugin:** Add a dependency/plugin [:heavy_plus_sign:]
- 📝 **Docs:** 문서 수정 [:memo:]
- 🔀 **Merge:** Merge branches [:twisted_rightwards_arrows:]
- 🚀 **Deploy:** Deploying stuff [:rocket:]
- 🚚 **Rename:** 파일 혹은 폴더명을 수정하거나 옮기는 작업만인 경우 [:truck:]
- 🔥 **Remove:** 파일을 삭제하는 작업만 수행한 경우 [:fire:]
- ⏪️ **Revert:** 전 버전으로 롤백 [:rewind:]

---

## 🪴 Branch Convention (GitHub Flow)

- `main`: 배포 가능한 브랜치, 항상 배포 가능한 상태 유지
- `develop`: 기능 개발 후 배포 전 테스트용 브랜치
- `feature/{description}`: 새로운 기능 개발용 브랜치
  - 예: `feature/lecture-summary`, `feature/mock-exam`, `feature/mentor-chat`

### Flow

1. `main` 브랜치에서 새로운 브랜치를 생성
2. 기능 개발 및 커밋
3. Pull Request 생성 후 팀원 리뷰
4. 승인되면 `main`에 merge
5. 필요 시 배포 진행

---
