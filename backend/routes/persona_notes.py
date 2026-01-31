"""
페르소나 노트 관련 API 라우터
HTTP 요청/응답만 처리하고, 실제 비즈니스 로직은 서비스 레이어에 위임
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from schemas import PersonaNoteCreate, PersonaNoteUpdate, PersonaNoteResponse
from services.persona_note_service import PersonaNoteService
from utils.dependencies import get_current_user
from models import User, Persona

router = APIRouter()


@router.post("/", response_model=PersonaNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_persona_note(
    note_data: PersonaNoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    새로운 페르소나 노트 생성
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 페르소나에만 노트를 생성할 수 있습니다.
    
    - **persona_id**: 대상 페르소나 ID (필수, 자신의 페르소나여야 함)
    - **type**: 노트 유형 (Memo=일반 메모, Question=관계 질문 답변)
    - **content**: 내용 텍스트
    """
    # 페르소나가 현재 사용자의 것인지 확인
    persona_result = await db.execute(
        select(Persona).where(Persona.id == note_data.persona_id)
    )
    persona = persona_result.scalar_one_or_none()
    
    if not persona:
        raise HTTPException(
            status_code=404,
            detail=f"페르소나를 찾을 수 없습니다. (ID: {note_data.persona_id})"
        )
    
    if persona.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="다른 사용자의 페르소나에는 노트를 생성할 수 없습니다."
        )
    
    return await PersonaNoteService.create_persona_note(db, note_data)


@router.get("/", response_model=List[PersonaNoteResponse])
async def get_persona_notes(
    persona_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    특정 페르소나의 모든 노트 조회
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 페르소나의 노트만 조회할 수 있습니다.
    
    - **persona_id**: 페르소나 ID (쿼리 파라미터)
    
    최신순으로 정렬됩니다.
    """
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
            detail="다른 사용자의 페르소나 노트는 조회할 수 없습니다."
        )
    
    return await PersonaNoteService.get_persona_notes_by_persona(db, persona_id)


@router.get("/{note_id}", response_model=PersonaNoteResponse)
async def get_persona_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    특정 페르소나 노트 상세 조회
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 페르소나의 노트만 조회할 수 있습니다.
    
    - **note_id**: 조회할 노트 ID
    """
    # 노트 조회
    note = await PersonaNoteService.get_persona_note_by_id(db, note_id)
    
    # 해당 노트의 페르소나가 현재 사용자의 것인지 확인
    persona_result = await db.execute(
        select(Persona).where(Persona.id == note.persona_id)
    )
    persona = persona_result.scalar_one_or_none()
    
    if persona and persona.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="다른 사용자의 페르소나 노트는 조회할 수 없습니다."
        )
    
    return note


@router.put("/{note_id}", response_model=PersonaNoteResponse)
async def update_persona_note(
    note_id: str,
    note_data: PersonaNoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    페르소나 노트 정보 업데이트
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 페르소나의 노트만 수정할 수 있습니다.
    
    - **note_id**: 업데이트할 노트 ID
    - **type**: 노트 유형 (선택적)
    - **content**: 내용 텍스트 (선택적)
    """
    # 노트 조회
    note = await PersonaNoteService.get_persona_note_by_id(db, note_id)
    
    # 해당 노트의 페르소나가 현재 사용자의 것인지 확인
    persona_result = await db.execute(
        select(Persona).where(Persona.id == note.persona_id)
    )
    persona = persona_result.scalar_one_or_none()
    
    if persona and persona.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="다른 사용자의 페르소나 노트는 수정할 수 없습니다."
        )
    
    return await PersonaNoteService.update_persona_note(db, note_id, note_data)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_persona_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    페르소나 노트 삭제
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 페르소나의 노트만 삭제할 수 있습니다.
    
    - **note_id**: 삭제할 노트 ID
    """
    # 노트 조회
    note = await PersonaNoteService.get_persona_note_by_id(db, note_id)
    
    # 해당 노트의 페르소나가 현재 사용자의 것인지 확인
    persona_result = await db.execute(
        select(Persona).where(Persona.id == note.persona_id)
    )
    persona = persona_result.scalar_one_or_none()
    
    if persona and persona.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="다른 사용자의 페르소나 노트는 삭제할 수 없습니다."
        )
    
    await PersonaNoteService.delete_persona_note(db, note_id)
    return None

