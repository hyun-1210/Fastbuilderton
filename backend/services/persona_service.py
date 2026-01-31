"""
페르소나 관련 비즈니스 로직 서비스
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from typing import List, Optional
import uuid
from datetime import datetime

from models import Persona
from schemas import PersonaCreate, PersonaUpdate, PersonaResponse


class PersonaService:
    """페르소나 CRUD 서비스"""

    @staticmethod
    async def create_persona(
        db: AsyncSession,
        persona_data: PersonaCreate,
        user_id: str
    ) -> PersonaResponse:
        """
        새로운 페르소나 생성
        
        Args:
            db: 데이터베이스 세션
            persona_data: 생성할 페르소나 데이터
            user_id: 소유자 사용자 ID
            
        Returns:
            생성된 페르소나 정보
        """
        # 새 페르소나 인스턴스 생성
        new_persona = Persona(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=persona_data.name,
            phone_number=persona_data.phone_number,
            category_id=persona_data.category_id,
            birth_date=persona_data.birth_date,
            anniversary_date=persona_data.anniversary_date,
            importance_weight=persona_data.importance_weight,
            relationship_temp=persona_data.relationship_temp
        )
        
        db.add(new_persona)
        await db.commit()
        await db.refresh(new_persona)
        
        return PersonaResponse.model_validate(new_persona)

    @staticmethod
    async def get_persona_by_id(
        db: AsyncSession,
        persona_id: str,
        user_id: Optional[str] = None
    ) -> PersonaResponse:
        """
        ID로 페르소나 조회
        
        Args:
            db: 데이터베이스 세션
            persona_id: 조회할 페르소나 ID
            user_id: 소유자 확인용 (선택적)
            
        Returns:
            페르소나 정보
            
        Raises:
            HTTPException: 페르소나를 찾을 수 없거나 권한이 없을 때
        """
        query = select(Persona).where(Persona.id == persona_id)
        
        # user_id가 제공되면 소유자 확인
        if user_id:
            query = query.where(Persona.user_id == user_id)
        
        result = await db.execute(query)
        persona = result.scalar_one_or_none()
        
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"페르소나를 찾을 수 없습니다. (ID: {persona_id})"
            )
        
        return PersonaResponse.model_validate(persona)

    @staticmethod
    async def get_personas_by_user(
        db: AsyncSession,
        user_id: str
    ) -> List[PersonaResponse]:
        """
        사용자의 모든 페르소나 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            페르소나 목록
        """
        query = select(Persona).where(Persona.user_id == user_id).order_by(Persona.created_at.desc())
        result = await db.execute(query)
        personas = result.scalars().all()
        
        return [PersonaResponse.model_validate(p) for p in personas]

    @staticmethod
    async def update_persona(
        db: AsyncSession,
        persona_id: str,
        persona_data: PersonaUpdate,
        user_id: Optional[str] = None
    ) -> PersonaResponse:
        """
        페르소나 정보 업데이트
        
        Args:
            db: 데이터베이스 세션
            persona_id: 업데이트할 페르소나 ID
            persona_data: 업데이트할 데이터 (선택적 필드만)
            user_id: 소유자 확인용 (선택적)
            
        Returns:
            업데이트된 페르소나 정보
            
        Raises:
            HTTPException: 페르소나를 찾을 수 없거나 권한이 없을 때
        """
        query = select(Persona).where(Persona.id == persona_id)
        
        if user_id:
            query = query.where(Persona.user_id == user_id)
        
        result = await db.execute(query)
        persona = result.scalar_one_or_none()
        
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"페르소나를 찾을 수 없습니다. (ID: {persona_id})"
            )
        
        # 제공된 필드만 업데이트
        update_data = persona_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(persona, field, value)
        
        await db.commit()
        await db.refresh(persona)
        
        return PersonaResponse.model_validate(persona)

    @staticmethod
    async def delete_persona(
        db: AsyncSession,
        persona_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        페르소나 삭제
        
        Args:
            db: 데이터베이스 세션
            persona_id: 삭제할 페르소나 ID
            user_id: 소유자 확인용 (선택적)
            
        Returns:
            삭제 성공 여부
            
        Raises:
            HTTPException: 페르소나를 찾을 수 없거나 권한이 없을 때
        """
        query = select(Persona).where(Persona.id == persona_id)
        
        if user_id:
            query = query.where(Persona.user_id == user_id)
        
        result = await db.execute(query)
        persona = result.scalar_one_or_none()
        
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"페르소나를 찾을 수 없습니다. (ID: {persona_id})"
            )
        
        await db.delete(persona)
        await db.commit()
        
        return True

