"""ListUnprocessedClipsユースケースのテスト"""

from sandpiper.clips.application.list_unprocessed_clips import ListUnprocessedClips
from sandpiper.clips.query.unprocessed_clip_item import UnprocessedClipItem


class MockClipsQuery:
    """テスト用のClipsQueryモック"""

    def __init__(self, items: list[UnprocessedClipItem] | None = None) -> None:
        self._items = items or []

    def fetch_unprocessed(self) -> list[UnprocessedClipItem]:
        return self._items


class TestListUnprocessedClips:
    def test_returns_unprocessed_clips(self):
        """未処理Clipsがある場合はリストを返す"""
        items = [
            UnprocessedClipItem(title="記事1", url="https://example.com/1"),
            UnprocessedClipItem(title="記事2", url="https://example.com/2"),
        ]
        query = MockClipsQuery(items=items)
        use_case = ListUnprocessedClips(clips_query=query)

        result = use_case.execute()

        assert len(result) == 2
        assert result[0].title == "記事1"
        assert result[0].url == "https://example.com/1"
        assert result[1].title == "記事2"
        assert result[1].url == "https://example.com/2"

    def test_returns_empty_list_when_no_unprocessed_clips(self):
        """未処理Clipsがない場合は空リストを返す"""
        query = MockClipsQuery(items=[])
        use_case = ListUnprocessedClips(clips_query=query)

        result = use_case.execute()

        assert result == []
