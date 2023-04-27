import re


DEFAULT_VALUES = {
    "ar": "1:1",
    "count": 4,
    "model": "illuminati_v1.1",
    "seed": -1,
    "cfg": 5.0,
    "facefix": "0",
    "style": "default",
    "negative": "",
    "hr": "0",
}


def get_generation_args_new(command, defaults):
    args = re.split(" --|--| —|—", command.replace("/imagine", "--prompt"))
    args_dict = {
        arg.split(" ", 1)[0]: arg.split(" ", 1)[1] for arg in args if " " in arg
    }
    return {**defaults, **args_dict}


if __name__ == "__main__":
    print(
        get_generation_args_new(
            "/imagine 90s hacker with mustaches, at hacker room,"
            " old monitors, keyboards, light background, reflections,"
            " neon lights, purple and light blue colors"
            " --cfg 6.5 --ar 16:9 --count 1 --style art",
            DEFAULT_VALUES,
        )
    )
