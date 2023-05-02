import re
from pyrogram.types import Message

MAX_SEED_VALUE = 9999999999999999999

TXT2IMG_AVAILABLE_ARGS = (
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
)

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

AVAILABLE_ASPECT_RATIO_DICT = ("16:9", "4:3", "1:1", "9:16", "3:4")

AVAILABLE_STYLES_DICT = ("default", "realistic", "art", "pixel-art")

AVAILABLE_MODELS_DICT = ("illuminati_v1.1", "original_sd_1.5", "original_sd_2.1")


def get_generation_args(command: Message):
    args = re.split(" --|--| —|—", command.text)
    args[0] = args[0].split(" ", 1)
    if len(args[0]) == 1:
        return False
    args[0][0] = "prompt"
    try:
        args[1:] = map(lambda param: re.split(" ", param, 1), args[1:])
        args = dict(args)
    except ValueError:
        return False
    return DEFAULT_VALUES | args


def check_args(args, available_args):
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
