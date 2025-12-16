from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

from app.db.database import engine, Base
from app.routers import upload_router, quiz_router, chatbot_router

# 환경변수 로드
load_dotenv()

# OPENAI API KEY 검증
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI(
    title="LecSum Backend API",
    description="강의 요약 및 퀴즈 생성 API",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(upload_router.router)
app.include_router(quiz_router.router)
app.include_router(chatbot_router.router)

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

# HTTP 예외 처리
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "message": exc.detail,
            "data": None
        }
    )

# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "message": f"서버 내부 오류: {str(exc)}",
            "data": None
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
