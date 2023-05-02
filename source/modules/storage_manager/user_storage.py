from typing import Iterable, Union

from PIL.Image import Image as ImageType
from PIL import Image
from pathlib import Path

from user import User
from user_job import UserJob
from job_payload import JobPayload


class UserStorage:
    _storage: Path
    _user_storage: Path
    _user: User

    def __init__(self, storage: Path, user: User) -> None:
        self._storage = storage
        self._user = user
        self._user_storage = self._storage.joinpath(user.id)

        self._user_storage.mkdir(parents=True, exist_ok=True)
        self._user.save(self._user_storage)

    @staticmethod
    def read(user_storage: Path):
        user = User.read(user_storage)
        if not user_storage.exists() or not user:
            return None
        return UserStorage(user_storage.parent, user)

    def remove(self) -> None:
        pass

    def get_job(self, job_id: str) -> Union[UserJob, None]:
        return UserJob.read(self._user_storage.joinpath(job_id))

    def save_job(
        self,
        job_payload: JobPayload,
        images: Iterable[ImageType],
        grid_image: ImageType,
    ) -> None:
        UserJob(self._user_storage, job_payload, images, grid_image).save()

    def get_job_ids(self) -> Iterable[str]:
        for folder in self._user_storage.iterdir():
            if folder.is_dir():
                yield folder.name

    def get_job_list(self) -> Iterable[UserJob]:
        for folder in self._user_storage.iterdir():
            if folder.is_dir():
                userjob = UserJob.read(folder)
                if userjob:
                    yield userjob


if __name__ == "__main__":
    payload = JobPayload.read(
        Path(".\\output\\txt2img\\mirvodaartem\\girl--rbj0hA0UlmNlmb1P\\")
    )
    if payload:
        user = User("UserId", "UserName")
        storage = UserStorage(Path("source\\modules\\user-storages-manager"), user=user)
        storage.get_job_list()

        images = [
            Image.open(
                "output\\txt2img\\mirvodaartem\\girl--rbj0hA0UlmNlmb1P\\0-girl--rbj0hA0UlmNlmb1P-2896430189.png"
            ),
            Image.open(
                "output\\txt2img\\mirvodaartem\\girl--rbj0hA0UlmNlmb1P\\0-girl--rbj0hA0UlmNlmb1P-2896430189.png"
            ),
            Image.open(
                "output\\txt2img\\mirvodaartem\\girl--rbj0hA0UlmNlmb1P\\0-girl--rbj0hA0UlmNlmb1P-2896430189.png"
            ),
            Image.open(
                "output\\txt2img\\mirvodaartem\\girl--rbj0hA0UlmNlmb1P\\0-girl--rbj0hA0UlmNlmb1P-2896430189.png"
            ),
        ]
        grid = Image.open(
            "output\\txt2img\\mirvodaartem\\girl--rbj0hA0UlmNlmb1P\\girl--rbj0hA0UlmNlmb1P-grid.jpg"
        )
        storage.save_job(payload, images, grid)
        lst = list(storage.get_job_list())
        print()
