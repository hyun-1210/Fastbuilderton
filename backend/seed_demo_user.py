"""
데모 계정 시드 스크립트.
models.py의 User, Category, Persona를 사용해 한 사용자에 카테고리와 페르소나를 연결합니다.
- User 1명 생성 → 그 User에 연결된 Category 5개 → 각 Category에 연결된 Persona 2명.

사용법: backend 폴더에서 실행
  python seed_demo_user.py

생성되는 계정:
  이메일: demo@anbu.app
  비밀번호: anbu2025

카테고리: 가족, 직장, 친구, 연인, 멘토 (각 2명의 페르소나, User와 Category에 연결)
"""
import asyncio
import uuid
from datetime import datetime

from database import init_db, AsyncSessionLocal
from models import User, Category, Persona
from utils.auth import get_password_hash
from schemas import OAuthProvider


DEMO_EMAIL = "demo@anbu.app"
DEMO_PASSWORD = "anbu2025"

# 카테고리 이름 → (페르소나 2명 이름, 각 관계온도)
# 관계온도는 현재 홈 라다와 비슷하게: 가족 74, 직장 58, 친구 61, 연인 42, 멘토 55
DEMO_CATEGORIES = [
    ("가족", [("엄마", 76), ("아빠", 72)]),
    ("직장", [("팀장님", 58), ("동료 지훈", 58)]),
    ("친구", [("민수", 62), ("수진", 60)]),
    ("연인", [("지은", 44), ("준호", 40)]),
    ("멘토", [("박교수님", 56), ("김선배", 54)]),
]

# 공통 생일/기념일 (필수 필드)
DEFAULT_BIRTH = datetime(1990, 6, 15)
DEFAULT_ANNIV = datetime(2020, 1, 1)
DEFAULT_PHONE = "010-0000-0000"


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        existing = await db.execute(select(User).where(User.email == DEMO_EMAIL))
        if existing.scalar_one_or_none():
            print(f"Demo user {DEMO_EMAIL} already exists. Skip seed.")
            return

        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=DEMO_EMAIL,
            password_hash=get_password_hash(DEMO_PASSWORD),
            oauth_provider=OAuthProvider.EMAIL,
            oauth_id=None,
            timezone="Asia/Seoul",
        )
        db.add(user)
        await db.flush()

        for cat_name, personas_data in DEMO_CATEGORIES:
            cat = Category(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name=cat_name,
            )
            db.add(cat)
            await db.flush()

            for name, temp in personas_data:
                p = Persona(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    name=name,
                    phone_number=DEFAULT_PHONE,
                    category_id=cat.id,
                    birth_date=DEFAULT_BIRTH,
                    anniversary_date=DEFAULT_ANNIV,
                    importance_weight=50,
                    relationship_temp=float(temp),
                )
                db.add(p)

        await db.commit()
        print(f"Demo user created: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print("Categories: 가족, 직장, 친구, 연인, 멘토 (2 personas each)")


if __name__ == "__main__":
    asyncio.run(seed())
