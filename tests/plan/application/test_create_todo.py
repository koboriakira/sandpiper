from unittest.mock import Mock

from sandpiper.app.message_dispatcher import MessageDispatcher
from sandpiper.plan.application.create_todo import CreateNewToDoRequest, CreateToDo
from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.plan.domain.todo_repository import TodoRepository
from sandpiper.shared.event.todo_created import TodoCreated
from sandpiper.shared.valueobject.task_chute_section import TaskChuteSection


class TestCreateToDo:
    def setup_method(self):
        self.mock_dispatcher = Mock(spec=MessageDispatcher)
        self.mock_repository = Mock(spec=TodoRepository)
        self.create_todo = CreateToDo(self.mock_dispatcher, self.mock_repository)

    def test_create_todo_basic(self):
        # Arrange
        mock_todo = Mock(spec=ToDo)
        mock_todo.id = "test-id-123"
        self.mock_repository.save.return_value = mock_todo

        request = CreateNewToDoRequest(title="テストタスク")

        # Act
        self.create_todo.execute(request)

        # Assert
        self.mock_repository.save.assert_called_once()
        saved_todo_arg = self.mock_repository.save.call_args[0][0]
        assert saved_todo_arg.title == "テストタスク"
        assert saved_todo_arg.kind is None
        assert saved_todo_arg.section is None

    def test_create_todo_with_kind_and_section(self):
        # Arrange
        mock_todo = Mock(spec=ToDo)
        mock_todo.id = "test-id-123"
        self.mock_repository.save.return_value = mock_todo

        request = CreateNewToDoRequest(
            title="プロジェクトタスク", kind=ToDoKind.PROJECT, section=TaskChuteSection.B_10_13
        )

        # Act
        self.create_todo.execute(request)

        # Assert
        self.mock_repository.save.assert_called_once()
        saved_todo_arg = self.mock_repository.save.call_args[0][0]
        assert saved_todo_arg.title == "プロジェクトタスク"
        assert saved_todo_arg.kind == ToDoKind.PROJECT
        assert saved_todo_arg.section == TaskChuteSection.B_10_13

    def test_create_todo_with_enable_start_false(self):
        # Arrange
        mock_todo = Mock(spec=ToDo)
        mock_todo.id = "test-id-123"
        self.mock_repository.save.return_value = mock_todo

        request = CreateNewToDoRequest(title="タスク")

        # Act
        self.create_todo.execute(request, enableStart=False)

        # Assert
        self.mock_repository.save.assert_called_once()
        self.mock_dispatcher.publish.assert_not_called()

    def test_create_todo_with_enable_start_true(self):
        # Arrange
        mock_todo = Mock(spec=ToDo)
        mock_todo.id = "test-id-123"
        self.mock_repository.save.return_value = mock_todo

        request = CreateNewToDoRequest(title="開始するタスク")

        # Act
        self.create_todo.execute(request, enableStart=True)

        # Assert
        self.mock_repository.save.assert_called_once()
        self.mock_dispatcher.publish.assert_called_once()

        # TodoCreatedイベントが正しく発行されることを確認
        published_event = self.mock_dispatcher.publish.call_args[0][0]
        assert isinstance(published_event, TodoCreated)
        assert published_event.page_id == "test-id-123"

    def test_create_todo_repository_save_called_with_correct_todo(self):
        # Arrange
        mock_todo = Mock(spec=ToDo)
        mock_todo.id = "test-id-456"
        self.mock_repository.save.return_value = mock_todo

        request = CreateNewToDoRequest(title="詳細タスク", kind=ToDoKind.REPEAT, section=TaskChuteSection.E_19_22)

        # Act
        self.create_todo.execute(request)

        # Assert
        self.mock_repository.save.assert_called_once()
        saved_todo = self.mock_repository.save.call_args[0][0]
        assert isinstance(saved_todo, ToDo)
        assert saved_todo.title == "詳細タスク"
        assert saved_todo.kind == ToDoKind.REPEAT
        assert saved_todo.section == TaskChuteSection.E_19_22

    def test_init_method(self):
        # Arrange & Act
        mock_dispatcher = Mock(spec=MessageDispatcher)
        mock_repository = Mock(spec=TodoRepository)

        create_todo = CreateToDo(mock_dispatcher, mock_repository)

        # Assert
        assert create_todo._dispatcher == mock_dispatcher
        assert create_todo._todo_repository == mock_repository


class TestCreateNewToDoRequest:
    def test_create_request_with_defaults(self):
        # Act
        request = CreateNewToDoRequest(title="基本タスク")

        # Assert
        assert request.title == "基本タスク"
        assert request.kind is None
        assert request.section is None

    def test_create_request_with_all_fields(self):
        # Act
        request = CreateNewToDoRequest(title="完全タスク", kind=ToDoKind.PROJECT, section=TaskChuteSection.C_13_17)

        # Assert
        assert request.title == "完全タスク"
        assert request.kind == ToDoKind.PROJECT
        assert request.section == TaskChuteSection.C_13_17
