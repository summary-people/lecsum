"""
FastAPI 애플리케이션 엔트리포인트
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="LecSum Backend API",
    description="강의 요약 및 멘토 챗봇 API",
    version="0.1.0"
)

# CORS 설정 (Streamlit 프론트엔드 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
from app.routers import chatbot_router, upload_router

app.include_router(chatbot_router.router)
app.include_router(upload_router.router)

# 루트 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "LecSum Backend API",
        "version": "0.1.0",
        "docs": "/docs"
    }

# 헬스체크
@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
