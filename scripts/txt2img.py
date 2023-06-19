import os
import requests
import json
import io
from PIL import Image, PngImagePlugin
import base64
import scripts.utils as utils
from types import SimpleNamespace
from pyrogram.types import (
    InputMediaPhoto,
    Message,
)
from scripts.get_settings import get_settings
import scripts.consts as consts
from scripts.inline_keyboards import inline_keyboards


class Txt2Img:
    def __init__(self, queue: list, message: Message = None, variations: bool = False):
        self.message = message
        self.queue = queue
        self.variations = variations
        self.job_name = "Генерация" if not variations else "Генерация вариаций для"
        self.job_id = None
        self.user_info = {}

    @staticmethod
    def _get_args_dict(message):
        args = utils.get_generation_args(message)
        if not args or not utils.check_args(args, consts.TXT2IMG_AVAILABLE_ARGS):
            message.reply_text(consts.TXT2IMG_HELP_TEXT)
            return
        return SimpleNamespace(**args)

    def _compose_payload_and_user_info(self, args):
        args.gen_prompt, args.gen_negative = utils.translate_prompt(args.prompt), (
            utils.translate_prompt(args.negative) if args.negative else None
        )
        model_path = get_settings(args.model)["model_path"]
        styles = get_settings(args.model)["styles"]
        override_payload = {"override_settings": {"sd_model_checkpoint": model_path}}
        alwayson_payload = {
            "alwayson_scripts": {
                "Tiled VAE": {
                    "args": ["True", 1024, 96, "False", "False", "False", "False"]
                }
            }
            if args.hr == "1"
            else {}
        }
        payload = (
            {
                "prompt": args.gen_prompt + styles[args.style]["prompt_addition"],
                "negative_prompt": styles[args.style]["negative_prompt"]
                + (f", {args.gen_negative}" if args.negative else ""),
                "cfg_scale": float(args.cfg),
                "sampler_index": "DPM++ 2M SDE",
                "steps": 10,
                "batch_size": int(args.count) if args.hr != "1" else 1,
                "n_iter": int(args.count) if args.hr == "1" else 1,
                "seed": int(args.seed),
                "restore_faces": args.facefix == "1",
                "enable_hr": args.hr == "1",
                "hr_upscaler": "4x-UltraSharp",
                "denoising_strength": 0.25,
            }
            | consts.ASPECT_RATIO_DICT[args.ar]
            | override_payload
            | alwayson_payload
        )
        self.user_info = {
            "user_id": self.message.from_user.id,
            "username": self.message.from_user.username,
            "orig_prompt": args.prompt,
            "negative_prompt": args.negative,
            "clean_prompt": utils.clean_prompt(args.prompt),
        }
        return payload

    def _get_data_for_variations_and_regen(self, call):
        username, image_job_id, seed_or_count = call.data.split("/")[1:]
        main_folder = f"./output/txt2img/{username}/"
        for folder in os.listdir(main_folder):
            if image_job_id in folder:
                main_folder += f"{folder}/"
                break
        with open(f"{main_folder}/gen_info.json") as json_file:
            payload = json.load(json_file)
        with open(f"{main_folder}/user_info.json") as json_file:
            user_gen_info = json.load(json_file)
        payload.update(
            {
                "seed": int(seed_or_count) if self.variations else -1,
                "batch_size": 4 if self.variations else int(seed_or_count),
                "subseed_strength": 0.1 if self.variations else 0,
                "enable_hr": False,
                "alwayson_scripts": {},
            }
        )
        self.user_info = {
            "user_id": call.from_user.id,
            "username": call.from_user.username,
            "orig_prompt": user_gen_info["orig_prompt"],
            "negative_prompt": user_gen_info["negative_prompt"],
            "clean_prompt": utils.clean_prompt(user_gen_info["orig_prompt"]),
            "seed": seed_or_count if self.variations else None,
            "orig_image_job_id": image_job_id,
        }
        return payload

    def _prepare_data(self, call):
        if self.variations and call:
            payload = self._get_data_for_variations_and_regen(call)
        elif call:
            payload = self._get_data_for_variations_and_regen(call)
        else:
            args = self._get_args_dict(self.message)
            payload = self._compose_payload_and_user_info(args)
        return payload

    def _process_images(self, path, response):
        images_list = []
        self.user_info["seeds"] = utils.get_json_from_info(response)[
            "all_subseeds" if self.variations else "all_seeds"
        ]
        for index, img_base64 in enumerate(response["images"]):
            image = Image.open(
                io.BytesIO(base64.b64decode(img_base64.split(",", 1)[0]))
            )
            images_list.append(image)
            filename = f"{index}-{path.split('/')[-1]}-{self.user_info['seeds'][index]}"
            png_payload = {"image": f"data:image/png;base64,{img_base64}"}
            r_info = requests.post(
                url=f"{consts.SD_URL}/sdapi/v1/png-info", json=png_payload
            )
            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", r_info.json().get("info"))
            image.save(f"{path}/{filename}.png", pnginfo=pnginfo)
        return images_list

    def _present_results(self, path, reply, call=None):
        caption = (
            f"Описание: **{self.user_info['orig_prompt']}**\n"
            + (
                f"Негативное описание: **{self.user_info['negative_prompt']}**\n"
                if self.user_info["negative_prompt"]
                else ""
            )
            + (
                f"Seed: `{self.user_info['seed']}`\nSubseeds: {', '.join([f'`{str(seed)}`' for seed in self.user_info['seeds']])}\n\n"
                if call and self.variations
                else f"Seeds: {', '.join([f'`{str(seed)}`' for seed in self.user_info['seeds']])}\n\n"
            )
            + f"**Сгенерировано [@{self.user_info['username']}]"
            + f"(tg://user?id={self.user_info['user_id']})**"
        )
        media = InputMediaPhoto(
            media=f"{path}/{self.user_info['clean_prompt']}-{self.job_id}-grid.jpg",
            caption=caption,
        )
        reply_markup = inline_keyboards(self.user_info, self.job_id, self.variations)
        reply.edit_media(media=media, reply_markup=reply_markup)
        self.queue.pop(0)

    def process(self, call=None):
        self.job_id = utils.generate_job_id(16)
        payload = self._prepare_data(call)
        reply_message = utils.reply_template(
            self.job_name, self.queue, self.user_info, self.variations
        )
        reply = (
            call.message.reply_animation(**reply_message)
            if call
            else self.message.reply_animation(**reply_message)
        )
        utils.add_to_queue(
            reply,
            self.queue,
            self.job_id,
            self.job_name,
            self.user_info["orig_prompt"],
            self.user_info["username"],
            self.user_info["user_id"],
        )
        path = f"./output/txt2img/{self.user_info['username']}/{self.user_info['clean_prompt']}-{self.job_id}"

        if not os.path.exists(path):
            os.makedirs(path)

        r_gen = requests.post(
            url=f"{consts.SD_URL}/sdapi/v1/txt2img", json=payload
        ).json()

        images_list = self._process_images(path, r_gen)
        self.user_info["images_count"] = len(images_list)
        utils.create_image_grid(images_list).save(
            f"{path}/{self.user_info['clean_prompt']}-{self.job_id}-grid.jpg"
        )
        self._present_results(path, reply, call)

        with open(f"{path}/gen_info.json", "w") as fp:
            json.dump(payload, fp)

        self.user_info["job_id"] = self.job_id
        with open(f"{path}/user_info.json", "w") as fp:
            json.dump(self.user_info, fp)
