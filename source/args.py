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

AVAILABLE_STYLES_LIST = ["default", "realistic", "art", "pixel-art"]

AVAILABLE_MODELS_LIST = ["illuminati_v1.1", "original_sd_1.5", "original_sd_2.1"]

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
        args = re.split(" --|--| —|—", command.replace("/imagine", "--prompt"))
        args = DEFAULT_VALUES | {
            arg.split(" ", 1)[0]: arg.split(" ", 1)[1] for arg in args if " " in arg
        }
        if not check_args(args, available_params):
            return None
        return args
    except ValueError:
        return None


def check_args(args: dict, available_args: list[str]):
    try:
        assert not sorted(set(args).difference(available_args))
        assert 1 <= int(args["count"]) <= 4
        assert int(args["seed"]) == -1 or (1 <= int(args["seed"]) <= MAX_SEED_VALUE)
        assert 1.0 <= float(args["cfg"]) <= 15.0
        assert int(args["facefix"]) in [0, 1]
        assert int(args["hr"]) in [0, 1]
        assert (
            args["prompt"]
            and args["ar"] in ASPECT_RATIO_DICT.keys()
            and args["style"] in AVAILABLE_STYLES_LIST
            and args["model"] in AVAILABLE_MODELS_LIST
        )
    except AssertionError:
        return False
    except KeyError:
        pass
    return True


if __name__ == "__main__":
    raw_imagine_prompt = "/imagine Владимир Путин, лсд, стиль Ван Гога, портрет 3/4, глитч, очки, цвета --facefix 0"
    parsed_args = command_to_args(raw_imagine_prompt, TXT2IMG_AVAILABLE_ARGS)
    print(parsed_args)
