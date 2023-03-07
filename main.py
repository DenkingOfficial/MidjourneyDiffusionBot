from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from pyrogram.handlers.callback_query_handler import CallbackQueryHandler
from scripts.get_secrets import read_secrets
from scripts.txt2img import txt2img
from scripts.upscale import upscale_fast
from scripts.variations import variations
from scripts.regenerate import regenerate
import scripts.utils as utils

secrets = read_secrets()

queue = []

app = Client(
    "MidjourneyDiffusion",
    api_id=secrets["API_ID"],
    api_hash=secrets["API_HASH"],
    bot_token=secrets["TOKEN"],
)


@app.on_message(filters.command(["start"], prefixes=["/", "!"]))
async def start(client, message):
    start_image = "./static/startImg.png"
    await message.reply_photo(
        photo=start_image,
        caption="Привет!\nЯ MidjourneyDiffusion бот, "
        "генерирую картинки по описанию.\n"
        "\n"
        "Для генерации картинок напиши команду\n"
        "`/imagine prompt:Описание картинки`\n",
    )


@app.on_message(filters.command(["imagine"]))
def imagine(client, message):
    global queue
    txt2img(client, message, queue)


def regenerate_process(client: Client, call: CallbackQuery):
    client.answer_callback_query(call.id)
    call.message.reply_text(call.data)
    global queue
    regenerate(client, call, queue)


def upscale_fast_process(client: Client, call: CallbackQuery):
    client.answer_callback_query(call.id)
    call.message.reply_text(call.data)
    global queue
    upscale_fast(client, call, queue)


def variations_process(client: Client, call: CallbackQuery):
    client.answer_callback_query(call.id)
    call.message.reply_text(call.data)
    global queue
    variations(client, call, queue)


def call_data(data):
    async def filter_data(self, __, call: CallbackQuery):
        return self.data.split("/")[0] == call.data.split("/")[0]

    return filters.create(filter_data, data=data)


app.add_handler(CallbackQueryHandler(upscale_fast_process, call_data("UF")))

app.add_handler(CallbackQueryHandler(variations_process, call_data("V")))

app.add_handler(CallbackQueryHandler(regenerate_process, call_data("RG")))


@app.on_message(filters.command(["help"]))
async def help(client, message):
    await message.reply_text(utils.HELP_TEXT)


app.run()