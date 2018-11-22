import datetime


def log(msg: str, is_error: bool = False) -> None:
    print(str(datetime.datetime.time(datetime.datetime.now())) + ' - ' + ("ERROR: " if is_error else "") + msg)
