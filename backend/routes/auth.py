"""
인증 관련 API 라우터
회원가입, 로그인, 소셜 로그인 등
"""
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import UserRegister, UserLogin, SocialLogin, Token
from services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    로컬 회원가입 (이메일 + 비밀번호)
    
    - **email**: 이메일 주소 (필수, 고유)
    - **password**: 비밀번호 (필수)
    - **timezone**: 시간대 (선택, 기본값: Asia/Seoul)
    
    회원가입 성공 시 JWT 토큰이 반환됩니다.
    """
    try:
        return await UserService.register_user(db, user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 중 오류 발생: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    로컬 로그인 (이메일 + 비밀번호)
    
    - **email**: 이메일 주소
    - **password**: 비밀번호
    
    로그인 성공 시 JWT 토큰이 반환됩니다.
    """
    return await UserService.login_user(db, login_data)


@router.post("/social", response_model=Token)
async def social_login(
    social_data: SocialLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    소셜 로그인 (Kakao, Google, Apple)
    
    - **email**: 이메일 주소
    - **oauth_provider**: 소셜 로그인 제공자 (kakao, google, apple)
    - **oauth_id**: 소셜 로그인 제공자의 사용자 ID
    - **profile_image**: 프로필 이미지 URL (선택)
    - **timezone**: 시간대 (선택, 기본값: Asia/Seoul)
    
    기존 사용자면 정보를 업데이트하고, 신규 사용자면 생성합니다.
    로그인 성공 시 JWT 토큰이 반환됩니다.
    """
    return await UserService.social_login(db, social_data)

