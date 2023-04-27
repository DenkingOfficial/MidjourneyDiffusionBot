MAX_SEED_VALUE = 9999999999999999999

DEFAULT_VALUES = {
    "ar": "1:1",
    "count": 4,
    "model": "illuminati_v1.1",
    "seed": -1,
    "cfg": 5.0,
    "facefix": "0",
    "style": "realistic",
    "negative": "",
}

AVAILABLE_ASPECT_RATIO = ("16:9", "4:3", "1:1", "9:16", "3:4")

AVAILABLE_STYLES = ("default", "realistic", "art", "pixel-art")

AVAILABLE_MODELS = ("illuminati_v1.1", "original_sd_1.5", "original_sd_2.1")

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
)


def check_args(args, args_dict, ar_dict, styles_dict, models_dict):
    try:
        assert not sorted(set(args).difference(args_dict))
        assert (
            args["prompt"]
            and args["ar"] in ar_dict
            and args["style"] in styles_dict
            and args["model"] in models_dict
        )
        assert int(args["count"]) >= 1 and int(args["count"]) <= 4
        assert int(args["seed"]) == -1 or (
            int(args["seed"]) >= 1 and int(args["seed"]) <= MAX_SEED_VALUE
        )
        assert float(args["cfg"]) >= 1.0 and float(args["cfg"]) <= 15.0
        assert int(args["facefix"]) == 0 or int(args["facefix"]) == 1
    except AssertionError:
        return False
    except KeyError:
        pass
    return True


if __name__ == "__main__":
    args = {
        "prompt": "90s hacker with mustaches",
        "ar": "16:9",
        "count": "1",
        "model": "illuminati_v1.1",
        "seed": -1,
        "cfg": "6.5",
        "facefix": "0",
        "style": "art",
        "negative": "",
    }
    result = check_args(
        args,
        TXT2IMG_AVAILABLE_ARGS,
        AVAILABLE_ASPECT_RATIO,
        AVAILABLE_STYLES,
        AVAILABLE_MODELS,
    )
    print(result)
