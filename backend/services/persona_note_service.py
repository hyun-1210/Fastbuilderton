"""
페르소나 노트 관련 비즈니스 로직 서비스
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from typing import List, Optional
import uuid

from models import PersonaNote, Persona
from schemas import PersonaNoteCreate, PersonaNoteUpdate, PersonaNoteResponse


class PersonaNoteService:
    """페르소나 노트 CRUD 서비스"""

    @staticmethod
    async def create_persona_note(
        db: AsyncSession,
        note_data: PersonaNoteCreate
    ) -> PersonaNoteResponse:
        """
        새로운 페르소나 노트 생성
        
        Args:
            db: 데이터베이스 세션
            note_data: 생성할 노트 데이터
            
        Returns:
            생성된 노트 정보
            
        Raises:
            HTTPException: 페르소나를 찾을 수 없을 때
        """
        # 페르소나 존재 확인
        persona = await db.execute(
            select(Persona).where(Persona.id == note_data.persona_id)
        )
        if not persona.scalar_one_or_none():
            raise HTTPException(
                status_code=404,
                detail=f"페르소나를 찾을 수 없습니다. (ID: {note_data.persona_id})"
            )
        
        # 새 노트 인스턴스 생성
        new_note = PersonaNote(
            id=str(uuid.uuid4()),
            persona_id=note_data.persona_id,
            type=note_data.type,
            content=note_data.content
        )
        
        db.add(new_note)
        await db.commit()
        await db.refresh(new_note)
        
        return PersonaNoteResponse.model_validate(new_note)

    @staticmethod
    async def get_persona_note_by_id(
        db: AsyncSession,
        note_id: str
    ) -> PersonaNoteResponse:
        """
        ID로 페르소나 노트 조회
        
        Args:
            db: 데이터베이스 세션
            note_id: 조회할 노트 ID
            
        Returns:
            노트 정보
            
        Raises:
            HTTPException: 노트를 찾을 수 없을 때
        """
        result = await db.execute(
            select(PersonaNote).where(PersonaNote.id == note_id)
        )
        note = result.scalar_one_or_none()
        
        if not note:
            raise HTTPException(
                status_code=404,
                detail=f"페르소나 노트를 찾을 수 없습니다. (ID: {note_id})"
            )
        
        return PersonaNoteResponse.model_validate(note)

    @staticmethod
    async def get_persona_notes_by_persona(
        db: AsyncSession,
        persona_id: str
    ) -> List[PersonaNoteResponse]:
        """
        특정 페르소나의 모든 노트 조회
        
        Args:
            db: 데이터베이스 세션
            persona_id: 페르소나 ID
            
        Returns:
            노트 목록 (최신순 정렬)
        """
        query = (
            select(PersonaNote)
            .where(PersonaNote.persona_id == persona_id)
            .order_by(PersonaNote.created_at.desc())
        )
        
        result = await db.execute(query)
        notes = result.scalars().all()
        
        return [PersonaNoteResponse.model_validate(note) for note in notes]

    @staticmethod
    async def update_persona_note(
        db: AsyncSession,
        note_id: str,
        note_data: PersonaNoteUpdate
    ) -> PersonaNoteResponse:
        """
        페르소나 노트 정보 업데이트
        
        Args:
            db: 데이터베이스 세션
            note_id: 업데이트할 노트 ID
            note_data: 업데이트할 데이터 (선택적 필드만)
            
        Returns:
            업데이트된 노트 정보
            
        Raises:
            HTTPException: 노트를 찾을 수 없을 때
        """
        result = await db.execute(
            select(PersonaNote).where(PersonaNote.id == note_id)
        )
        note = result.scalar_one_or_none()
        
        if not note:
            raise HTTPException(
                status_code=404,
                detail=f"페르소나 노트를 찾을 수 없습니다. (ID: {note_id})"
            )
        
        # 제공된 필드만 업데이트
        update_data = note_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(note, field, value)
        
        await db.commit()
        await db.refresh(note)
        
        return PersonaNoteResponse.model_validate(note)

    @staticmethod
    async def delete_persona_note(
        db: AsyncSession,
        note_id: str
    ) -> bool:
        """
        페르소나 노트 삭제
        
        Args:
            db: 데이터베이스 세션
            note_id: 삭제할 노트 ID
            
        Returns:
            삭제 성공 여부
            
        Raises:
            HTTPException: 노트를 찾을 수 없을 때
        """
        result = await db.execute(
            select(PersonaNote).where(PersonaNote.id == note_id)
        )
        note = result.scalar_one_or_none()
        
        if not note:
            raise HTTPException(
                status_code=404,
                detail=f"페르소나 노트를 찾을 수 없습니다. (ID: {note_id})"
            )
        
        await db.delete(note)
        await db.commit()
        
        return True

