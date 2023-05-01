from typing import Union
from user_storage import UserStorage
from pathlib import Path

from user import User

DEFAULT_STORAGE_PATH = Path("./output/txt2img/")


class UserStorageManager:
    storage: Path
    _user_storages: dict[str, UserStorage] = {}

    def __init__(self, storage_dir: Path = DEFAULT_STORAGE_PATH) -> None:
        self.storage = storage_dir
        for item in self.storage.iterdir():
            if item.is_dir():
                user_storage = UserStorage.read(self.storage.joinpath(item.name))
                if user_storage:
                    self._user_storages[item.name] = user_storage

    def get_storage(
        self, user: User, create_if_not_exist=True
    ) -> Union[UserStorage, None]:
        user_storage = self._user_storages.get(user.id)
        if user_storage or not create_if_not_exist:
            return user_storage
        user_storage = UserStorage(self.storage, user=user)
        self._user_storages[user.id] = user_storage
        return user_storage

    def remove_storage(self) -> None:
        pass
