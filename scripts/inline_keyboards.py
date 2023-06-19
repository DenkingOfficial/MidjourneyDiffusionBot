from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def inline_keyboards(user_info, job_id, variations):
    if variations:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Увеличить изображение:", callback_data="_"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=str(i + 1),
                        callback_data=f"UF/{user_info['username']}/{job_id}/{i}",
                    )
                    for i in range(user_info["images_count"])
                ],
                [
                    InlineKeyboardButton(
                        text="🔄 Перегенерировать вариации",
                        callback_data=f"V/{user_info['username']}/{user_info['orig_image_job_id']}/{user_info['seed']}",
                    )
                ],
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Увеличить изображение:", callback_data="_"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=str(i + 1),
                        callback_data=f"UF/{user_info['username']}/{job_id}/{i}",
                    )
                    for i in range(user_info["images_count"])
                ],
                [
                    InlineKeyboardButton(
                        text="Сгенерировать вариации:", callback_data="_"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=str(i + 1),
                        callback_data=f"V/{user_info['username']}/{job_id}/{user_info['seeds'][i]}",
                    )
                    for i in range(user_info["images_count"])
                ],
                [
                    InlineKeyboardButton(
                        text="🔄 Перегенерировать (кол-во)",
                        callback_data="_",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=str(i + 1),
                        callback_data=f"RG/{user_info['username']}/{job_id}/{str(i + 1)}",
                    )
                    for i in range(4)
                ],
            ]
        )
