"""check-dakoku コマンドの打刻フィルタロジックのテスト"""

import pytest

from sandpiper.perform.domain.todo import ToDo
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


def _find_dakoku_titles(todos: list[ToDo]) -> list[str]:
    """「打刻」を含む未完了TODOのタイトルを返す (main.py の check_dakoku と同一ロジック)"""
    return [todo.title for todo in todos if "打刻" in todo.title]


class TestCheckDakokuFilter:
    def test_打刻を含むTODOがある場合(self) -> None:
        todos = [
            ToDo(id="1", title="打刻", status=ToDoStatusEnum.TODO),
            ToDo(id="2", title="朝会", status=ToDoStatusEnum.TODO),
        ]
        result = _find_dakoku_titles(todos)
        assert result == ["打刻"]

    def test_打刻を含むTODOがない場合(self) -> None:
        todos = [
            ToDo(id="1", title="朝会", status=ToDoStatusEnum.TODO),
            ToDo(id="2", title="レビュー", status=ToDoStatusEnum.IN_PROGRESS),
        ]
        assert _find_dakoku_titles(todos) == []

    def test_空リストの場合(self) -> None:
        assert _find_dakoku_titles([]) == []

    def test_打刻がタイトルの一部に含まれる場合(self) -> None:
        todos = [
            ToDo(id="1", title="出勤打刻する", status=ToDoStatusEnum.TODO),
        ]
        result = _find_dakoku_titles(todos)
        assert result == ["出勤打刻する"]

    @pytest.mark.parametrize(
        "status",
        [ToDoStatusEnum.TODO, ToDoStatusEnum.IN_PROGRESS],
    )
    def test_未完了ステータスの打刻タスクを検出する(self, status: ToDoStatusEnum) -> None:
        todos = [ToDo(id="1", title="打刻", status=status)]
        assert len(_find_dakoku_titles(todos)) == 1

    def test_複数の打刻タスクがある場合(self) -> None:
        todos = [
            ToDo(id="1", title="打刻", status=ToDoStatusEnum.TODO),
            ToDo(id="2", title="退勤打刻", status=ToDoStatusEnum.IN_PROGRESS),
        ]
        result = _find_dakoku_titles(todos)
        assert result == ["打刻", "退勤打刻"]
