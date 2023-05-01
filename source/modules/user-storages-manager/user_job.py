from pathlib import Path
from typing import Iterable
from PIL.Image import Image as ImageType
from PIL import Image

from job_payload import JobPayload
from utils import crfname

GRID_IMG = "grid"
GEN_IMG = "gen"
IMG_FORMAT = "png"


class UserJob:
    _user_storage: Path
    _user_job: Path

    job_payload: JobPayload
    grid_image: ImageType
    images: Iterable[ImageType]

    def __init__(
        self,
        user_storage: Path,
        job_payload: JobPayload,
        images: Iterable[ImageType],
        grid_image: ImageType,
    ) -> None:
        self._user_storage = user_storage
        self.job_payload = job_payload
        self.images = images
        self.grid_image = grid_image
        self._user_job = user_storage.joinpath(job_payload.id)

    def save(self) -> None:
        self._user_job.mkdir(parents=True, exist_ok=True)
        self.job_payload.save(self._user_job)
        self.grid_image.save(self._user_job.joinpath(crfname(GRID_IMG, IMG_FORMAT)))
        for idx, img in enumerate(self.images):
            img.save(
                self._user_job.joinpath(crfname(idx, GEN_IMG, IMG_FORMAT)),
                format=IMG_FORMAT,
            )

    @staticmethod
    def read(user_job: Path):
        job_payload = JobPayload.read(user_job)
        grid_path = user_job.joinpath(crfname(GRID_IMG, IMG_FORMAT))
        if not user_job.exists() or not grid_path.exists() or not job_payload:
            return None
        images = [
            Image.open(file)
            for file in user_job.iterdir()
            if crfname(GEN_IMG, IMG_FORMAT) in file.name
        ]
        grid = Image.open(grid_path)
        return UserJob(user_job.parent, job_payload, images, grid)
