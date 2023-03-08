from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def txt2img_inline_keyboard(message, job_id, images_count, seeds):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Upscale an image:", callback_data="_")],
            [
                InlineKeyboardButton(
                    text=str(i + 1),
                    callback_data=f"UF/{message.from_user.username}/{job_id}/{i}/{message.from_user.id}",
                )
                for i in range(images_count)
            ],
            [InlineKeyboardButton(text="Generate variations:", callback_data="_")],
            [
                InlineKeyboardButton(
                    text=str(i + 1),
                    callback_data=f"V/{message.from_user.username}/{job_id}/{seeds[i]}",
                )
                for i in range(images_count)
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Regenerate (Count)",
                    callback_data="_",
                )
            ],
            [
                InlineKeyboardButton(
                    text=str(i + 1),
                    callback_data=f"RG/{message.from_user.username}/{job_id}/{str(i + 1)}",
                )
                for i in range(4)
            ],
        ]
    )
