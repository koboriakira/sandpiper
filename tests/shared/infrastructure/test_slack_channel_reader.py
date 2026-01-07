from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from sandpiper.shared.infrastructure.slack_channel_reader import (
    SlackChannelReader,
    SlackMessage,
)


class TestSlackMessage:
    def test_from_api_response_full_data(self):
        """完全なAPIレスポンスからSlackMessageを生成"""
        # Arrange
        api_response = {
            "ts": "1704067200.000000",
            "text": "テストメッセージ",
            "user": "U1234567890",
        }

        # Act
        message = SlackMessage.from_api_response(api_response)

        # Assert
        assert message.ts == "1704067200.000000"
        assert message.text == "テストメッセージ"
        assert message.user == "U1234567890"
        assert message.timestamp == datetime.fromtimestamp(1704067200.0)

    def test_from_api_response_missing_user(self):
        """userがないAPIレスポンスを処理"""
        # Arrange
        api_response = {
            "ts": "1704067200.000000",
            "text": "ボットメッセージ",
        }

        # Act
        message = SlackMessage.from_api_response(api_response)

        # Assert
        assert message.ts == "1704067200.000000"
        assert message.text == "ボットメッセージ"
        assert message.user is None

    def test_from_api_response_empty_fields(self):
        """空のフィールドを処理"""
        # Arrange
        api_response = {}

        # Act
        message = SlackMessage.from_api_response(api_response)

        # Assert
        assert message.ts == ""
        assert message.text == ""
        assert message.user is None


class TestSlackChannelReader:
    def setup_method(self):
        self.test_token = "test-business-token"
        self.channel_id = "C02CVBZV0UB"

    @patch("sandpiper.shared.infrastructure.slack_channel_reader.WebClient")
    def test_init_with_token(self, mock_web_client):
        """トークン指定での初期化をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client

        # Act
        reader = SlackChannelReader(token=self.test_token)

        # Assert
        assert reader._channel_id == self.channel_id
        assert reader._client == mock_client
        mock_web_client.assert_called_once_with(token=self.test_token)

    @patch.dict("os.environ", {"SLACK_BOT_TOKEN_BUSINESS": "env-business-token"})
    @patch("sandpiper.shared.infrastructure.slack_channel_reader.WebClient")
    def test_init_with_env_token(self, mock_web_client):
        """環境変数からのトークン取得での初期化をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client

        # Act
        reader = SlackChannelReader()

        # Assert
        assert reader._channel_id == self.channel_id
        mock_web_client.assert_called_once_with(token="env-business-token")

    @patch("sandpiper.shared.infrastructure.slack_channel_reader.WebClient")
    def test_init_with_custom_channel(self, mock_web_client):
        """カスタムチャンネルIDでの初期化をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client
        custom_channel = "C99999999"

        # Act
        reader = SlackChannelReader(channel_id=custom_channel, token=self.test_token)

        # Assert
        assert reader._channel_id == custom_channel

    @patch("sandpiper.shared.infrastructure.slack_channel_reader.WebClient")
    def test_fetch_messages_success(self, mock_web_client):
        """メッセージ取得の成功をテスト"""
        # Arrange
        mock_client = Mock()
        mock_client.conversations_history.return_value = {
            "messages": [
                {"ts": "1704067200.000000", "text": "メッセージ1", "user": "U001"},
                {"ts": "1704067100.000000", "text": "メッセージ2", "user": "U002"},
            ]
        }
        mock_web_client.return_value = mock_client
        reader = SlackChannelReader(token=self.test_token)

        # Act
        messages = reader.fetch_messages(limit=10)

        # Assert
        assert len(messages) == 2
        assert messages[0].text == "メッセージ1"
        assert messages[1].text == "メッセージ2"
        mock_client.conversations_history.assert_called_once_with(channel=self.channel_id, limit=10)

    @patch("sandpiper.shared.infrastructure.slack_channel_reader.WebClient")
    def test_fetch_messages_with_time_range(self, mock_web_client):
        """時間範囲指定でのメッセージ取得をテスト"""
        # Arrange
        mock_client = Mock()
        mock_client.conversations_history.return_value = {"messages": []}
        mock_web_client.return_value = mock_client
        reader = SlackChannelReader(token=self.test_token)

        oldest = datetime(2024, 1, 1, 0, 0, 0)
        latest = datetime(2024, 1, 1, 23, 59, 59)

        # Act
        reader.fetch_messages(oldest=oldest, latest=latest)

        # Assert
        mock_client.conversations_history.assert_called_once_with(
            channel=self.channel_id,
            limit=100,
            oldest=str(oldest.timestamp()),
            latest=str(latest.timestamp()),
        )

    @patch("sandpiper.shared.infrastructure.slack_channel_reader.WebClient")
    def test_fetch_messages_empty(self, mock_web_client):
        """空のメッセージ取得をテスト"""
        # Arrange
        mock_client = Mock()
        mock_client.conversations_history.return_value = {"messages": []}
        mock_web_client.return_value = mock_client
        reader = SlackChannelReader(token=self.test_token)

        # Act
        messages = reader.fetch_messages()

        # Assert
        assert len(messages) == 0

    @patch("sandpiper.shared.infrastructure.slack_channel_reader.WebClient")
    def test_fetch_messages_for_date(self, mock_web_client):
        """特定日付のメッセージ取得をテスト"""
        # Arrange
        mock_client = Mock()
        mock_client.conversations_history.return_value = {
            "messages": [{"ts": "1704067200.000000", "text": "今日のメッセージ", "user": "U001"}]
        }
        mock_web_client.return_value = mock_client
        reader = SlackChannelReader(token=self.test_token)

        target_date = datetime(2024, 1, 1, 12, 0, 0)

        # Act
        messages = reader.fetch_messages_for_date(target_date)

        # Assert
        assert len(messages) == 1
        assert messages[0].text == "今日のメッセージ"
        # 日の開始と終了が正しく設定されていることを確認
        call_kwargs = mock_client.conversations_history.call_args.kwargs
        assert "oldest" in call_kwargs
        assert "latest" in call_kwargs

    @patch("sandpiper.shared.infrastructure.slack_channel_reader.WebClient")
    def test_fetch_messages_api_error(self, mock_web_client):
        """Slack API エラー時のテスト"""
        # Arrange
        from slack_sdk.errors import SlackApiError

        mock_client = Mock()
        mock_client.conversations_history.side_effect = SlackApiError(
            message="channel_not_found", response={"error": "channel_not_found"}
        )
        mock_web_client.return_value = mock_client
        reader = SlackChannelReader(token=self.test_token)

        # Act & Assert
        with pytest.raises(SlackApiError):
            reader.fetch_messages()

    @patch.dict("os.environ", {"CUSTOM_SLACK_TOKEN": "custom-token"})
    @patch("sandpiper.shared.infrastructure.slack_channel_reader.WebClient")
    def test_init_with_custom_env_var(self, mock_web_client):
        """カスタム環境変数での初期化をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client

        # Act
        _reader = SlackChannelReader(env_var="CUSTOM_SLACK_TOKEN")

        # Assert
        mock_web_client.assert_called_once_with(token="custom-token")

    def test_default_channel_id(self):
        """デフォルトチャンネルIDが正しいことをテスト"""
        # Assert
        assert SlackChannelReader.DEFAULT_CHANNEL_ID == "C02CVBZV0UB"

    def test_default_env_var(self):
        """デフォルト環境変数名が正しいことをテスト"""
        # Assert
        assert SlackChannelReader.DEFAULT_ENV_VAR == "SLACK_BOT_TOKEN_BUSINESS"
