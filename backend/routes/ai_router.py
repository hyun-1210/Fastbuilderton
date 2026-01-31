"""
NVIDIA NIM API를 호출하는 라우터
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

router = APIRouter()


class AIRequest(BaseModel):
    """AI 요청 모델"""
    prompt: str
    max_tokens: int = 100


class AIResponse(BaseModel):
    """AI 응답 모델"""
    response: str
    model: str


@router.post("/chat", response_model=AIResponse)
async def chat_with_nim(request: AIRequest):
    """
    NVIDIA NIM API를 호출하는 더미 엔드포인트
    
    실제 구현 시:
    1. services/nim_service.py에서 실제 API 호출 로직 구현
    2. openai 라이브러리를 사용하여 NVIDIA NIM 엔드포인트에 연결
    """
    try:
        api_key = os.getenv("NVIDIA_API_KEY")
        
        if not api_key:
            # API 키가 없어도 더미 응답 반환 (개발용)
            return AIResponse(
                response=f"[더미 응답] 입력된 프롬프트: {request.prompt}",
                model="nvidia-nim-dummy"
            )
        
        # TODO: 실제 NVIDIA NIM API 호출 구현
        # from services.nim_service import call_nim_api
        # response = await call_nim_api(request.prompt, request.max_tokens)
        
        # 현재는 더미 응답 반환
        return AIResponse(
            response=f"[더미 응답] 입력된 프롬프트: {request.prompt}",
            model="nvidia-nim-dummy"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI API 호출 중 오류 발생: {str(e)}"
        )


@router.get("/test")
async def test_endpoint():
    """테스트용 엔드포인트"""
    return {
        "message": "AI Router is working!",
        "status": "ok"
    }

