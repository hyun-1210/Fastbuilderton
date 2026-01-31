"""
SQLAlchemy 데이터베이스 모델 정의
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from enum import Enum
from database import Base


# Enum 타입 정의
class OAuthProvider(str, Enum):
    """소셜 로그인 제공자"""
    EMAIL = "email"  # 로컬 로그인
    KAKAO = "kakao"
    GOOGLE = "google"
    APPLE = "apple"


class PersonaCategory(str, Enum):
    """페르소나 관계 유형"""
    FAMILY = "Family"
    PARTNER = "Partner"
    WORK = "Work"
    FRIEND = "Friend"
    OTHER = "Other"


class InteractionType(str, Enum):
    """상호작용 유형"""
    CALL = "Call"
    MESSAGE = "Message"
    MEETING = "Meeting"
    NOTE = "Note"


class InteractionDirection(str, Enum):
    """상호작용 방향"""
    INBOUND = "Inbound"  # 받음
    OUTBOUND = "Outbound"  # 내가 함


class NoteType(str, Enum):
    """노트 유형"""
    MEMO = "Memo"
    QUESTION = "Question"


class NotificationType(str, Enum):
    """알림 유형"""
    REMINDER = "Reminder"
    RISK = "Risk"
    ACTION = "Action"


class User(Base):
    """사용자 정보 테이블. 한 사용자(User)가 여러 Category를 갖고, 각 Category에 여러 Persona가 연결됩니다."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)  # 로컬 로그인용 (소셜 로그인은 null)
    oauth_provider = Column(SQLEnum(OAuthProvider), nullable=False)
    oauth_id = Column(String, nullable=True)  # 소셜 로그인 제공자의 사용자 ID
    profile_image = Column(String, nullable=True)  # URL
    timezone = Column(String, default="Asia/Seoul", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # 사용자 소유: 카테고리 목록(가족/직장/친구 등) 및 각 카테고리 내 페르소나
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    personas = relationship("Persona", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    """카테고리 테이블. User에 연결되며, 해당 카테고리(가족/직장/친구 등) 안에 여러 Persona가 속합니다."""
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)  # 카테고리 이름 (예: "가족", "직장", "친구")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # 소유 사용자 + 이 카테고리 안의 페르소나들 (홈 라다 차트의 “축” 하나에 해당)
    user = relationship("User", back_populates="categories")
    personas = relationship("Persona", back_populates="category", cascade="all, delete-orphan")


class Persona(Base):
    """페르소나 (관리 대상 인물) 테이블. User와 Category에 연결되며, 홈 라다 차트의 한 “축” 안의 인물입니다."""
    __tablename__ = "personas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(String, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)  # 필수
    birth_date = Column(DateTime, nullable=False)  # 필수
    anniversary_date = Column(DateTime, nullable=False)  # 필수
    importance_weight = Column(Integer, default=50, nullable=False)  # 0~100
    relationship_temp = Column(Float, default=50.0, nullable=False)  # 0~100도, AI 계산 (라다 점수)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # 소유 사용자 + 소속 카테고리 (User → Category → Persona 연결)
    user = relationship("User", back_populates="personas")
    category = relationship("Category", back_populates="personas")
    interaction_logs = relationship("InteractionLog", back_populates="persona", cascade="all, delete-orphan")
    persona_profiles = relationship("PersonaProfile", back_populates="persona", cascade="all, delete-orphan")
    persona_notes = relationship("PersonaNote", back_populates="persona", cascade="all, delete-orphan")
    notification_logs = relationship("NotificationLog", back_populates="persona", cascade="all, delete-orphan")


class InteractionLog(Base):
    """상호작용 기록 테이블"""
    __tablename__ = "interaction_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    persona_id = Column(String, ForeignKey("personas.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SQLEnum(InteractionType), nullable=False)
    direction = Column(SQLEnum(InteractionDirection), nullable=False)  # 핵심: 능동적 노력 점수 계산용
    timestamp = Column(DateTime, nullable=False, index=True)
    duration = Column(Integer, nullable=True)  # 초 단위 (통화/만남일 때만)
    sentiment_score = Column(Float, nullable=True)  # -1.0 ~ +1.0
    summary_text = Column(Text, nullable=True)  # 대화 내용 3줄 요약
    raw_vector_id = Column(String, nullable=True)  # Vector DB에 저장된 원본 ID

    # 관계
    persona = relationship("Persona", back_populates="interaction_logs")


class PersonaProfile(Base):
    """AI 분석 성향 테이블"""
    __tablename__ = "persona_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    persona_id = Column(String, ForeignKey("personas.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    character = Column(Text, nullable=True)  # AI가 추정한 성격
    communication_style = Column(Text, nullable=True)  # 대화 스타일 태그 (예: "용건만 간단히, 감성적, 장문 선호")
    sensitive_topics = Column(Text, nullable=True)  # JSON 형태 (예: ["취업", "정치", "결혼"])

    # 관계
    persona = relationship("Persona", back_populates="persona_profiles")


class PersonaNote(Base):
    """메모 및 질문 테이블"""
    __tablename__ = "persona_notes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    persona_id = Column(String, ForeignKey("personas.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SQLEnum(NoteType), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # 관계
    persona = relationship("Persona", back_populates="persona_notes")


class NotificationLog(Base):
    """알림 및 리스크 로그 테이블"""
    __tablename__ = "notification_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    persona_id = Column(String, ForeignKey("personas.id", ondelete="CASCADE"), nullable=True, index=True)
    # user_id도 참조 가능 (persona_id가 null일 수 있음)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    type = Column(SQLEnum(NotificationType), nullable=False)
    content = Column(Text, nullable=False)  # 알림 메시지 본문
    sent_at = Column(DateTime, server_default=func.now(), nullable=False)
    action_taken = Column(Boolean, default=False, nullable=False)  # 사용자가 실제 행동을 취했는지 여부

    # 관계
    persona = relationship("Persona", back_populates="notification_logs")

