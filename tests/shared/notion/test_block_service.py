from unittest.mock import MagicMock, patch

import pytest

from sandpiper.shared.notion.block_service import NotionBlockService, get_block_service


class TestNotionBlockService:
    """NotionBlockServiceのテスト"""

    @pytest.fixture
    def mock_notion_client(self):
        """notion_clientのモック"""
        with patch("sandpiper.shared.notion.block_service.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def block_service(self, mock_notion_client):
        """NotionBlockServiceのインスタンス"""
        return NotionBlockService()

    def test_init(self, mock_notion_client):
        """初期化のテスト"""
        service = NotionBlockService()
        assert service.client is not None

    def test_fetch_blocks_empty(self, block_service, mock_notion_client):
        """ブロックが空の場合のテスト"""
        mock_notion_client.blocks.children.list.return_value = {
            "results": [],
            "has_more": False,
        }

        blocks = block_service.fetch_blocks("test-page-id")
        assert blocks == []
        mock_notion_client.blocks.children.list.assert_called_once_with(
            block_id="test-page-id",
            start_cursor=None,
        )

    def test_fetch_blocks_single_paragraph(self, block_service, mock_notion_client):
        """単一のパラグラフブロックを取得するテスト"""
        mock_notion_client.blocks.children.list.return_value = {
            "results": [
                {
                    "id": "block-1",
                    "type": "paragraph",
                    "has_children": False,
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": "Hello"}}]
                    },
                }
            ],
            "has_more": False,
        }

        blocks = block_service.fetch_blocks("test-page-id")
        assert len(blocks) == 1
        assert blocks[0]["type"] == "paragraph"
        assert blocks[0]["object"] == "block"

    def test_fetch_blocks_multiple_types(self, block_service, mock_notion_client):
        """複数タイプのブロックを取得するテスト"""
        mock_notion_client.blocks.children.list.return_value = {
            "results": [
                {
                    "id": "block-1",
                    "type": "paragraph",
                    "has_children": False,
                    "paragraph": {"rich_text": []},
                },
                {
                    "id": "block-2",
                    "type": "heading_2",
                    "has_children": False,
                    "heading_2": {"rich_text": []},
                },
                {
                    "id": "block-3",
                    "type": "bulleted_list_item",
                    "has_children": False,
                    "bulleted_list_item": {"rich_text": []},
                },
            ],
            "has_more": False,
        }

        blocks = block_service.fetch_blocks("test-page-id")
        assert len(blocks) == 3
        assert blocks[0]["type"] == "paragraph"
        assert blocks[1]["type"] == "heading_2"
        assert blocks[2]["type"] == "bulleted_list_item"

    def test_fetch_blocks_pagination(self, block_service, mock_notion_client):
        """ページネーションのテスト"""
        mock_notion_client.blocks.children.list.side_effect = [
            {
                "results": [
                    {
                        "id": "block-1",
                        "type": "paragraph",
                        "has_children": False,
                        "paragraph": {"rich_text": []},
                    }
                ],
                "has_more": True,
                "next_cursor": "cursor-1",
            },
            {
                "results": [
                    {
                        "id": "block-2",
                        "type": "paragraph",
                        "has_children": False,
                        "paragraph": {"rich_text": []},
                    }
                ],
                "has_more": False,
            },
        ]

        blocks = block_service.fetch_blocks("test-page-id")
        assert len(blocks) == 2
        assert mock_notion_client.blocks.children.list.call_count == 2

    def test_fetch_blocks_with_children(self, block_service, mock_notion_client):
        """子ブロックを持つブロックの取得テスト"""
        mock_notion_client.blocks.children.list.side_effect = [
            # 親ブロックの取得
            {
                "results": [
                    {
                        "id": "parent-block",
                        "type": "toggle",
                        "has_children": True,
                        "toggle": {"rich_text": []},
                    }
                ],
                "has_more": False,
            },
            # 子ブロックの取得
            {
                "results": [
                    {
                        "id": "child-block",
                        "type": "paragraph",
                        "has_children": False,
                        "paragraph": {"rich_text": []},
                    }
                ],
                "has_more": False,
            },
        ]

        blocks = block_service.fetch_blocks("test-page-id")
        assert len(blocks) == 1
        assert blocks[0]["type"] == "toggle"
        assert "children" in blocks[0]["toggle"]
        assert len(blocks[0]["toggle"]["children"]) == 1

    def test_clean_block_for_copy_removes_metadata(self, block_service):
        """メタデータが除去されることをテスト"""
        block = {
            "id": "should-be-removed",
            "type": "paragraph",
            "has_children": False,
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "paragraph": {"rich_text": []},
        }

        cleaned = block_service._clean_block_for_copy(block)
        assert "id" not in cleaned
        assert "created_time" not in cleaned
        assert "last_edited_time" not in cleaned
        assert cleaned["type"] == "paragraph"
        assert cleaned["object"] == "block"

    def test_clean_block_for_copy_invalid_block(self, block_service):
        """不正なブロックの処理テスト"""
        block = {"invalid": "block"}
        result = block_service._clean_block_for_copy(block)
        assert result is None

    def test_copy_blocks_empty(self, block_service, mock_notion_client):
        """空のブロックのコピーテスト"""
        mock_notion_client.blocks.children.list.return_value = {
            "results": [],
            "has_more": False,
        }

        count = block_service.copy_blocks("source-id", "target-id")
        assert count == 0
        mock_notion_client.blocks.children.append.assert_not_called()

    def test_copy_blocks_success(self, block_service, mock_notion_client):
        """ブロックのコピー成功テスト"""
        mock_notion_client.blocks.children.list.return_value = {
            "results": [
                {
                    "id": "block-1",
                    "type": "paragraph",
                    "has_children": False,
                    "paragraph": {"rich_text": []},
                },
                {
                    "id": "block-2",
                    "type": "heading_2",
                    "has_children": False,
                    "heading_2": {"rich_text": []},
                },
            ],
            "has_more": False,
        }

        count = block_service.copy_blocks("source-id", "target-id")
        assert count == 2
        mock_notion_client.blocks.children.append.assert_called_once()

    def test_class_constants(self):
        """クラス定数のテスト"""
        assert "id" in NotionBlockService._EXCLUDED_FIELDS
        assert "parent" in NotionBlockService._EXCLUDED_FIELDS
        assert "paragraph" in NotionBlockService._BLOCK_TYPES_WITH_CHILDREN
        assert "toggle" in NotionBlockService._BLOCK_TYPES_WITH_CHILDREN
        assert "bulleted_list_item" in NotionBlockService._BLOCK_TYPES_WITH_CHILDREN


class TestGetBlockService:
    """get_block_service関数のテスト"""

    def test_get_block_service_singleton(self):
        """シングルトンパターンのテスト"""
        with patch("sandpiper.shared.notion.block_service.Client"):
            # グローバル変数をリセット
            import sandpiper.shared.notion.block_service as bs

            bs._instance = None

            service1 = get_block_service()
            service2 = get_block_service()
            assert service1 is service2
