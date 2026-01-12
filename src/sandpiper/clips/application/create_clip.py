from dataclasses import dataclass

from sandpiper.clips.domain.clip import Clip, InsertedClip
from sandpiper.clips.domain.clips_repository import ClipsRepository
from sandpiper.shared.notion.databases.inbox import InboxType


@dataclass
class CreateClipRequest:
    title: str
    url: str


def _detect_inbox_type(url: str) -> InboxType:
    """URLからInboxTypeを判別する。"""
    if "youtube.com" in url or "youtu.be" in url:
        return InboxType.VIDEO
    return InboxType.WEB


@dataclass
class CreateClip:
    _clips_repository: ClipsRepository

    def __init__(self, clips_repository: ClipsRepository) -> None:
        self._clips_repository = clips_repository

    def execute(self, request: CreateClipRequest) -> InsertedClip:
        inbox_type = _detect_inbox_type(request.url)
        clip = Clip(title=request.title, url=request.url, inbox_type=inbox_type)
        inserted_clip = self._clips_repository.save(clip)
        print(f"Created Clip: {inserted_clip}")
        return inserted_clip
