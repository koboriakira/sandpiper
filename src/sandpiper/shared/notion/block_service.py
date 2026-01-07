"""Notionブロックの取得とコピー機能を提供するサービス"""

import os
from typing import Any, ClassVar

from notion_client import Client


class NotionBlockService:
    """Notionのページブロックを取得・コピーするサービス"""

    # コピー時に除外するメタデータフィールド
    _EXCLUDED_FIELDS: ClassVar[set[str]] = {
        "id",
        "parent",
        "created_time",
        "last_edited_time",
        "created_by",
        "last_edited_by",
        "has_children",
        "archived",
        "in_trash",
    }

    # 子ブロックを持つことができるブロックタイプ
    _BLOCK_TYPES_WITH_CHILDREN: ClassVar[set[str]] = {
        "paragraph",
        "bulleted_list_item",
        "numbered_list_item",
        "toggle",
        "quote",
        "callout",
        "synced_block",
        "template",
        "column",
        "column_list",
        "table",
    }

    def __init__(self) -> None:
        self.client = Client(auth=os.environ.get("NOTION_TOKEN"))

    def fetch_blocks(self, page_id: str) -> list[dict[str, Any]]:
        """ページ内のブロックを再帰的に取得する"""
        blocks: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            response: dict[str, Any] = self.client.blocks.children.list(  # type: ignore[assignment]
                block_id=page_id,
                start_cursor=cursor,
            )
            for block in response.get("results", []):
                block_data = self._clean_block_for_copy(block)
                if block_data:
                    blocks.append(block_data)

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        return blocks

    def _clean_block_for_copy(self, block: dict[str, Any]) -> dict[str, Any] | None:
        """ブロックをコピー用にクリーンアップする(メタデータを除去)"""
        block_type = block.get("type")
        if not block_type:
            return None

        # 基本的なブロック構造を作成
        cleaned: dict[str, Any] = {
            "object": "block",
            "type": block_type,
        }

        # ブロックタイプ固有のコンテンツをコピー
        if block_type in block:
            content = block[block_type].copy()

            # 子ブロックがある場合は再帰的に取得してコピー
            if block.get("has_children") and block_type in self._BLOCK_TYPES_WITH_CHILDREN:
                children = self._fetch_children_blocks(block["id"])
                if children:
                    content["children"] = children

            cleaned[block_type] = content

        return cleaned

    def _fetch_children_blocks(self, block_id: str) -> list[dict[str, Any]]:
        """子ブロックを再帰的に取得する"""
        children: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            response: dict[str, Any] = self.client.blocks.children.list(  # type: ignore[assignment]
                block_id=block_id,
                start_cursor=cursor,
            )
            for block in response.get("results", []):
                block_data = self._clean_block_for_copy(block)
                if block_data:
                    children.append(block_data)

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        return children

    def copy_blocks(self, source_page_id: str, target_page_id: str) -> int:
        """ソースページのブロックをターゲットページにコピーする

        Args:
            source_page_id: コピー元のページID
            target_page_id: コピー先のページID

        Returns:
            コピーされたブロック数
        """
        blocks = self.fetch_blocks(source_page_id)
        if not blocks:
            return 0

        # Notion APIの制限: 1回のリクエストで最大100ブロックまで
        batch_size = 100
        copied_count = 0

        for i in range(0, len(blocks), batch_size):
            batch = blocks[i : i + batch_size]
            self.client.blocks.children.append(
                block_id=target_page_id,
                children=batch,
            )
            copied_count += len(batch)

        return copied_count


# シングルトンインスタンス
_instance: NotionBlockService | None = None


def get_block_service() -> NotionBlockService:
    """NotionBlockServiceのシングルトンインスタンスを取得する"""
    global _instance
    if _instance is None:
        _instance = NotionBlockService()
    return _instance
