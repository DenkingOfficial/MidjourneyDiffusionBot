import re

defaults = {
    "prompt": "test",
    "ar": "1:1",
    "count": 4,
    "model": "illuminati_v1.1",
    "seed": -1,
    "cfg": 5.0,
    "facefix": "0",
    "style": "default",
    "negative": "",
}


def get_generation_args_new(command, defaults):
    args = command.replace("/imagine", "--prompt")
    args = re.split(" --|--| —|—", args)
    args = [arg.split(" ", 1) for arg in args]
    args = {arg[0]: arg[1] for arg in args if len(arg) == 2}
    return defaults | args


if __name__ == "__main__":
    print(
        get_generation_args_new(
            "/imagine 90s hacker with mustaches, at hacker room,"
            " old monitors, keyboards, light background, reflections,"
            " neon lights, purple and light blue colors"
            " --cfg 6.5 --ar 16:9 --count 1 --style art",
            defaults
        )
    )
