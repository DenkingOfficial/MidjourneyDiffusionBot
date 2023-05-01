from pathlib import Path
import json

USER_INFO = "user_info.json"


class User:
    id: str
    name: str

    def __init__(self, user_id: str, username: str) -> None:
        self.name = username
        self.id = user_id

    def save(self, user_storage: Path) -> None:
        with open(str(user_storage.joinpath(USER_INFO)), "w") as fp:
            json.dump(self, fp, default=lambda o: o.__dict__, sort_keys=True)

    def __str__(self) -> str:
        return f"User: {self.name}/{self.id}"

    @staticmethod
    def read(user_storage: Path):
        user_job_info = user_storage.joinpath(USER_INFO)
        if not user_job_info.exists():
            return None
        with open(str(user_job_info)) as fp:
            user_job_info_obj = json.load(fp)
        username = user_job_info_obj["username"]
        user_id = user_job_info_obj["user_id"]
        return User(username, user_id)
