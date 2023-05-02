from app import create_app
from modules.storage_manager.user_storages_manager import UserStorageManager
from dependencies import DependencyContainer

queue = []
storage_manager = UserStorageManager()

deps = DependencyContainer(queue, storage_manager)

app = create_app(deps)
app.run()
