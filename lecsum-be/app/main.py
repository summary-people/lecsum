from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.database import engine, Base
from app.routers import summarize_router, quiz_router, chatbot_router

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI(
    title="LecSum Backend API",
    description="강의 자료(PDF/PPT) 요약 및 키워드 추출 API",
    version="0.1.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 운영 환경에서는 도메인 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(summarize_router.router)
app.include_router(quiz_router.router)
app.include_router(chatbot_router.router)

# HTTP 예외 처리
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "message": exc.detail,
            "data": None,
        },
    )

# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "message": f"서버 내부 오류: {str(exc)}",
            "data": None,
        },
    )