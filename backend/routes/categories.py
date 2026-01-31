"""
카테고리 관련 API 라우터
HTTP 요청/응답만 처리하고, 실제 비즈니스 로직은 서비스 레이어에 위임
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db
from schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from services.category_service import CategoryService
from utils.dependencies import get_current_user
from models import User

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    새로운 카테고리 생성
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    
    - **name**: 카테고리 이름 (예: "가족", "직장", "친구")
    - 같은 사용자의 중복된 이름은 허용되지 않습니다.
    """
    return await CategoryService.create_category(db, category_data, current_user.id)


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    현재 로그인한 사용자의 모든 카테고리 조회
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    생성일 기준 내림차순으로 정렬됩니다.
    """
    return await CategoryService.get_categories_by_user(db, current_user.id)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    특정 카테고리 상세 조회
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 카테고리만 조회할 수 있습니다.
    
    - **category_id**: 조회할 카테고리 ID
    """
    return await CategoryService.get_category_by_id(db, category_id, current_user.id)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    카테고리 정보 업데이트
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 카테고리만 수정할 수 있습니다.
    
    - **category_id**: 업데이트할 카테고리 ID
    - **name**: 새로운 카테고리 이름 (선택적)
    
    카테고리 이름이 업데이트되면, 연결된 모든 페르소나의 카테고리도 자동으로 업데이트됩니다.
    """
    return await CategoryService.update_category(db, category_id, category_data, current_user.id)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    카테고리 삭제
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 카테고리만 삭제할 수 있습니다.
    
    - **category_id**: 삭제할 카테고리 ID
    
    ⚠️ **주의**: 카테고리를 삭제하면, 연결된 모든 페르소나도 함께 삭제됩니다 (CASCADE).
    """
    await CategoryService.delete_category(db, category_id, current_user.id)
    return None

