from lotion import Lotion  # type: ignore[import-untyped]


class NotionCommentator:
    def __init__(self) -> None:
        self.client = Lotion.get_instance()

    def comment(self, page_id: str, message: str) -> None:
        self.client.append_comment(page_id, message)
