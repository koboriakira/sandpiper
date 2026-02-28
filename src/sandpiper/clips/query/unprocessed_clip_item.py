from dataclasses import dataclass


@dataclass(frozen=True)
class UnprocessedClipItem:
    """未処理Clip一覧表示用のDTO"""

    title: str
    url: str
