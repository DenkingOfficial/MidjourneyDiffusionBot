from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import CallbackQuery
from pyrogram.handlers.callback_query_handler import CallbackQueryHandler
from scripts.get_secrets import read_secrets
from scripts.txt2img import Txt2Img
from scripts.upscale import Upscale
from scripts.outpainting import Outpaint
from scripts.redraw import Redraw
import scripts.consts as consts

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
        "`/imagine Описание картинки`\n",
    )


@app.on_message(filters.command(["help"]))
async def help(client, message):
    command = message.text.split(" ", 1)

    if len(command) > 1:
        argument = command[1].lower()

        if argument == "imagine":
            await message.reply_text(consts.TXT2IMG_HELP_TEXT)
        elif argument == "outpaint":
            await message.reply_text(consts.OUTPAINT_HELP_TEXT)
        elif argument == "redraw":
            await message.reply_text(consts.REDRAW_HELP_TEXT)
        else:
            await message.reply_text(
                "Неизвестная команда. Используйте /help без аргументов, чтобы увидеть список доступных команд."
            )
    else:
        await message.reply_text(consts.HELP_TEXT)


@app.on_message(filters.command(["imagine"]))
def imagine(client, message):
    global queue
    t2i = Txt2Img(queue, message)
    t2i.process()


@app.on_message(filters.command(["outpaint"]))
def outpaint(client, message):
    global queue
    outpaint = Outpaint(queue, message)
    outpaint.process()


@app.on_message(filters.command(["redraw"]))
def redraw(client, message):
    global queue
    redraw = Redraw(queue, message)
    redraw.process()


def variations_process(client: Client, call: CallbackQuery):
    client.answer_callback_query(call.id)  # type: ignore
    global queue
    var = Txt2Img(queue, variations=True)
    var.process(call=call)


def regenerate_process(client: Client, call: CallbackQuery):
    client.answer_callback_query(call.id)  # type: ignore
    global queue
    regen = Txt2Img(queue)
    regen.process(call=call)


def upscale_fast_process(client: Client, call: CallbackQuery):
    client.answer_callback_query(call.id)  # type: ignore
    global queue
    ups = Upscale(queue)
    ups.process(call=call)


def call_data(data):
    async def filter_data(self, __, call: CallbackQuery):
        return self.data.split("/")[0] == call.data.split("/")[0]  # type: ignore

    return filters.create(filter_data, data=data)


app.add_handler(CallbackQueryHandler(upscale_fast_process, call_data("UF")))

app.add_handler(CallbackQueryHandler(variations_process, call_data("V")))

app.add_handler(CallbackQueryHandler(regenerate_process, call_data("RG")))

app.run()
