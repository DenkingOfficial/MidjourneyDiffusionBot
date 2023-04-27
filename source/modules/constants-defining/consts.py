SD_URL = "192.168.0.66"

SD_PORT = "7860"

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
