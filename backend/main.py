"""
FastAPI 애플리케이션 진입점
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes import ai_router, personas, categories, interaction_logs, auth, users, persona_notes
from database import init_db

# 모델을 로드해 Base.metadata에 테이블이 등록된 뒤 init_db()가 실행되도록 함
import models  # noqa: F401, E402

# 앱 시작/종료 시 실행할 함수
@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 시 DB 초기화, 종료 시 정리"""
    try:
        await init_db()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"DB 초기화 실패: {e}") from e
    yield
    # 종료 시 (필요시 정리 작업)


# FastAPI 앱 생성
app = FastAPI(
    title="FastAPI Backend",
    description="해커톤 프로젝트 백엔드 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 미들웨어 설정 (React Native 앱 접속 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용 (개발 환경용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 라우터 등록
app.include_router(ai_router.router, prefix="/api/ai", tags=["AI"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(personas.router, prefix="/api/personas", tags=["Personas"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(interaction_logs.router, prefix="/api/interaction-logs", tags=["InteractionLogs"])
app.include_router(persona_notes.router, prefix="/api/persona-notes", tags=["PersonaNotes"])


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "FastAPI Backend is running!", "status": "ok"}


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}

