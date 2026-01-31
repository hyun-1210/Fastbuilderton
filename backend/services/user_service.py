"""
사용자 관련 비즈니스 로직 서비스
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Optional
import uuid

from models import User
from schemas import UserRegister, UserLogin, SocialLogin, UserCreate, UserUpdate, UserResponse, Token, OAuthProvider
from utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token
)


class UserService:
    """사용자 CRUD 및 인증 서비스"""

    @staticmethod
    async def register_user(
        db: AsyncSession,
        user_data: UserRegister
    ) -> Token:
        """
        로컬 회원가입 (이메일 + 비밀번호)
        
        Args:
            db: 데이터베이스 세션
            user_data: 회원가입 데이터
            
        Returns:
            JWT 토큰 및 사용자 정보
            
        Raises:
            HTTPException: 이메일이 이미 존재하는 경우
        """
        # 이메일 중복 체크
        existing = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다."
            )
        
        # 새 사용자 생성
        new_user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            oauth_provider=OAuthProvider.EMAIL,  # 로컬 로그인은 EMAIL로 표시
            oauth_id=None,
            timezone=user_data.timezone
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": new_user.id})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(new_user)
        )

    @staticmethod
    async def login_user(
        db: AsyncSession,
        login_data: UserLogin
    ) -> Token:
        """
        로컬 로그인 (이메일 + 비밀번호)
        
        Args:
            db: 데이터베이스 세션
            login_data: 로그인 데이터
            
        Returns:
            JWT 토큰 및 사용자 정보
            
        Raises:
            HTTPException: 이메일 또는 비밀번호가 잘못된 경우
        """
        # 사용자 조회
        result = await db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 잘못되었습니다."
            )
        
        # 비밀번호 확인 (로컬 로그인만)
        if not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="소셜 로그인으로 가입된 계정입니다."
            )
        
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 잘못되었습니다."
            )
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": user.id})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    async def social_login(
        db: AsyncSession,
        social_data: SocialLogin
    ) -> Token:
        """
        소셜 로그인 (Kakao, Google, Apple)
        
        Args:
            db: 데이터베이스 세션
            social_data: 소셜 로그인 데이터
            
        Returns:
            JWT 토큰 및 사용자 정보
        """
        # 기존 사용자 조회 (이메일 또는 oauth_id로)
        result = await db.execute(
            select(User).where(
                (User.email == social_data.email) |
                (User.oauth_id == social_data.oauth_id)
            )
        )
        user = result.scalar_one_or_none()
        
        if user:
            # 기존 사용자: 정보 업데이트
            user.oauth_provider = social_data.oauth_provider
            user.oauth_id = social_data.oauth_id
            if social_data.profile_image:
                user.profile_image = social_data.profile_image
            user.timezone = social_data.timezone
        else:
            # 신규 사용자: 생성
            user = User(
                id=str(uuid.uuid4()),
                email=social_data.email,
                password_hash=None,  # 소셜 로그인은 비밀번호 없음
                oauth_provider=social_data.oauth_provider,
                oauth_id=social_data.oauth_id,
                profile_image=social_data.profile_image,
                timezone=social_data.timezone
            )
            db.add(user)
        
        await db.commit()
        await db.refresh(user)
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": user.id})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: str
    ) -> UserResponse:
        """
        ID로 사용자 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            사용자 정보
            
        Raises:
            HTTPException: 사용자를 찾을 수 없을 때
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"사용자를 찾을 수 없습니다. (ID: {user_id})"
            )
        
        return UserResponse.model_validate(user)

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: str,
        user_data: UserUpdate
    ) -> UserResponse:
        """
        사용자 정보 업데이트
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            user_data: 업데이트할 데이터
            
        Returns:
            업데이트된 사용자 정보
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"사용자를 찾을 수 없습니다. (ID: {user_id})"
            )
        
        # 제공된 필드만 업데이트
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        return UserResponse.model_validate(user)

    @staticmethod
    async def delete_user(
        db: AsyncSession,
        user_id: str
    ) -> bool:
        """
        사용자 삭제
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            삭제 성공 여부
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"사용자를 찾을 수 없습니다. (ID: {user_id})"
            )
        
        await db.delete(user)
        await db.commit()
        
        return True

