GREETINGS = (
    "Привет!\nЯ MidjourneyDiffusion бот, "
    "генерирую картинки по описанию.\n\n"
    "Для генерации картинок напиши команду\n"
    "`/imagine Описание картинки`\n"
)
HELP = (
    "Format: `/imagine (Your prompt) [--argument value]`\n"
    "\n"
    "Available args:\n"
    "`--ar` — aspect ratio of an image (default: `1:1`)\n"
    "` ` Available values:\n"
    "`  ` — `1:1`\n"
    "`  ` — `16:9` or `9:16`\n"
    "`  ` — `4:3` or `3:4`\n"
    "\n"
    "`--count` — number of images to generate (default: `4`)\n"
    "` ` Available values:\n"
    "`  ` — A number in range `1-4`\n"
    "\n"
    "`--model` — which model to use (default: `illuminati_v1.1`)\n"
    "` ` Available values:\n"
    "`  ` — `illuminati_v1.1` - High quality model trained using "
    "noise offset, based on SD 2.1\n"
    "`  ` — `original_sd_2.1` - Original Stable Diffusion 2.1 model\n"
    "`  ` — `original_sd_1.5` - Original Stable Diffusion 1.5 model\n"
    "\n"
    "`--seed` — seed to use (default: `random`)\n"
    "` ` Available values:\n"
    "`  ` — A number in range `0-9999999999999999999`\n"
    "\n"
    "`--cfg` — how close prompt follows the image (default: `5`)\n"
    "` ` Available values:\n"
    "`  ` — A number in range `1-15`\n"
    "\n"
    "`--facefix` — fix faces (default: `0`)\n"
    "` ` Available values:\n"
    "`  ` — `0` - Turn off\n"
    "`  ` — `1` - Turn on\n"
    "\n"
    "`--style` — style to use\n"
    "` ` Available values:\n"
    "`  ` — `realistic` - photorealistic images\n"
    "`  ` — `art` - digital art\n"
    "`  ` — `pixel-art` - pixel art images (NOT IMPLEMENTED)"
)