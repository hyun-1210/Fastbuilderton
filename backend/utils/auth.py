"""
인증 관련 유틸리티 함수
JWT 토큰 생성/검증, 비밀번호 해싱 등
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7일


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시된 비밀번호 비교
    
    Args:
        plain_password: 사용자가 입력한 평문 비밀번호
        hashed_password: 데이터베이스에 저장된 해시된 비밀번호
        
    Returns:
        비밀번호 일치 여부
        
    Note:
        get_password_hash에서 72바이트 초과 시 SHA256으로 먼저 해시했으므로,
        검증 시에도 동일한 처리를 합니다.
    """
    try:
        # 원본 비밀번호로 먼저 시도
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            # 72바이트를 초과하면 SHA256으로 먼저 해시
            password = hashlib.sha256(password_bytes).hexdigest().encode('utf-8')
        else:
            password = password_bytes
        
        return bcrypt.checkpw(password, hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    비밀번호를 해시화
    
    Args:
        password: 평문 비밀번호
        
    Returns:
        해시된 비밀번호 (bcrypt 해시)
        
    Note:
        bcrypt는 72바이트를 초과하는 비밀번호를 처리할 수 없으므로,
        초과하는 경우 SHA256으로 먼저 해시한 후 bcrypt로 해시합니다.
    """
    # bcrypt는 72바이트를 초과하는 비밀번호를 처리할 수 없음
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # 72바이트를 초과하면 SHA256으로 먼저 해시 (항상 64자 hex 문자열 = 32바이트)
        password = hashlib.sha256(password_bytes).hexdigest()
        password_bytes = password.encode('utf-8')
    
    # bcrypt로 해시 (salt 자동 생성)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성
    
    Args:
        data: 토큰에 포함할 데이터 (예: {"sub": user_id})
        expires_delta: 만료 시간 (None이면 기본값 사용)
        
    Returns:
        JWT 토큰 문자열
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    JWT 토큰 디코딩 및 검증
    
    Args:
        token: JWT 토큰 문자열
        
    Returns:
        토큰 페이로드 (dict) 또는 None (유효하지 않은 경우)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

