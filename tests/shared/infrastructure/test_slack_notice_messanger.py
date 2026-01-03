from unittest.mock import Mock, patch

import pytest

from sandpiper.shared.infrastructure.slack_notice_messanger import SlackNoticeMessanger


class TestSlackNoticeMessanger:
    def setup_method(self):
        self.channel_id = "test-channel"
        self.test_token = "test-token"

    @patch('sandpiper.shared.infrastructure.slack_notice_messanger.WebClient')
    def test_init_with_token(self, mock_web_client):
        """トークン指定での初期化をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client

        # Act
        messanger = SlackNoticeMessanger(self.channel_id, self.test_token)

        # Assert
        assert messanger._channel_id == self.channel_id
        assert messanger._client == mock_client
        mock_web_client.assert_called_once_with(token=self.test_token)

    @patch.dict('os.environ', {'SLACK_BOT_TOKEN': 'env-token'})
    @patch('sandpiper.shared.infrastructure.slack_notice_messanger.WebClient')
    def test_init_with_env_token(self, mock_web_client):
        """環境変数からのトークン取得での初期化をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client

        # Act
        messanger = SlackNoticeMessanger(self.channel_id)

        # Assert
        assert messanger._channel_id == self.channel_id
        assert messanger._client == mock_client
        mock_web_client.assert_called_once_with(token='env-token')

    @patch.dict('os.environ', {}, clear=True)  # 環境変数をクリア
    @patch('sandpiper.shared.infrastructure.slack_notice_messanger.WebClient')
    def test_init_with_no_token(self, mock_web_client):
        """トークンなしでの初期化をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client

        # Act
        messanger = SlackNoticeMessanger(self.channel_id)

        # Assert
        assert messanger._channel_id == self.channel_id
        assert messanger._client == mock_client
        mock_web_client.assert_called_once_with(token=None)

    @patch('sandpiper.shared.infrastructure.slack_notice_messanger.WebClient')
    def test_send_message_success(self, mock_web_client):
        """メッセージ送信の成功をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client
        messanger = SlackNoticeMessanger(self.channel_id, self.test_token)
        test_message = "テストメッセージ"

        # Act
        messanger.send(test_message)

        # Assert
        expected_text = "<@U04PQMBCFNE> テストメッセージ"
        mock_client.chat_postMessage.assert_called_once_with(
            channel=self.channel_id,
            text=expected_text
        )

    @patch('sandpiper.shared.infrastructure.slack_notice_messanger.WebClient')
    def test_send_empty_message(self, mock_web_client):
        """空のメッセージ送信をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client
        messanger = SlackNoticeMessanger(self.channel_id, self.test_token)

        # Act
        messanger.send("")

        # Assert
        expected_text = "<@U04PQMBCFNE> "
        mock_client.chat_postMessage.assert_called_once_with(
            channel=self.channel_id,
            text=expected_text
        )

    @patch('sandpiper.shared.infrastructure.slack_notice_messanger.WebClient')
    def test_send_long_message(self, mock_web_client):
        """長いメッセージ送信をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client
        messanger = SlackNoticeMessanger(self.channel_id, self.test_token)
        long_message = "これは非常に長いメッセージです。" * 100

        # Act
        messanger.send(long_message)

        # Assert
        expected_text = f"<@U04PQMBCFNE> {long_message}"
        mock_client.chat_postMessage.assert_called_once_with(
            channel=self.channel_id,
            text=expected_text
        )

    @patch('sandpiper.shared.infrastructure.slack_notice_messanger.WebClient')
    def test_send_message_with_special_characters(self, mock_web_client):
        """特殊文字を含むメッセージ送信をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client
        messanger = SlackNoticeMessanger(self.channel_id, self.test_token)
        special_message = "!@#$%^&*()_+{}|:<>?[]\\;'\",./"

        # Act
        messanger.send(special_message)

        # Assert
        expected_text = f"<@U04PQMBCFNE> {special_message}"
        mock_client.chat_postMessage.assert_called_once_with(
            channel=self.channel_id,
            text=expected_text
        )

    @patch('sandpiper.shared.infrastructure.slack_notice_messanger.WebClient')
    def test_send_multiple_messages(self, mock_web_client):
        """複数メッセージ送信をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client
        messanger = SlackNoticeMessanger(self.channel_id, self.test_token)

        # Act
        messanger.send("メッセージ1")
        messanger.send("メッセージ2")
        messanger.send("メッセージ3")

        # Assert
        assert mock_client.chat_postMessage.call_count == 3
        mock_client.chat_postMessage.assert_any_call(
            channel=self.channel_id,
            text="<@U04PQMBCFNE> メッセージ1"
        )
        mock_client.chat_postMessage.assert_any_call(
            channel=self.channel_id,
            text="<@U04PQMBCFNE> メッセージ2"
        )
        mock_client.chat_postMessage.assert_any_call(
            channel=self.channel_id,
            text="<@U04PQMBCFNE> メッセージ3"
        )

    @patch('sandpiper.shared.infrastructure.slack_notice_messanger.WebClient')
    def test_send_with_api_error(self, mock_web_client):
        """Slack API エラー時のテスト"""
        # Arrange
        mock_client = Mock()
        mock_client.chat_postMessage.side_effect = Exception("Slack API error")
        mock_web_client.return_value = mock_client
        messanger = SlackNoticeMessanger(self.channel_id, self.test_token)

        # Act & Assert
        with pytest.raises(Exception, match="Slack API error"):
            messanger.send("テストメッセージ")

        mock_client.chat_postMessage.assert_called_once()

    @patch('sandpiper.shared.infrastructure.slack_notice_messanger.WebClient')
    def test_mention_user_id_consistency(self, mock_web_client):
        """ユーザーIDメンションの一貫性をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client
        messanger = SlackNoticeMessanger(self.channel_id, self.test_token)

        # Act
        messanger.send("任意のメッセージ")

        # Assert
        # U04PQMBCFNE が一貫して使われることを確認
        expected_text = "<@U04PQMBCFNE> 任意のメッセージ"
        mock_client.chat_postMessage.assert_called_once_with(
            channel=self.channel_id,
            text=expected_text
        )

    @patch('sandpiper.shared.infrastructure.slack_notice_messanger.WebClient')
    def test_different_channels(self, mock_web_client):
        """異なるチャンネルでの動作をテスト"""
        # Arrange
        mock_client = Mock()
        mock_web_client.return_value = mock_client
        channel1 = "channel-1"
        channel2 = "channel-2"
        messanger1 = SlackNoticeMessanger(channel1, self.test_token)
        messanger2 = SlackNoticeMessanger(channel2, self.test_token)

        # Act
        messanger1.send("チャンネル1メッセージ")
        messanger2.send("チャンネル2メッセージ")

        # Assert
        assert mock_client.chat_postMessage.call_count == 2
        mock_client.chat_postMessage.assert_any_call(
            channel=channel1,
            text="<@U04PQMBCFNE> チャンネル1メッセージ"
        )
        mock_client.chat_postMessage.assert_any_call(
            channel=channel2,
            text="<@U04PQMBCFNE> チャンネル2メッセージ"
        )
