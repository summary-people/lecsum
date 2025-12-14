# FastAPI 엔트리포인트

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.db.database import engine, Base
from app.routers import upload_router, quiz_router

import os
from dotenv import load_dotenv
load_dotenv()
import openai

Base.metadata.create_all(bind=engine)
app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

app.include_router(upload_router.router)
app.include_router(quiz_router.router)

# 전역 예외 처리
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

# 500 에러 처리
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