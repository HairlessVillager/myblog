from os import getenv
from datetime import datetime, timedelta, timezone
from hashlib import sha256, pbkdf2_hmac


def get_now(tz: str = "UTC+8") -> datetime:
    if tz == "UTC+8":
        tz = timezone(timedelta(hours=8))
        return datetime.now(tz)
    elif tz == "NOTZ":
        return datetime.now()
    else:
        raise ValueError(f"not known {tz=}")


def create_token(dt: datetime) -> str:
    salt = getenv("SECRET")  # TODO: reuseable configure
    if salt is None:
        raise ValueError("SECRET is empty, a value is expected")
    salt: bytes = sha256(salt.encode("utf-8")).digest()  # type: ignore
    dk = pbkdf2_hmac(
        "sha256",
        dt.strftime("%y-%m-%d %H:%M:%S").encode("utf-8"),
        salt,  # type: ignore
        500000,
    )
    return dk.hex()


def check_token(token: str, timeout: int = 30) -> bool:
    print(f"got {token=}")
    now = get_now()
    for i in range(timeout):
        dt = now - timedelta(seconds=i)
        token2 = create_token(dt)
        print(f"check {dt=}, {token2=}")
        if token == token2:
            return True
    return False
