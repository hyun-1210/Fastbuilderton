"""
상호작용 로그 관련 API 라우터
HTTP 요청/응답만 처리하고, 실제 비즈니스 로직은 서비스 레이어에 위임
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from database import get_db
from schemas import InteractionLogCreate, InteractionLogResponse
from services.interaction_log_service import InteractionLogService
from utils.dependencies import get_current_user
from models import User, Persona, InteractionLog

router = APIRouter()


@router.post("/", response_model=InteractionLogResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction_log(
    log_data: InteractionLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    새로운 상호작용 로그 생성
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 페르소나에만 상호작용 로그를 생성할 수 있습니다.
    
    - **persona_id**: 대상 페르소나 ID (필수, 자신의 페르소나여야 함)
    - **type**: 활동 유형 (Call, Message, Meeting, Note)
    - **direction**: 행동의 방향 (Inbound=받음, Outbound=내가 함)
    - **timestamp**: 행동 발생 시간 (필수)
    - **duration**: 소요 시간 (초 단위, 통화나 만남일 때만)
    - **sentiment_score**: AI가 분석한 감정 점수 (-1.0 부정 ~ +1.0 긍정)
    - **summary_text**: 대화 내용 3줄 요약
    - **raw_vector_id**: Vector DB에 저장된 실제 대화 원본의 ID
    """
    # 페르소나가 현재 사용자의 것인지 확인
    persona_result = await db.execute(
        select(Persona).where(Persona.id == log_data.persona_id)
    )
    persona = persona_result.scalar_one_or_none()
    
    if not persona:
        # 사용자의 페르소나 목록을 가져와서 힌트 제공
        user_personas = await db.execute(
            select(Persona).where(Persona.user_id == current_user.id)
        )
        persona_list = user_personas.scalars().all()
        
        if persona_list:
            persona_ids = [p.id for p in persona_list]
            raise HTTPException(
                status_code=404,
                detail=f"페르소나를 찾을 수 없습니다. (ID: {log_data.persona_id})\n"
                       f"사용 가능한 페르소나 ID: {persona_ids[:5]}"  # 최대 5개만 표시
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"페르소나를 찾을 수 없습니다. (ID: {log_data.persona_id})\n"
                       f"먼저 페르소나를 생성해주세요. (/api/personas/ POST)"
            )
    
    if persona.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="다른 사용자의 페르소나에는 상호작용 로그를 생성할 수 없습니다."
        )
    
    return await InteractionLogService.create_interaction_log(db, log_data)


@router.get("/", response_model=List[InteractionLogResponse])
async def get_interaction_logs(
    persona_id: Optional[str] = Query(None, description="페르소나 ID (특정 페르소나의 로그만 조회, 선택적)"),
    limit: Optional[int] = Query(None, description="최대 조회 개수"),
    offset: int = Query(0, description="시작 위치 (페이지네이션)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    상호작용 로그 조회
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 페르소나의 로그만 조회할 수 있습니다.
    
    - **persona_id**: 페르소나 ID (선택적, 제공하면 해당 페르소나의 로그만 조회)
    - **limit**: 최대 조회 개수 (선택적)
    - **offset**: 시작 위치 (페이지네이션용, 기본값: 0)
    
    persona_id가 없으면 현재 사용자의 모든 페르소나 로그를 조회합니다.
    최신순으로 정렬됩니다.
    """
    if persona_id:
        # 페르소나가 현재 사용자의 것인지 확인
        persona_result = await db.execute(
            select(Persona).where(Persona.id == persona_id)
        )
        persona = persona_result.scalar_one_or_none()
        
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"페르소나를 찾을 수 없습니다. (ID: {persona_id})"
            )
        
        if persona.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="다른 사용자의 페르소나 로그는 조회할 수 없습니다."
            )
        
        return await InteractionLogService.get_interaction_logs_by_persona(
            db, persona_id, limit, offset
        )
    else:
        # 현재 사용자의 모든 페르소나 로그 조회
        return await InteractionLogService.get_interaction_logs_by_user(
            db, current_user.id, limit, offset
        )


@router.get("/{log_id}", response_model=InteractionLogResponse)
async def get_interaction_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    특정 상호작용 로그 상세 조회
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 페르소나의 로그만 조회할 수 있습니다.
    
    - **log_id**: 조회할 상호작용 로그 ID
    """
    # 로그 조회
    log = await InteractionLogService.get_interaction_log_by_id(db, log_id)
    
    # 해당 로그의 페르소나가 현재 사용자의 것인지 확인
    persona_result = await db.execute(
        select(Persona).where(Persona.id == log.persona_id)
    )
    persona = persona_result.scalar_one_or_none()
    
    if persona and persona.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="다른 사용자의 상호작용 로그는 조회할 수 없습니다."
        )
    
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interaction_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    상호작용 로그 삭제
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 페르소나의 로그만 삭제할 수 있습니다.
    
    - **log_id**: 삭제할 상호작용 로그 ID
    
    ⚠️ **참고**: 페르소나를 삭제하면 연결된 모든 상호작용 로그도 자동으로 삭제됩니다 (CASCADE).
    """
    # 로그 조회
    log_result = await db.execute(
        select(InteractionLog).where(InteractionLog.id == log_id)
    )
    log = log_result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(
            status_code=404,
            detail=f"상호작용 로그를 찾을 수 없습니다. (ID: {log_id})"
        )
    
    # 해당 로그의 페르소나가 현재 사용자의 것인지 확인
    persona_result = await db.execute(
        select(Persona).where(Persona.id == log.persona_id)
    )
    persona = persona_result.scalar_one_or_none()
    
    if persona and persona.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="다른 사용자의 상호작용 로그는 삭제할 수 없습니다."
        )
    
    await InteractionLogService.delete_interaction_log(db, log_id)
    return None

