from unittest.mock import Mock, patch

import pytest

from sandpiper.shared.infrastructure.notion_commentator import NotionCommentator


class TestNotionCommentator:
    @patch('sandpiper.shared.infrastructure.notion_commentator.Lotion')
    def test_init(self, mock_lotion_class):
        """NotionCommentatorの初期化をテスト"""
        # Arrange
        mock_client = Mock()
        mock_lotion_class.get_instance.return_value = mock_client

        # Act
        commentator = NotionCommentator()

        # Assert
        assert commentator.client == mock_client
        mock_lotion_class.get_instance.assert_called_once()

    @patch('sandpiper.shared.infrastructure.notion_commentator.Lotion')
    def test_comment_success(self, mock_lotion_class):
        """コメント投稿の成功をテスト"""
        # Arrange
        mock_client = Mock()
        mock_lotion_class.get_instance.return_value = mock_client
        commentator = NotionCommentator()

        page_id = "test-page-123"
        message = "テストコメント"

        # Act
        commentator.comment(page_id, message)

        # Assert
        mock_client.append_comment.assert_called_once_with(page_id, message)

    @patch('sandpiper.shared.infrastructure.notion_commentator.Lotion')
    def test_comment_empty_message(self, mock_lotion_class):
        """空のメッセージでのコメント投稿をテスト"""
        # Arrange
        mock_client = Mock()
        mock_lotion_class.get_instance.return_value = mock_client
        commentator = NotionCommentator()

        page_id = "test-page-empty"
        message = ""

        # Act
        commentator.comment(page_id, message)

        # Assert
        mock_client.append_comment.assert_called_once_with(page_id, message)

    @patch('sandpiper.shared.infrastructure.notion_commentator.Lotion')
    def test_comment_long_message(self, mock_lotion_class):
        """長いメッセージでのコメント投稿をテスト"""
        # Arrange
        mock_client = Mock()
        mock_lotion_class.get_instance.return_value = mock_client
        commentator = NotionCommentator()

        page_id = "test-page-long"
        message = "これは非常に長いテストコメントです。" * 100

        # Act
        commentator.comment(page_id, message)

        # Assert
        mock_client.append_comment.assert_called_once_with(page_id, message)

    @patch('sandpiper.shared.infrastructure.notion_commentator.Lotion')
    def test_comment_with_special_characters(self, mock_lotion_class):
        """特殊文字を含むメッセージでのコメント投稿をテスト"""
        # Arrange
        mock_client = Mock()
        mock_lotion_class.get_instance.return_value = mock_client
        commentator = NotionCommentator()

        page_id = "test-page-special"
        message = "特殊文字: @#$%^&*()_+{}|:<>?[]\\;'\",./"

        # Act
        commentator.comment(page_id, message)

        # Assert
        mock_client.append_comment.assert_called_once_with(page_id, message)

    @patch('sandpiper.shared.infrastructure.notion_commentator.Lotion')
    def test_comment_multiple_calls(self, mock_lotion_class):
        """複数回のコメント投稿をテスト"""
        # Arrange
        mock_client = Mock()
        mock_lotion_class.get_instance.return_value = mock_client
        commentator = NotionCommentator()

        # Act
        commentator.comment("page-1", "メッセージ1")
        commentator.comment("page-2", "メッセージ2")
        commentator.comment("page-3", "メッセージ3")

        # Assert
        assert mock_client.append_comment.call_count == 3
        mock_client.append_comment.assert_any_call("page-1", "メッセージ1")
        mock_client.append_comment.assert_any_call("page-2", "メッセージ2")
        mock_client.append_comment.assert_any_call("page-3", "メッセージ3")

    @patch('sandpiper.shared.infrastructure.notion_commentator.Lotion')
    def test_comment_with_api_error(self, mock_lotion_class):
        """Notion API エラー時のテスト"""
        # Arrange
        mock_client = Mock()
        mock_client.append_comment.side_effect = Exception("Notion API error")
        mock_lotion_class.get_instance.return_value = mock_client
        commentator = NotionCommentator()

        # Act & Assert
        with pytest.raises(Exception, match="Notion API error"):
            commentator.comment("error-page", "エラーテストメッセージ")

        mock_client.append_comment.assert_called_once()

    @patch('sandpiper.shared.infrastructure.notion_commentator.Lotion')
    def test_client_reuse(self, mock_lotion_class):
        """クライアントインスタンスが再利用されることをテスト"""
        # Arrange
        mock_client = Mock()
        mock_lotion_class.get_instance.return_value = mock_client

        # Act
        commentator1 = NotionCommentator()
        commentator2 = NotionCommentator()

        # Assert
        # get_instanceは各インスタンス作成時に呼ばれる
        assert mock_lotion_class.get_instance.call_count == 2
        assert commentator1.client == mock_client
        assert commentator2.client == mock_client

    @patch('sandpiper.shared.infrastructure.notion_commentator.Lotion')
    def test_comment_parameter_validation(self, mock_lotion_class):
        """コメント投稿時のパラメータ検証をテスト"""
        # Arrange
        mock_client = Mock()
        mock_lotion_class.get_instance.return_value = mock_client
        commentator = NotionCommentator()

        # Act
        commentator.comment("test-page", "test-message")

        # Assert
        # 正確なパラメータで呼び出されることを確認
        args, kwargs = mock_client.append_comment.call_args
        assert args[0] == "test-page"
        assert args[1] == "test-message"
