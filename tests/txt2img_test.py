import sys
from pathlib import Path

from pyrogram.types import Message, User, CallbackQuery

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.txt2img import Txt2Img

user = User(
    id=1,
    username="Test",
)
message = Message(
    id=1,
    text="/imagine a beautiful picture --hr 1 --count 1 --negative ugly, blurred --ar 9:16",
    from_user=user,
)
call = CallbackQuery(
    id=1, data="V/Test/1234567812345678/4", from_user=user, chat_instance="Test"
)
txt2img = Txt2Img(queue=[], message=message)
variations = Txt2Img(queue=[], message=message, variations=True)

args = txt2img._get_args_dict(message)


def test_message_payload_former():
    payload = txt2img._compose_payload_and_user_info(args)
    assert payload["prompt"] == "a beautiful picture" + " <lyco:Mangled_Merge_Lyco:1.0>"
    assert payload["enable_hr"]
    assert payload["batch_size"] == 1
    assert payload["n_iter"] == 1
    assert payload["seed"] == -1


def test_call_variations_payload_former():
    payload = variations._get_data_for_variations_and_regen(call)
    assert payload["prompt"] == "a beautiful picture" + " <lyco:Mangled_Merge_Lyco:1.0>"
    assert payload["enable_hr"] is False
    assert payload["batch_size"] == 4
    assert payload["n_iter"] == 1
    assert payload["seed"] == 4


def test_call_regen_payload_former():
    payload = txt2img._get_data_for_variations_and_regen(call)
    assert payload["prompt"] == "a beautiful picture" + " <lyco:Mangled_Merge_Lyco:1.0>"
    assert payload["enable_hr"] is False
    assert payload["batch_size"] == 4
    assert payload["n_iter"] == 1
    assert payload["seed"] == -1
