from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routers import candidates, uploads, evaluations, excel_import

app = FastAPI(title="후보 평가 시스템", description="CJ온스타일 온큐베이팅 지원자 심사 도구")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidates.router)
app.include_router(uploads.router)
app.include_router(evaluations.router)
app.include_router(excel_import.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "후보 평가 시스템"}
