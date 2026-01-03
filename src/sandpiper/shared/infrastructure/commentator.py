from typing import Protocol


class Commentator(Protocol):
    def comment(self, page_id: str, message: str) -> None: ...
