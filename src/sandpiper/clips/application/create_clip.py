from dataclasses import dataclass

from sandpiper.clips.domain.clip import Clip, InsertedClip
from sandpiper.clips.domain.clips_repository import ClipsRepository


@dataclass
class CreateClipRequest:
    title: str
    url: str


@dataclass
class CreateClip:
    _clips_repository: ClipsRepository

    def __init__(self, clips_repository: ClipsRepository) -> None:
        self._clips_repository = clips_repository

    def execute(self, request: CreateClipRequest) -> InsertedClip:
        clip = Clip(title=request.title, url=request.url)
        inserted_clip = self._clips_repository.save(clip)
        print(f"Created Clip: {inserted_clip}")
        return inserted_clip
