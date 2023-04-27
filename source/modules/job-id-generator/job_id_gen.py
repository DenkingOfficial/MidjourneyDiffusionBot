import secrets
import time


def generate_id(id_length: int = 16) -> str:
    return secrets.token_urlsafe(id_length)[:id_length]


if __name__ == "__main__":
    start_time = time.time()
    print(generate_id(16))
    print("--- %s seconds ---" % (time.time() - start_time))
