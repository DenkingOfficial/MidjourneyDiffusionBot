import secrets
from functools import partial
import string
import time


def produce_id(id_len: int = 16) -> str:
    pickchar = partial(secrets.choice, string.ascii_letters + string.digits)
    key = "".join([pickchar() for _ in range(id_len)])
    return key


if __name__ == "__main__":
    start_time = time.time()
    print(produce_id(16))
    print("--- %s seconds ---" % (time.time() - start_time))
