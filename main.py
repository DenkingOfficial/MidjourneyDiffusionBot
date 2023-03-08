from pyrogram import Client, filters
# from pyrogram.types import CallbackQuery
# from pyrogram.handlers.callback_query_handler import CallbackQueryHandler
import scripts.utils as utils
from scripts.txt2img import txt2img
import webuiapi

AUTH_INFO = utils.json_to_dict("secrets.json")
LOCALIZATION_FILE = "./config/ru_RU.json"
LOCALIZATION = utils.json_to_dict(LOCALIZATION_FILE)

queue = []

api = webuiapi.WebUIApi(
    host=AUTH_INFO["SD_HOST"],
    port=AUTH_INFO["SD_PORT"],
    sampler="Euler",
    steps=10
)

app = Client(
    "MidjourneyDiffusion",
    api_id=AUTH_INFO["API_ID"],
    api_hash=AUTH_INFO["API_HASH"],
    bot_token=AUTH_INFO["TOKEN"],
)


@app.on_message(filters.command(["start"]))
async def start(client, message):
    start_image = "./static/startImg.png"
    await message.reply_photo(
        photo=start_image,
        caption=LOCALIZATION["start_message"],
    )


@app.on_message(filters.command(["help"]))
def help(message):
    message.reply_text(LOCALIZATION["help_txt2img"])


@app.on_message(filters.command(["imagine"]))
def imagine(client, message):
    global queue
    status = txt2img(api, client, message, queue)
    if not status:
        help(message)


app.run()
