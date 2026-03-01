from dataclasses import dataclass

from sandpiper.clips.query.clips_query import ClipsQuery
from sandpiper.clips.query.unprocessed_clip_item import UnprocessedClipItem


@dataclass
class ListUnprocessedClips:
    _clips_query: ClipsQuery

    def __init__(self, clips_query: ClipsQuery) -> None:
        self._clips_query = clips_query

    def execute(self) -> list[UnprocessedClipItem]:
        """未処理のClips一覧を取得する"""
        return self._clips_query.fetch_unprocessed()
