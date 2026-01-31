"""
사용자 관련 API 라우터
CRUD 기능 (인증 필요)
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import UserResponse, UserUpdate
from services.user_service import UserService
from utils.dependencies import get_current_user
from models import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    현재 로그인한 사용자 정보 조회
    
    JWT 토큰에서 사용자 정보를 가져옵니다.
    """
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    특정 사용자 정보 조회
    
    - **user_id**: 조회할 사용자 ID
    """
    return await UserService.get_user_by_id(db, user_id)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    현재 로그인한 사용자 정보 업데이트
    
    - **profile_image**: 프로필 이미지 URL (선택)
    - **timezone**: 시간대 (선택)
    """
    return await UserService.update_user(db, current_user.id, user_data)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    현재 로그인한 사용자 계정 삭제
    
    ⚠️ **주의**: 계정 삭제 시 모든 페르소나, 카테고리, 상호작용 로그 등이 함께 삭제됩니다 (CASCADE).
    """
    await UserService.delete_user(db, current_user.id)
    return None

