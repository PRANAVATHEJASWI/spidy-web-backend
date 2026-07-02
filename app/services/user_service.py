from uuid import uuid4
from hashlib import sha256

from app.models.user import StoredUser, User, UserCreate, UserLogin
from app.repositories.store import Store, get_store


class UserService:
    collection = "users"

    def __init__(self, store: Store | None = None) -> None:
        self.store = store or get_store()

    def _hash_password(self, password: str) -> str:
        return sha256(password.encode("utf-8")).hexdigest()

    def _public_user(self, user: StoredUser) -> User:
        return User(**user.model_dump(exclude={"password_hash"}))

    def get_user_by_email(self, email: str) -> StoredUser | None:
        for item in self.store.list(self.collection):
            if item.get("email", "").lower() == email.lower():
                return StoredUser(**item)
        return None

    def create_user(self, payload: UserCreate) -> User:
        if self.get_user_by_email(str(payload.email)):
            raise ValueError("A user with this email already exists")
        data = payload.model_dump(exclude={"password"})
        user = StoredUser(
            id=str(uuid4()),
            password_hash=self._hash_password(payload.password),
            **data,
        )
        self.store.set(self.collection, user.id, user.model_dump(mode="json"))
        return self._public_user(user)

    def login(self, payload: UserLogin) -> User | None:
        user = self.get_user_by_email(str(payload.email))
        if user is None:
            return None
        if user.password_hash != self._hash_password(payload.password):
            return None
        return self._public_user(user)

    def get_user(self, user_id: str) -> User | None:
        data = self.store.get(self.collection, user_id)
        return self._public_user(StoredUser(**data)) if data else None

    def list_users(self) -> list[User]:
        return [self._public_user(StoredUser(**item)) for item in self.store.list(self.collection)]
