SD_URL = "http://192.168.0.66:7860"

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

ASPECT_RATIO_DICT = {
    "16:9": {"width": 1024, "height": 576},
    "4:3": {"width": 768, "height": 576},
    "1:1": {"width": 768, "height": 768},
    "9:16": {"width": 576, "height": 1024},
    "3:4": {"width": 576, "height": 768},
}

OUTPAINTING_AVAILABLE_ARGS = (
    "direction",
    "amount",
)
