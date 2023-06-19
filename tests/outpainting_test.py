import sys
from pathlib import Path

from pyrogram.types import Message

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.outpainting import Outpaint

message = Message(
    id=1,
    text="/outpaint --guide a beautiful picture --direction vertical --amount 40",
)
outpaint = Outpaint(queue=[], message=message)


def test_outpaint_args_parser():
    args = outpaint.parse_message_text(message.text)
    assert args["guide"] == "a beautiful picture"
    assert args["direction"] == "vertical"
    assert args["amount"] == 40


def test_nearest_divisible_by_8():
    resolution = (514, 769)
    assert outpaint.nearest_divisible_by_8(resolution) == (512, 768)
