"""
라다 차트(홈 화면 관계 만족도) 비즈니스 로직
사용자별 카테고리 + 페르소나 평균 관계온도 조회
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import Category, Persona
from schemas import RadarResponse, RadarCategoryItem, RadarPersonaItem


# 라다 차트 카테고리별 색상 (순서대로 적용)
RADAR_COLORS = [
    "#9B7BCC", "#5BA8C9", "#5BA89A", "#C97B9A", "#C9A86B",
    "#8B7BAB", "#7BA8B9", "#7BA89A", "#B97B8A", "#B9A87B",
]


class RadarService:
    """라다 차트 데이터 서비스"""

    @staticmethod
    async def get_radar_for_user(db: AsyncSession, user_id: str) -> RadarResponse:
        """
        로그인한 사용자의 라다 차트 데이터 조회.
        카테고리별 평균 relationship_temp(관계온도)와 페르소나 목록을 반환합니다.
        """
        result = await db.execute(
            select(Category)
            .where(Category.user_id == user_id)
            .order_by(Category.created_at.asc())
            .options(selectinload(Category.personas))
        )
        categories = result.scalars().all()

        items: list[RadarCategoryItem] = []
        total_score_sum = 0.0
        total_count = 0

        for cat in categories:
            personas = cat.personas or []
            if not personas:
                score = 50.0  # 페르소나 없으면 중간값
                names = []
            else:
                score = sum(p.relationship_temp for p in personas) / len(personas)
                names = [RadarPersonaItem(name=p.name) for p in personas]

            items.append(
                RadarCategoryItem(
                    id=cat.id,
                    name=cat.name,
                    score=round(score, 1),
                    persona_count=len(personas),
                    personas=names,
                )
            )
            total_score_sum += score * len(personas) if personas else score
            total_count += len(personas) if personas else 1

        overall = round(total_score_sum / total_count, 1) if total_count > 0 else 63.0
        return RadarResponse(categories=items, overall_score=overall)
