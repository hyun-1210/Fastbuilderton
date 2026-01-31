"""
카테고리 관련 비즈니스 로직 서비스
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from typing import List, Optional
import uuid

from models import Category
from schemas import CategoryCreate, CategoryUpdate, CategoryResponse


class CategoryService:
    """카테고리 CRUD 서비스"""

    @staticmethod
    async def create_category(
        db: AsyncSession,
        category_data: CategoryCreate,
        user_id: str
    ) -> CategoryResponse:
        """
        새로운 카테고리 생성
        
        Args:
            db: 데이터베이스 세션
            category_data: 생성할 카테고리 데이터
            user_id: 소유자 사용자 ID
            
        Returns:
            생성된 카테고리 정보
        """
        # 중복 체크 (같은 사용자의 같은 이름 카테고리)
        existing = await db.execute(
            select(Category).where(
                Category.user_id == user_id,
                Category.name == category_data.name
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"이미 존재하는 카테고리입니다: {category_data.name}"
            )
        
        # 새 카테고리 인스턴스 생성
        new_category = Category(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=category_data.name
        )
        
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        
        return CategoryResponse.model_validate(new_category)

    @staticmethod
    async def get_category_by_id(
        db: AsyncSession,
        category_id: str,
        user_id: Optional[str] = None
    ) -> CategoryResponse:
        """
        ID로 카테고리 조회
        
        Args:
            db: 데이터베이스 세션
            category_id: 조회할 카테고리 ID
            user_id: 소유자 확인용 (선택적)
            
        Returns:
            카테고리 정보
            
        Raises:
            HTTPException: 카테고리를 찾을 수 없거나 권한이 없을 때
        """
        query = select(Category).where(Category.id == category_id)
        
        if user_id:
            query = query.where(Category.user_id == user_id)
        
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"카테고리를 찾을 수 없습니다. (ID: {category_id})"
            )
        
        return CategoryResponse.model_validate(category)

    @staticmethod
    async def get_categories_by_user(
        db: AsyncSession,
        user_id: str
    ) -> List[CategoryResponse]:
        """
        사용자의 모든 카테고리 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            카테고리 목록
        """
        query = select(Category).where(Category.user_id == user_id).order_by(Category.created_at.desc())
        result = await db.execute(query)
        categories = result.scalars().all()
        
        return [CategoryResponse.model_validate(c) for c in categories]

    @staticmethod
    async def update_category(
        db: AsyncSession,
        category_id: str,
        category_data: CategoryUpdate,
        user_id: Optional[str] = None
    ) -> CategoryResponse:
        """
        카테고리 정보 업데이트
        
        카테고리 이름이 업데이트되면, 연결된 모든 페르소나의 카테고리도 자동으로 업데이트됩니다.
        (SQLAlchemy relationship을 통해 자동 처리)
        
        Args:
            db: 데이터베이스 세션
            category_id: 업데이트할 카테고리 ID
            category_data: 업데이트할 데이터 (선택적 필드만)
            user_id: 소유자 확인용 (선택적)
            
        Returns:
            업데이트된 카테고리 정보
            
        Raises:
            HTTPException: 카테고리를 찾을 수 없거나 권한이 없을 때
        """
        query = select(Category).where(Category.id == category_id)
        
        if user_id:
            query = query.where(Category.user_id == user_id)
        
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"카테고리를 찾을 수 없습니다. (ID: {category_id})"
            )
        
        # 이름 중복 체크 (다른 카테고리와 중복되지 않는지)
        if category_data.name and category_data.name != category.name:
            existing = await db.execute(
                select(Category).where(
                    Category.user_id == category.user_id,
                    Category.name == category_data.name,
                    Category.id != category_id
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail=f"이미 존재하는 카테고리입니다: {category_data.name}"
                )
        
        # 제공된 필드만 업데이트
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        await db.commit()
        await db.refresh(category)
        
        return CategoryResponse.model_validate(category)

    @staticmethod
    async def delete_category(
        db: AsyncSession,
        category_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        카테고리 삭제
        
        카테고리를 삭제하면, CASCADE 설정에 의해 연결된 모든 페르소나도 함께 삭제됩니다.
        
        Args:
            db: 데이터베이스 세션
            category_id: 삭제할 카테고리 ID
            user_id: 소유자 확인용 (선택적)
            
        Returns:
            삭제 성공 여부
            
        Raises:
            HTTPException: 카테고리를 찾을 수 없거나 권한이 없을 때
        """
        query = select(Category).where(Category.id == category_id)
        
        if user_id:
            query = query.where(Category.user_id == user_id)
        
        result = await db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"카테고리를 찾을 수 없습니다. (ID: {category_id})"
            )
        
        # CASCADE 삭제: 연결된 모든 페르소나도 함께 삭제됨
        await db.delete(category)
        await db.commit()
        
        return True

