import sys
from pathlib import Path

from pyrogram.types import Message

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.redraw import Redraw

message = Message(
    id=1,
    text="/redraw a beautiful picture",
)
redraw = Redraw(queue=[], message=message)


def test_redraw_args_parser():
    prompt = redraw.parse_message_text(message.text)
    assert prompt == "a beautiful picture"
