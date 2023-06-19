import sys
from pathlib import Path

from pyrogram.types import Message

sys.path.insert(0, str(Path(__file__).parent.parent))
import scripts.utils as utils
from scripts.consts import TXT2IMG_AVAILABLE_ARGS


message = Message(
    id=1,
    text="/imagine a beautiful picture --hr 1 --count 1 --negative ugly, blurred --ar 9:16",
)
args = utils.get_generation_args(message)


def test_get_generation_args_txt2img():
    assert args["prompt"] == "a beautiful picture"
    assert args["hr"] == "1"
    assert args["count"] == "1"
    assert args["negative"] == "ugly, blurred"
    assert args["ar"] == "9:16"


def test_check_args_txt2img():
    assert utils.check_args(args, TXT2IMG_AVAILABLE_ARGS)


def test_clean_prompt():
    assert utils.clean_prompt(r"H:ello ?W<orld") == "Hello World"
