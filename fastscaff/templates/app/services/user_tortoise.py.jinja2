from app.core.security import get_password_hash
from app.exceptions.base import UserAlreadyExists, UserNotFound
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserInfo


class UserService:
    def __init__(self) -> None:
        self.repo = UserRepository()

    async def create_user(self, data: UserCreate) -> UserInfo:
        existing = await self.repo.get_by_username(data.username)
        if existing:
            raise UserAlreadyExists

        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise UserAlreadyExists

        hashed_password = get_password_hash(data.password)
        user = await self.repo.create_user(
            username=data.username,
            email=data.email,
            hashed_password=hashed_password,
        )

        return UserInfo.model_validate(user)

    async def get_user_by_id(self, user_id: int) -> UserInfo:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound

        return UserInfo.model_validate(user)

