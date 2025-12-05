from typing import Any, Generic, List, Optional, Tuple, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.sql import Select

from app.core.database import db
from app.models.base import BaseModel
from app.schemas.base import Pager
from app.utils.sort_helper import parse_order_string

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    model: Type[ModelType]

    async def get_by_id(self, entity_id: int) -> Optional[ModelType]:
        async with db.session() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == entity_id)
            )
            return result.scalar_one_or_none()

    async def get_all(
        self,
        pager: Optional[Pager] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[List[ModelType], int]:
        query = select(self.model)
        return await self._paginate(query, pager, order_by)

    async def create(self, **kwargs: Any) -> ModelType:
        async with db.session() as session:
            instance = self.model(**kwargs)
            session.add(instance)
            await session.flush()
            await session.refresh(instance)
            return instance

    async def update(self, entity_id: int, **kwargs: Any) -> Optional[ModelType]:
        async with db.session() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == entity_id)
            )
            instance = result.scalar_one_or_none()
            if not instance:
                return None
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await session.flush()
            await session.refresh(instance)
            return instance

    async def delete(self, entity_id: int) -> bool:
        async with db.session() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == entity_id)
            )
            instance = result.scalar_one_or_none()
            if not instance:
                return False
            await session.delete(instance)
            return True

    async def count(self, query: Optional[Select] = None) -> int:
        async with db.session() as session:
            if query is None:
                count_query = select(func.count()).select_from(self.model)
            else:
                count_query = select(func.count()).select_from(query.subquery())
            result = await session.execute(count_query)
            return result.scalar() or 0

    async def _paginate(
        self,
        query: Select,
        pager: Optional[Pager] = None,
        order_by: Optional[str] = None,
    ) -> Tuple[List[ModelType], int]:
        """Execute query with pagination and sorting."""
        async with db.session() as session:
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            if not total:
                return [], 0

            if order_by:
                order_clause = parse_order_string(order_by, self.model)
                if order_clause is not None:
                    query = query.order_by(order_clause)

            if pager:
                query = query.offset(pager.offset).limit(pager.limit)

            result = await session.execute(query)
            items = list(result.scalars().all())
            return items, total
