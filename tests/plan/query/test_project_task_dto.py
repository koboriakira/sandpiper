from sandpiper.plan.domain.todo import ToDo, ToDoKind
from sandpiper.plan.query.project_task_dto import ProjectTaskDto
from sandpiper.shared.valueobject.todo_status_enum import ToDoStatusEnum


class TestProjectTaskDto:
    def test_project_task_dto_creation(self):
        """ProjectTaskDtoの基本的な作成をテスト"""
        # Arrange & Act
        dto = ProjectTaskDto(
            page_id="task-page-123",
            title="プロジェクトタスク",
            status=ToDoStatusEnum.TODO,
            project_page_id="project-page-456",
            is_next=True,
        )

        # Assert
        assert dto.page_id == "task-page-123"
        assert dto.title == "プロジェクトタスク"
        assert dto.status == ToDoStatusEnum.TODO
        assert dto.project_page_id == "project-page-456"
        assert dto.is_next is True

    def test_project_task_dto_dataclass_fields(self):
        """ProjectTaskDtoがdataclassとして正しく定義されていることをテスト"""
        # Arrange
        dto = ProjectTaskDto(
            page_id="test-page",
            title="テストタスク",
            status=ToDoStatusEnum.IN_PROGRESS,
            project_page_id="test-project",
            is_next=False,
        )

        # Assert
        assert hasattr(dto, "__dataclass_fields__")
        expected_fields = {
            "page_id",
            "title",
            "status",
            "project_page_id",
            "is_next",
            "block_children",
            "context",
            "sort_order",
            "is_work_project",
        }
        actual_fields = set(dto.__dataclass_fields__.keys())
        assert actual_fields == expected_fields

    def test_project_task_dto_is_work_project_default(self):
        """is_work_projectフィールドのデフォルト値がFalseであることをテスト"""
        # Arrange & Act
        dto = ProjectTaskDto(
            page_id="task-page-123",
            title="プロジェクトタスク",
            status=ToDoStatusEnum.TODO,
            project_page_id="project-page-456",
            is_next=True,
        )

        # Assert
        assert dto.is_work_project is False

    def test_project_task_dto_is_work_project_true(self):
        """is_work_project=Trueでの作成をテスト"""
        # Arrange & Act
        dto = ProjectTaskDto(
            page_id="task-page-123",
            title="仕事プロジェクトタスク",
            status=ToDoStatusEnum.TODO,
            project_page_id="project-page-456",
            is_next=True,
            is_work_project=True,
        )

        # Assert
        assert dto.is_work_project is True

    def test_to_todo_model(self):
        """to_todo_model()メソッドの基本的な動作をテスト"""
        # Arrange
        dto = ProjectTaskDto(
            page_id="task-123",
            title="変換テストタスク",
            status=ToDoStatusEnum.DONE,
            project_page_id="project-789",
            is_next=False,
        )

        # Act
        todo = dto.to_todo_model()

        # Assert
        assert isinstance(todo, ToDo)
        assert todo.title == "変換テストタスク"
        assert todo.section is None
        assert todo.kind == ToDoKind.PROJECT
        assert todo.project_page_id == "project-789"
        assert todo.project_task_page_id == "task-123"

    def test_to_todo_model_different_statuses(self):
        """異なるステータスでのto_todo_model()をテスト"""
        # 複数のステータスをテスト
        test_cases = [ToDoStatusEnum.TODO, ToDoStatusEnum.IN_PROGRESS, ToDoStatusEnum.DONE]

        for status in test_cases:
            # Arrange
            dto = ProjectTaskDto(
                page_id=f"task-{status.value}",
                title=f"タスク-{status.value}",
                status=status,
                project_page_id="project-test",
                is_next=True,
            )

            # Act
            todo = dto.to_todo_model()

            # Assert
            assert todo.title == f"タスク-{status.value}"
            assert todo.kind == ToDoKind.PROJECT
            assert todo.project_page_id == "project-test"
            assert todo.project_task_page_id == f"task-{status.value}"

    def test_to_todo_model_with_is_next_variations(self):
        """is_nextフィールドの異なる値でのto_todo_model()をテスト"""
        # is_nextの値をテスト(ToDoモデルには影響しないが、DTOの動作確認)
        test_cases = [True, False]

        for is_next in test_cases:
            # Arrange
            dto = ProjectTaskDto(
                page_id="task-next-test",
                title="Next フラグテスト",
                status=ToDoStatusEnum.TODO,
                project_page_id="project-next",
                is_next=is_next,
            )

            # Act
            todo = dto.to_todo_model()

            # Assert
            assert todo.title == "Next フラグテスト"
            assert todo.kind == ToDoKind.PROJECT
            # is_nextフィールドはToDoDTOには影響しないが、変換は正常に行われる
            assert dto.is_next == is_next

    def test_to_todo_model_preserves_ids(self):
        """to_todo_model()がIDを正しく保持することをテスト"""
        # Arrange
        dto = ProjectTaskDto(
            page_id="unique-task-id",
            title="ID保持テスト",
            status=ToDoStatusEnum.IN_PROGRESS,
            project_page_id="unique-project-id",
            is_next=True,
        )

        # Act
        todo = dto.to_todo_model()

        # Assert
        assert todo.project_page_id == "unique-project-id"
        assert todo.project_task_page_id == "unique-task-id"
        # 元のDTOのIDは変更されない
        assert dto.page_id == "unique-task-id"
        assert dto.project_page_id == "unique-project-id"

    def test_equality(self):
        """ProjectTaskDtoの等価性をテスト"""
        # Arrange
        dto1 = ProjectTaskDto(
            page_id="same-id",
            title="同じタスク",
            status=ToDoStatusEnum.TODO,
            project_page_id="same-project",
            is_next=True,
        )

        dto2 = ProjectTaskDto(
            page_id="same-id",
            title="同じタスク",
            status=ToDoStatusEnum.TODO,
            project_page_id="same-project",
            is_next=True,
        )

        # Assert
        assert dto1 == dto2

    def test_inequality(self):
        """ProjectTaskDtoの非等価性をテスト"""
        # Arrange
        dto1 = ProjectTaskDto(
            page_id="id-1", title="タスク1", status=ToDoStatusEnum.TODO, project_page_id="project-1", is_next=True
        )

        dto2 = ProjectTaskDto(
            page_id="id-2",
            title="タスク2",
            status=ToDoStatusEnum.IN_PROGRESS,
            project_page_id="project-2",
            is_next=False,
        )

        # Assert
        assert dto1 != dto2

    def test_to_todo_model_with_empty_strings(self):
        """空文字列でのto_todo_model()をテスト"""
        # Arrange
        dto = ProjectTaskDto(page_id="", title="", status=ToDoStatusEnum.TODO, project_page_id="", is_next=False)

        # Act
        todo = dto.to_todo_model()

        # Assert
        assert todo.title == ""
        assert todo.project_page_id == ""
        assert todo.project_task_page_id == ""
        assert todo.kind == ToDoKind.PROJECT
        assert todo.section is None
