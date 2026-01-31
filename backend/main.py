"""
FastAPI 애플리케이션 진입점
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import ai_router

# FastAPI 앱 생성
app = FastAPI(
    title="FastAPI Backend",
    description="해커톤 프로젝트 백엔드 API",
    version="1.0.0"
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


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "FastAPI Backend is running!", "status": "ok"}


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}

