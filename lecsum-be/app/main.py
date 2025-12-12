# FastAPI 엔트리포인트

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from db.database import engine, Base
from routers import upload_router, quiz_router

import os
from dotenv import load_dotenv
load_dotenv()
import openai

Base.metadata.create_all(bind=engine)
app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

app.include_router(upload_router.router)
app.include_router(quiz_router.router)

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