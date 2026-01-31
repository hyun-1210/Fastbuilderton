"""
상호작용 로그 관련 비즈니스 로직 서비스
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException
from typing import List, Optional
import uuid
from datetime import datetime

from models import InteractionLog, Persona
from schemas import InteractionLogCreate, InteractionLogResponse


class InteractionLogService:
    """상호작용 로그 CRUD 서비스"""

    @staticmethod
    async def create_interaction_log(
        db: AsyncSession,
        log_data: InteractionLogCreate
    ) -> InteractionLogResponse:
        """
        새로운 상호작용 로그 생성
        
        Args:
            db: 데이터베이스 세션
            log_data: 생성할 상호작용 로그 데이터
            
        Returns:
            생성된 상호작용 로그 정보
            
        Raises:
            HTTPException: 페르소나를 찾을 수 없을 때
        """
        # 페르소나 존재 확인
        persona = await db.execute(
            select(Persona).where(Persona.id == log_data.persona_id)
        )
        if not persona.scalar_one_or_none():
            raise HTTPException(
                status_code=404,
                detail=f"페르소나를 찾을 수 없습니다. (ID: {log_data.persona_id})"
            )
        
        # 새 상호작용 로그 인스턴스 생성
        new_log = InteractionLog(
            id=str(uuid.uuid4()),
            persona_id=log_data.persona_id,
            type=log_data.type,
            direction=log_data.direction,
            timestamp=log_data.timestamp,
            duration=log_data.duration,
            sentiment_score=log_data.sentiment_score,
            summary_text=log_data.summary_text,
            raw_vector_id=log_data.raw_vector_id
        )
        
        db.add(new_log)
        await db.commit()
        await db.refresh(new_log)
        
        return InteractionLogResponse.model_validate(new_log)

    @staticmethod
    async def get_interaction_log_by_id(
        db: AsyncSession,
        log_id: str
    ) -> InteractionLogResponse:
        """
        ID로 상호작용 로그 조회
        
        Args:
            db: 데이터베이스 세션
            log_id: 조회할 상호작용 로그 ID
            
        Returns:
            상호작용 로그 정보
            
        Raises:
            HTTPException: 상호작용 로그를 찾을 수 없을 때
        """
        result = await db.execute(
            select(InteractionLog).where(InteractionLog.id == log_id)
        )
        log = result.scalar_one_or_none()
        
        if not log:
            raise HTTPException(
                status_code=404,
                detail=f"상호작용 로그를 찾을 수 없습니다. (ID: {log_id})"
            )
        
        return InteractionLogResponse.model_validate(log)

    @staticmethod
    async def get_interaction_logs_by_persona(
        db: AsyncSession,
        persona_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[InteractionLogResponse]:
        """
        특정 페르소나의 모든 상호작용 로그 조회
        
        Args:
            db: 데이터베이스 세션
            persona_id: 페르소나 ID
            limit: 최대 조회 개수 (선택적)
            offset: 시작 위치 (페이지네이션용)
            
        Returns:
            상호작용 로그 목록 (최신순 정렬)
        """
        query = (
            select(InteractionLog)
            .where(InteractionLog.persona_id == persona_id)
            .order_by(InteractionLog.timestamp.desc())
        )
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return [InteractionLogResponse.model_validate(log) for log in logs]

    @staticmethod
    async def get_interaction_logs_by_user(
        db: AsyncSession,
        user_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[InteractionLogResponse]:
        """
        사용자의 모든 페르소나에 대한 상호작용 로그 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            limit: 최대 조회 개수 (선택적)
            offset: 시작 위치 (페이지네이션용)
            
        Returns:
            상호작용 로그 목록 (최신순 정렬)
        """
        query = (
            select(InteractionLog)
            .join(Persona)
            .where(Persona.user_id == user_id)
            .order_by(InteractionLog.timestamp.desc())
        )
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return [InteractionLogResponse.model_validate(log) for log in logs]

    @staticmethod
    async def delete_interaction_log(
        db: AsyncSession,
        log_id: str
    ) -> bool:
        """
        상호작용 로그 삭제
        
        Args:
            db: 데이터베이스 세션
            log_id: 삭제할 상호작용 로그 ID
            
        Returns:
            삭제 성공 여부
            
        Raises:
            HTTPException: 상호작용 로그를 찾을 수 없을 때
        """
        result = await db.execute(
            select(InteractionLog).where(InteractionLog.id == log_id)
        )
        log = result.scalar_one_or_none()
        
        if not log:
            raise HTTPException(
                status_code=404,
                detail=f"상호작용 로그를 찾을 수 없습니다. (ID: {log_id})"
            )
        
        await db.delete(log)
        await db.commit()
        
        return True

