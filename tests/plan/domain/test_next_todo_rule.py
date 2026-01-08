from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from sandpiper.plan.domain.next_todo_rule import next_todo_rule
from sandpiper.plan.domain.todo import ToDoKind
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


class TestNextTodoRule:
    """next_todo_rule関数のテスト"""

    @pytest.mark.parametrize("title", ["洗濯"])
    def test_洗濯完了で乾燥機に入れるが作成される(self, title: str):
        # Arrange
        mock_now = datetime(2024, 3, 20, 10, 0)

        # Act
        with patch("sandpiper.plan.domain.next_todo_rule.jst_now", return_value=mock_now):
            result = next_todo_rule(title)

        # Assert
        assert result is not None
        assert result.title == "乾燥機に入れる"
        assert result.kind == ToDoKind.REPEAT
        expected_section = TaskChuteSection.new(mock_now + timedelta(minutes=30))
        assert result.section == expected_section

    @pytest.mark.parametrize("title", ["乾燥機に入れる"])
    def test_乾燥機に入れる完了で乾燥機から取り込むが作成される(self, title: str):
        # Arrange
        mock_now = datetime(2024, 3, 20, 10, 0)

        # Act
        with patch("sandpiper.plan.domain.next_todo_rule.jst_now", return_value=mock_now):
            result = next_todo_rule(title)

        # Assert
        assert result is not None
        assert result.title == "乾燥機から取り込む"
        assert result.kind == ToDoKind.REPEAT
        expected_section = TaskChuteSection.new(mock_now + timedelta(hours=6))
        assert result.section == expected_section

    @pytest.mark.parametrize("title", ["料理", "朝食", "昼食", "夕食"])
    def test_食事関連タスク完了で食器洗いが作成される(self, title: str):
        # Arrange
        mock_now = datetime(2024, 3, 20, 12, 0)

        # Act
        with patch("sandpiper.plan.domain.next_todo_rule.jst_now", return_value=mock_now):
            result = next_todo_rule(title)

        # Assert
        assert result is not None
        assert result.title == "食器洗い"
        assert result.kind == ToDoKind.REPEAT
        expected_section = TaskChuteSection.new(mock_now)
        assert result.section == expected_section

    @pytest.mark.parametrize("title", ["食器洗い"])
    def test_食器洗い完了で食器の片付けが作成される(self, title: str):
        # Arrange
        mock_now = datetime(2024, 3, 20, 12, 0)

        # Act
        with patch("sandpiper.plan.domain.next_todo_rule.jst_now", return_value=mock_now):
            result = next_todo_rule(title)

        # Assert
        assert result is not None
        assert result.title == "食器の片付け"
        assert result.kind == ToDoKind.REPEAT
        expected_section = TaskChuteSection.new(mock_now + timedelta(minutes=60))
        assert result.section == expected_section

    @pytest.mark.parametrize("title", ["会議", "ミーティング", "その他のタスク", ""])
    def test_ルールに該当しないタイトルはNoneを返す(self, title: str):
        # Act
        result = next_todo_rule(title)

        # Assert
        assert result is None

    def test_食器洗いのセクションは現在時刻で計算される(self):
        # Arrange: 朝7時に朝食完了
        mock_now = datetime(2024, 3, 20, 7, 30)

        # Act
        with patch("sandpiper.plan.domain.next_todo_rule.jst_now", return_value=mock_now):
            result = next_todo_rule("朝食")

        # Assert
        assert result is not None
        assert result.section == TaskChuteSection.A_07_10

    def test_食器の片付けのセクションは60分後で計算される(self):
        # Arrange: 12時に食器洗い完了 -> 13時(60分後)のセクション
        mock_now = datetime(2024, 3, 20, 12, 30)

        # Act
        with patch("sandpiper.plan.domain.next_todo_rule.jst_now", return_value=mock_now):
            result = next_todo_rule("食器洗い")

        # Assert
        assert result is not None
        # 12:30 + 60分 = 13:30 -> C_13_17セクション
        assert result.section == TaskChuteSection.C_13_17

    def test_食器の片付けのセクションが日跨ぎでも正しく計算される(self):
        # Arrange: 23時30分に食器洗い完了 -> 00時30分(60分後)のセクション
        mock_now = datetime(2024, 3, 20, 23, 30)

        # Act
        with patch("sandpiper.plan.domain.next_todo_rule.jst_now", return_value=mock_now):
            result = next_todo_rule("食器洗い")

        # Assert
        assert result is not None
        # 23:30 + 60分 = 00:30 -> G_24_07セクション
        assert result.section == TaskChuteSection.G_24_07
