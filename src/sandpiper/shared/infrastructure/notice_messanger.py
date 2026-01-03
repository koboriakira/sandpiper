from typing import Protocol


class NoticeMessanger(Protocol):
    def send(self, message: str) -> None: ...
