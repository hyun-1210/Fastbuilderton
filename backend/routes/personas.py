"""
페르소나 관련 API 라우터
HTTP 요청/응답만 처리하고, 실제 비즈니스 로직은 서비스 레이어에 위임
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db
from schemas import PersonaCreate, PersonaUpdate, PersonaResponse
from services.persona_service import PersonaService
from utils.dependencies import get_current_user
from models import User

router = APIRouter()


@router.post("/", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def create_persona(
    persona_data: PersonaCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    새로운 페르소나 생성
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    
    - **name**: 표시 이름 (예: "우리 엄마")
    - **phone_number**: 연락처 (필수)
    - **category_id**: 카테고리 ID (필수)
    - **birth_date**: 생일 (필수)
    - **anniversary_date**: 기념일 (필수)
    - **importance_weight**: 중요도 가중치 (0~100, 기본값: 50)
    - **relationship_temp**: 관계 온도 (0~100도, 기본값: 50.0)
    """
    return await PersonaService.create_persona(db, persona_data, current_user.id)


@router.get("/", response_model=List[PersonaResponse])
async def get_personas(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    현재 로그인한 사용자의 모든 페르소나 조회
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    생성일 기준 내림차순으로 정렬됩니다.
    """
    return await PersonaService.get_personas_by_user(db, current_user.id)


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    특정 페르소나 상세 조회
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 페르소나만 조회할 수 있습니다.
    
    - **persona_id**: 조회할 페르소나 ID
    """
    return await PersonaService.get_persona_by_id(db, persona_id, current_user.id)


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: str,
    persona_data: PersonaUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    페르소나 정보 업데이트
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 페르소나만 수정할 수 있습니다.
    
    - **persona_id**: 업데이트할 페르소나 ID
    - 모든 필드는 선택적입니다. 제공된 필드만 업데이트됩니다.
    """
    return await PersonaService.update_persona(db, persona_id, persona_data, current_user.id)


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_persona(
    persona_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    페르소나 삭제
    
    JWT 토큰에서 자동으로 사용자 ID를 가져옵니다.
    자신의 페르소나만 삭제할 수 있습니다.
    
    - **persona_id**: 삭제할 페르소나 ID
    - 관련된 모든 상호작용 로그, 메모 등도 함께 삭제됩니다 (CASCADE).
    """
    await PersonaService.delete_persona(db, persona_id, current_user.id)
    return None

