import re
from typing import Any, Union

MAX_SEED_VALUE = 9999999999999999999

ASPECT_RATIO_DICT = {
    "16:9": {"width": 1024, "height": 576},
    "4:3": {"width": 768, "height": 576},
    "1:1": {"width": 768, "height": 768},
    "9:16": {"width": 576, "height": 1024},
    "3:4": {"width": 576, "height": 768},
}

TXT2IMG_AVAILABLE_ARGS = [
    "prompt",
    "ar",
    "count",
    "model",
    "seed",
    "cfg",
    "facefix",
    "style",
    "negative",
    "hr",
]

AVAILABLE_ASPECT_RATIO_DICT = ["16:9", "4:3", "1:1", "9:16", "3:4"]

AVAILABLE_STYLES_DICT = ["default", "realistic", "art", "pixel-art"]

AVAILABLE_MODELS_DICT = ["illuminati_v1.1", "original_sd_1.5", "original_sd_2.1"]

DEFAULT_VALUES = {
    "ar": "1:1",
    "count": 4,
    "model": "illuminati_v1.1",
    "seed": -1,
    "cfg": 5.0,
    "facefix": "0",
    "style": "default",
    "negative": "",
    "hr": "0",
}


def command_to_args(
    command: str, available_params: list[str]
) -> Union[dict[str, Any], None]:
    try:
        prompt, *args = re.split(" --|--| —|—", command)
        cmd, *prompt = prompt.split(" ", 1)
        args = map(lambda arg: re.split(" ", arg, 1), args)
        if len(prompt) == 0:
            return None
        formatted_args = {"prompt": prompt, **dict(args)}
        if not check_args(formatted_args, available_params):
            return None
        return DEFAULT_VALUES | formatted_args
    except ValueError:
        return None


def check_args(args: dict, available_args: list[str]):
    try:
        assert not sorted(set(args).difference(available_args))
        assert args["prompt"]
        assert int(args["hr"]) == 0 or int(args["hr"]) == 1
        assert args["ar"] in AVAILABLE_ASPECT_RATIO_DICT
        assert int(args["count"]) >= 1 and int(args["count"]) <= 4
        assert int(args["seed"]) == -1 or (
            int(args["seed"]) >= 1 and int(args["seed"]) <= MAX_SEED_VALUE
        )
        assert float(args["cfg"]) >= 1.0 and float(args["cfg"]) <= 15.0
        assert int(args["facefix"]) == 0 or int(args["facefix"]) == 1
        assert args["style"] in AVAILABLE_STYLES_DICT
        assert args["model"] in AVAILABLE_MODELS_DICT
    except AssertionError:
        return False
    except KeyError:
        pass
    return True


if __name__ == "__main__":
    raw_imagine_prompt = "/imagine Владимир Путин, лсд, стиль Ван Гога, портрет 3/4, глитч, очки, цвета --facefix 1"
    command_to_args(raw_imagine_prompt, TXT2IMG_AVAILABLE_ARGS)
