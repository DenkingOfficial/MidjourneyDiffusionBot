import json


class JsonReader:
    @staticmethod
    def read_json_file(filename, model=None) -> dict:
        try:
            with open(filename, mode="r", encoding="UTF-8") as f:
                if model is None:
                    return json.loads(f.read())
                else:
                    return json.loads(f.read())[model]
        except FileNotFoundError:
            raise FileNotFoundError("JSON File not found")


if __name__ == "__main__":
    json_reader = JsonReader()
    print("Model not specified")
    print(json_reader.read_json_file("secrets.json"))
    print("Model specified")
    print(json_reader.read_json_file("config/settings.json", "model_2"))
