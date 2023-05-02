from modules.storage_manager.user_storages_manager import UserStorageManager


class DependencyContainer:
    queue: list
    storage_manager: UserStorageManager

    def __init__(self, queue: list, storage_manager: UserStorageManager) -> None:
        self.queue = queue
        self.storage_manager = storage_manager
