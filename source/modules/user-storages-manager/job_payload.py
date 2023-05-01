import json
from typing import Any
from pathlib import Path


GEN_INFO = "gen_info.json"


class JobPayload:
    id: str
    prompt: str
    negative_prompt: str
    cfg_scale: float
    sampler_index: str
    steps: int
    batch_size: int
    n_iter: int
    seed: int
    restore_faces: bool
    enable_hr: bool
    hr_upscaler: str
    denoising_strength: float
    width: int
    height: int
    override_settings: dict

    def __init__(self, payload: dict[str, Any]) -> None:
        self.id = payload["id"]
        self.prompt = payload["prompt"]
        self.negative_prompt = payload["negative_prompt"]
        self.cfg_scale = payload["cfg_scale"]
        self.sampler_index = payload["sampler_index"]
        self.steps = payload["steps"]
        self.batch_size = payload["batch_size"]
        self.n_iter = payload["n_iter"]
        self.seed = payload["seed"]
        self.restore_faces = payload["restore_faces"]
        self.enable_hr = payload["enable_hr"]
        self.hr_upscaler = payload["hr_upscaler"]
        self.denoising_strength = payload["denoising_strength"]
        self.width = payload["width"]
        self.height = payload["height"]
        self.override_settings = payload["override_settings"]

    def save(self, user_job: Path) -> None:
        with open(str(user_job.joinpath(GEN_INFO)), "w") as fp:
            json.dump(self, fp, default=lambda o: o.__dict__, sort_keys=True)

    @staticmethod
    def read(user_job: Path):
        user_job_info = user_job.joinpath(GEN_INFO)
        if not user_job_info.exists():
            return None
        with open(str(user_job_info)) as fp:
            user_job_info_obj = json.load(fp)
        return JobPayload(user_job_info_obj)
