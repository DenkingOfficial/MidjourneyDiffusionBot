# MidjourneyDiffusionBot

![build status](https://img.shields.io/github/actions/workflow/status/DenkingOfficial/MidjourneyDiffusionBot/python-app.yml?style=flat-square)

Telegram бот, который позволяет генерировать изображения по описанию (совсем как Midjourney).

![Bot UI](/static/bot-ui.jpg)

Он использует локальный или удаленный сервер со [Stable Diffusion WebUI](https://github.com/DenkingOfficial/pure-sd-webui), руководство по установке в репозитории. Бот полностью мультиязычный ~~(Скажи ДА промптам на казахском)~~. На выбор пользователя доступны три модели, генерирующие различные результаты:

* Illuminati Diffusion 2.1-768
* Stable Diffusion 2.1-768
* Stable Diffusion 1.5

Бот поднят на Yandex.Cloud и работает прямо сейчас. Потыкать можно [тут](https://t.me/midjourneydiffusion_bot).

## Возможности

На выбор для пользователя доступны 3 команды для исполнения:
1. /imagine - команда для генерации изображений
2. /redraw - команда для перерисовки изображений
3. /outpaint - команда для дорисовки изображений

Более подробная инструкция по командам [здесь](https://github.com/DenkingOfficial/MidjourneyDiffusionBot/wiki/%D0%94%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%B0%D1%86%D0%B8%D1%8F-%D0%BF%D0%BE-%D0%BA%D0%BE%D0%BC%D0%B0%D0%BD%D0%B4%D0%B0%D0%BC)

Также пользователь может перегенирировать изображения (если они ему не понравились), сгенерировать вариации или увеличить разрешение в Inline-клавиатуре под ответом бота:

![Inline Keyboard](/static/inline-keyboard.jpg)

## Зависимости

- Python 3.10 или новее
- Pillow 9.4.0
- Pyrogram 2.0.100
- Requests 2.28.2
- TgCrypto 1.2.5
- YandexFreeTranslate

## Как установить

1. Установить и запустить [Stable Diffusion WebUI](https://github.com/DenkingOfficial/pure-sd-webui). (требуется GPU с +6GB видеопамяти)
2. Скачать вышеуказанные модели, поместить в папку `[папка с webui]/models/Stable-diffusion`.
3. Установить расширения [ControlNet](https://github.com/Mikubill/sd-webui-controlnet) и [Tiled Diffusion & VAE](https://github.com/pkuliyi2015/multidiffusion-upscaler-for-automatic1111) для WebUI.
4. Скачать две модели ([одна](https://huggingface.co/lllyasviel/control_v11p_sd15_softedge/blob/main/diffusion_pytorch_model.fp16.safetensors), [вторая](https://huggingface.co/lllyasviel/control_v11p_sd15_inpaint/blob/main/diffusion_pytorch_model.fp16.safetensors)) и поместить в папку `[папка с webui]/models/ControlNet`.
5. Создать бота через [BotFather](https://t.me/BotFather) в Telegram и приложение на [этом](https://telegram.org/apps) сайте.
6. На выбор:

Первый способ

+ Поставить разработанное [расширение](https://github.com/DenkingOfficial/sd-telegram-bot-extension) для Stable Diffusion WebUI
+ Настроить данные для доступа к боту в настройках WebUI и применить изменения

![WebUI Settings](/static/webui-extension.jpg)

+ Перейти на вкладку Telegram Bot и нажать на кнопку `Start Telegram Bot`

![WebUI Bot Tab](/static/webui-bot-tab.jpg)

ИЛИ

Второй способ

+ Загрузить данный репозиторий используя команду `git clone https://github.com/DenkingOfficial/MidjourneyDiffusionBot.git`
+ Перейти в директорию репозитория `cd MidjourneyDiffusionBot`
+ Cоздать виртуальное окружение (venv) с помощью команды `python -m venv venv`
+ Активировать виртуальное окружение с помощью комамнды `./venv/Scripts/activate`
+ Установить зависимости используя команду `pip install -r requirements.txt`
+ Создать файл `secrets.json` на основе `secrets_template.json` приложенного в репозитории с данными для доступа к боту
+ Выполнить команду `python main.py`

## Авторы

Это приложение было разработано студентами Уральского Федерального университета (УрФУ):

- [Шершнев Андрей](https://github.com/DenkingOfficial), РИМ-120907
- [Касов Артем](https://github.com/A-Kasov), РИМ-120906
- [Мирвода Артем](https://github.com/Roccowen)(†), РИМ-120907 
- [Иванов Сергей](https://github.com/rancelyndar), РИМ-120906
