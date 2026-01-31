"""
FastAPI 의존성 함수들
인증, 권한 확인 등에 사용
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User
from utils.auth import decode_access_token

# HTTP Bearer 토큰 스키마 설정 (Swagger UI에서 사용하기 쉬움)
security = HTTPBearer(
    description="JWT 토큰을 입력하세요. 로그인/회원가입 후 받은 access_token을 입력하면 됩니다.",
    scheme_name="Bearer"
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    JWT 토큰에서 현재 사용자 정보 가져오기
    
    Args:
        credentials: HTTP Bearer 토큰 (Swagger UI에서 자동으로 처리)
        db: 데이터베이스 세션
        
    Returns:
        현재 사용자 객체
        
    Raises:
        HTTPException: 토큰이 유효하지 않거나 사용자를 찾을 수 없을 때
    """
    # Bearer 토큰에서 실제 토큰 추출
    token = credentials.credentials
    
    # 토큰 디코딩
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에 사용자 정보가 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 사용자 조회
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

