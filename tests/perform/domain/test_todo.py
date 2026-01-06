from datetime import datetime
from unittest.mock import patch

from sandpiper.perform.domain.todo import ToDo
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TestToDo:
    def test_todo_creation(self):
        """ToDoの基本的な作成をテスト"""
        # Arrange & Act
        todo = ToDo(id="test-todo-1", title="テストタスク", status=ToDoStatusEnum.TODO)

        # Assert
        assert todo.id == "test-todo-1"
        assert todo.title == "テストタスク"
        assert todo.status == ToDoStatusEnum.TODO
        assert todo.section is None
        assert todo.log_start_datetime is None
        assert todo.log_end_datetime is None

    def test_todo_creation_with_optional_fields(self):
        """オプショナルフィールド付きでのToDo作成をテスト"""
        # Arrange
        test_datetime = datetime(2024, 1, 15, 10, 30)

        # Act
        todo = ToDo(
            id="test-todo-2",
            title="詳細テストタスク",
            status=ToDoStatusEnum.IN_PROGRESS,
            section=TaskChuteSection.A_07_10,
            log_start_datetime=test_datetime,
            log_end_datetime=None,
        )

        # Assert
        assert todo.id == "test-todo-2"
        assert todo.title == "詳細テストタスク"
        assert todo.status == ToDoStatusEnum.IN_PROGRESS
        assert todo.section == TaskChuteSection.A_07_10
        assert todo.log_start_datetime == test_datetime
        assert todo.log_end_datetime is None

    @patch("sandpiper.perform.domain.todo.jst_now")
    @patch("sandpiper.shared.valueobject.task_chute_section.TaskChuteSection.new")
    def test_start(self, mock_section_new, mock_jst_now):
        """ToDoのstart()メソッドをテスト"""
        # Arrange
        mock_current_time = datetime(2024, 1, 15, 9, 0)
        mock_new_section = TaskChuteSection.A_07_10
        mock_jst_now.return_value = mock_current_time
        mock_section_new.return_value = mock_new_section

        todo = ToDo(id="start-test", title="開始テスト", status=ToDoStatusEnum.TODO)

        # Act
        todo.start()

        # Assert
        assert todo.status == ToDoStatusEnum.IN_PROGRESS
        assert todo.section == mock_new_section
        assert todo.log_start_datetime == mock_current_time
        assert todo.log_end_datetime is None

        # モックの呼び出し確認
        mock_jst_now.assert_called_once()
        mock_section_new.assert_called_once()

    @patch("sandpiper.perform.domain.todo.jst_now")
    def test_complete(self, mock_jst_now):
        """ToDoのcomplete()メソッドをテスト"""
        # Arrange
        mock_completion_time = datetime(2024, 1, 15, 12, 0)
        mock_jst_now.return_value = mock_completion_time

        todo = ToDo(
            id="complete-test",
            title="完了テスト",
            status=ToDoStatusEnum.IN_PROGRESS,
            section=TaskChuteSection.B_10_13,
            log_start_datetime=datetime(2024, 1, 15, 10, 0),
        )

        # Act
        todo.complete()

        # Assert
        assert todo.status == ToDoStatusEnum.DONE
        assert todo.log_end_datetime == mock_completion_time
        # 他のフィールドは変更されない
        assert todo.id == "complete-test"
        assert todo.title == "完了テスト"
        assert todo.section == TaskChuteSection.B_10_13
        assert todo.log_start_datetime == datetime(2024, 1, 15, 10, 0)

        # モックの呼び出し確認
        mock_jst_now.assert_called_once()

    def test_todo_dataclass_fields(self):
        """ToDoがdataclassとして正しく定義されていることをテスト"""
        # Arrange
        todo = ToDo(id="dataclass-test", title="データクラステスト", status=ToDoStatusEnum.TODO)

        # Assert
        assert hasattr(todo, "__dataclass_fields__")
        expected_fields = {
            "id",
            "title",
            "status",
            "section",
            "log_start_datetime",
            "log_end_datetime",
            "project_task_page_id",
        }
        actual_fields = set(todo.__dataclass_fields__.keys())
        assert actual_fields == expected_fields

    def test_todo_equality(self):
        """同じ内容のToDoが等しいことをテスト"""
        # Arrange
        todo1 = ToDo(id="equal-test", title="等価テスト", status=ToDoStatusEnum.TODO)

        todo2 = ToDo(id="equal-test", title="等価テスト", status=ToDoStatusEnum.TODO)

        # Assert
        assert todo1 == todo2

    def test_todo_inequality(self):
        """異なる内容のToDoが等しくないことをテスト"""
        # Arrange
        todo1 = ToDo(id="different-test-1", title="異なるテスト1", status=ToDoStatusEnum.TODO)

        todo2 = ToDo(id="different-test-2", title="異なるテスト2", status=ToDoStatusEnum.IN_PROGRESS)

        # Assert
        assert todo1 != todo2

    @patch("sandpiper.perform.domain.todo.jst_now")
    @patch("sandpiper.shared.valueobject.task_chute_section.TaskChuteSection.new")
    def test_start_and_complete_workflow(self, mock_section_new, mock_jst_now):
        """ToDoの開始から完了までのワークフローをテスト"""
        # Arrange
        start_time = datetime(2024, 1, 15, 9, 0)
        complete_time = datetime(2024, 1, 15, 12, 0)
        test_section = TaskChuteSection.C_13_17

        mock_section_new.return_value = test_section
        mock_jst_now.side_effect = [start_time, complete_time]

        todo = ToDo(id="workflow-test", title="ワークフローテスト", status=ToDoStatusEnum.TODO)

        # Act - 開始
        todo.start()

        # Assert - 開始後の状態
        assert todo.status == ToDoStatusEnum.IN_PROGRESS
        assert todo.section == test_section
        assert todo.log_start_datetime == start_time
        assert todo.log_end_datetime is None

        # Act - 完了
        todo.complete()

        # Assert - 完了後の状態
        assert todo.status == ToDoStatusEnum.DONE
        assert todo.section == test_section  # セクションは変更されない
        assert todo.log_start_datetime == start_time  # 開始時刻は変更されない
        assert todo.log_end_datetime == complete_time

        # モック呼び出し確認
        assert mock_jst_now.call_count == 2
        mock_section_new.assert_called_once()

    def test_todo_mutable_behavior(self):
        """ToDoのミュータブルな動作をテスト"""
        # Arrange
        original_todo = ToDo(id="mutable-test", title="ミュータブルテスト", status=ToDoStatusEnum.TODO)

        # オリジナルの状態を記録
        original_status = original_todo.status
        original_section = original_todo.section
        original_start_time = original_todo.log_start_datetime

        # Act - start()を呼び出し、元のオブジェクトが変更されることを確認
        with (
            patch("sandpiper.perform.domain.todo.jst_now") as mock_jst_now,
            patch("sandpiper.shared.valueobject.task_chute_section.TaskChuteSection.new") as mock_section_new,
        ):
            mock_time = datetime(2024, 1, 15, 10, 0)
            mock_section = TaskChuteSection.B_10_13
            mock_jst_now.return_value = mock_time
            mock_section_new.return_value = mock_section

            original_todo.start()

        # Assert - オリジナルオブジェクトが変更された
        assert original_todo.status != original_status
        assert original_todo.section != original_section
        assert original_todo.log_start_datetime != original_start_time
        assert original_todo.status == ToDoStatusEnum.IN_PROGRESS
        assert original_todo.section == mock_section
        assert original_todo.log_start_datetime == mock_time
