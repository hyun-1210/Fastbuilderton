"""
데이터베이스 연결 설정
SQLite를 사용하며, 필요시 PostgreSQL로 쉽게 전환 가능하도록 구성
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# 데이터베이스 URL (환경 변수에서 가져오거나 기본값 사용)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./app.db"  # SQLite 기본값
)

# 비동기 엔진 생성
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL 쿼리 로깅 (개발 환경용)
    future=True
)

# 세션 팩토리 생성
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base 클래스 (모든 모델이 상속받을 클래스)
Base = declarative_base()


async def get_db():
    """
    의존성 주입용 DB 세션 생성기
    FastAPI 라우터에서 사용: async def route(db: AsyncSession = Depends(get_db))
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    데이터베이스 초기화 (테이블 생성)
    앱 시작 시 한 번 호출
    """
    async with engine.begin() as conn:
        # 모든 테이블 생성
        await conn.run_sync(Base.metadata.create_all)

