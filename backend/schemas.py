"""
Pydantic V2 스키마 정의
API 요청/응답 검증 및 직렬화에 사용
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enum 타입 (모델과 동일)
class OAuthProvider(str, Enum):
    EMAIL = "email"  # 로컬 로그인
    KAKAO = "kakao"
    GOOGLE = "google"
    APPLE = "apple"


class PersonaCategory(str, Enum):
    FAMILY = "Family"
    PARTNER = "Partner"
    WORK = "Work"
    FRIEND = "Friend"
    OTHER = "Other"


class InteractionType(str, Enum):
    CALL = "Call"
    MESSAGE = "Message"
    MEETING = "Meeting"
    NOTE = "Note"


class InteractionDirection(str, Enum):
    INBOUND = "Inbound"
    OUTBOUND = "Outbound"


class NoteType(str, Enum):
    MEMO = "Memo"
    QUESTION = "Question"


class NotificationType(str, Enum):
    REMINDER = "Reminder"
    RISK = "Risk"
    ACTION = "Action"


# ========== Users 스키마 ==========
class UserBase(BaseModel):
    """사용자 기본 스키마"""
    email: str
    profile_image: Optional[str] = None
    timezone: str = "Asia/Seoul"


class UserRegister(BaseModel):
    """로컬 회원가입 요청"""
    email: str
    password: str
    timezone: str = "Asia/Seoul"


class UserLogin(BaseModel):
    """로컬 로그인 요청"""
    email: str
    password: str


class SocialLogin(BaseModel):
    """소셜 로그인 요청"""
    email: str
    oauth_provider: OAuthProvider
    oauth_id: str  # 소셜 로그인 제공자의 사용자 ID
    profile_image: Optional[str] = None
    timezone: str = "Asia/Seoul"


class Token(BaseModel):
    """JWT 토큰 응답"""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserCreate(UserBase):
    """사용자 생성 요청 (내부용)"""
    oauth_provider: OAuthProvider
    password_hash: Optional[str] = None
    oauth_id: Optional[str] = None


class UserUpdate(BaseModel):
    """사용자 정보 업데이트 요청"""
    profile_image: Optional[str] = None
    timezone: Optional[str] = None


class UserResponse(UserBase):
    """사용자 응답"""
    id: str
    oauth_provider: OAuthProvider
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== Categories 스키마 ==========
class CategoryBase(BaseModel):
    """카테고리 기본 스키마"""
    name: str


class CategoryCreate(CategoryBase):
    """카테고리 생성 요청"""
    pass


class CategoryUpdate(BaseModel):
    """카테고리 업데이트 요청"""
    name: Optional[str] = None


class CategoryResponse(CategoryBase):
    """카테고리 응답"""
    id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== Personas 스키마 ==========
class PersonaBase(BaseModel):
    """페르소나 기본 스키마"""
    name: str
    phone_number: str
    category_id: str  # 카테고리 ID
    birth_date: datetime
    anniversary_date: datetime
    importance_weight: int = Field(default=50, ge=0, le=100)
    relationship_temp: float = Field(default=50.0, ge=0.0, le=100.0)


class PersonaCreate(PersonaBase):
    """페르소나 생성 요청"""
    pass


class PersonaUpdate(BaseModel):
    """페르소나 업데이트 요청 (모든 필드 선택적)"""
    name: Optional[str] = None
    phone_number: Optional[str] = None
    category_id: Optional[str] = None  # 카테고리 ID
    birth_date: Optional[datetime] = None
    anniversary_date: Optional[datetime] = None
    importance_weight: Optional[int] = Field(None, ge=0, le=100)
    relationship_temp: Optional[float] = Field(None, ge=0.0, le=100.0)


class PersonaResponse(PersonaBase):
    """페르소나 응답"""
    id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== InteractionLogs 스키마 ==========
class InteractionLogBase(BaseModel):
    """상호작용 로그 기본 스키마"""
    type: InteractionType
    direction: InteractionDirection
    timestamp: datetime
    duration: Optional[int] = None  # 초 단위
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    summary_text: Optional[str] = None
    raw_vector_id: Optional[str] = None


class InteractionLogCreate(InteractionLogBase):
    """상호작용 로그 생성 요청"""
    persona_id: str = Field(..., description="페르소나 ID (UUID 형식, 예: 23f68fa6-2a3d-4459-943a-556e868f20c5)")


class InteractionLogResponse(InteractionLogBase):
    """상호작용 로그 응답"""
    id: str
    persona_id: str

    model_config = ConfigDict(from_attributes=True)


# ========== PersonaProfiles 스키마 ==========
class PersonaProfileBase(BaseModel):
    """페르소나 프로필 기본 스키마"""
    character: Optional[str] = None
    communication_style: Optional[str] = None
    sensitive_topics: Optional[str] = None  # JSON 문자열로 저장


class PersonaProfileCreate(PersonaProfileBase):
    """페르소나 프로필 생성 요청"""
    persona_id: str


class PersonaProfileUpdate(PersonaProfileBase):
    """페르소나 프로필 업데이트 요청"""
    pass


class PersonaProfileResponse(PersonaProfileBase):
    """페르소나 프로필 응답"""
    id: str
    persona_id: str

    model_config = ConfigDict(from_attributes=True)


# ========== PersonaNotes 스키마 ==========
class PersonaNoteBase(BaseModel):
    """페르소나 노트 기본 스키마"""
    type: NoteType
    content: str


class PersonaNoteCreate(PersonaNoteBase):
    """페르소나 노트 생성 요청"""
    persona_id: str


class PersonaNoteUpdate(BaseModel):
    """페르소나 노트 업데이트 요청 (모든 필드 선택적)"""
    type: Optional[NoteType] = None
    content: Optional[str] = None


class PersonaNoteResponse(PersonaNoteBase):
    """페르소나 노트 응답"""
    id: str
    persona_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== NotificationLogs 스키마 ==========
class NotificationLogBase(BaseModel):
    """알림 로그 기본 스키마"""
    type: NotificationType
    content: str
    action_taken: bool = False


class NotificationLogCreate(NotificationLogBase):
    """알림 로그 생성 요청"""
    persona_id: Optional[str] = None
    user_id: Optional[str] = None


class NotificationLogResponse(NotificationLogBase):
    """알림 로그 응답"""
    id: str
    persona_id: Optional[str] = None
    user_id: Optional[str] = None
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== 복합 응답 스키마 ==========
class PersonaDetailResponse(PersonaResponse):
    """페르소나 상세 정보 (관계 데이터 포함)"""
    interaction_logs: List[InteractionLogResponse] = []
    persona_profiles: Optional[PersonaProfileResponse] = None
    persona_notes: List[PersonaNoteResponse] = []
    notification_logs: List[NotificationLogResponse] = []

    model_config = ConfigDict(from_attributes=True)

