from datetime import date

from sandpiper.plan.domain.project import InsertedProject, Project


class TestProject:
    def test_project_creation_basic(self):
        # Arrange & Act
        project = Project(
            name="新しいプロジェクト",
            start_date=date(2024, 1, 1),
        )

        # Assert
        assert project.name == "新しいプロジェクト"
        assert project.start_date == date(2024, 1, 1)
        assert project.end_date is None

    def test_project_creation_with_end_date(self):
        # Arrange & Act
        project = Project(
            name="期限付きプロジェクト",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )

        # Assert
        assert project.name == "期限付きプロジェクト"
        assert project.start_date == date(2024, 1, 1)
        assert project.end_date == date(2024, 12, 31)

    def test_project_creation_with_claude_url(self):
        # Arrange & Act
        project = Project(
            name="Claude連携プロジェクト",
            start_date=date(2024, 1, 1),
            claude_url="https://claude.ai/project/abc-123",
        )

        # Assert
        assert project.name == "Claude連携プロジェクト"
        assert project.claude_url == "https://claude.ai/project/abc-123"

    def test_project_claude_url_defaults_to_none(self):
        # Arrange & Act
        project = Project(
            name="基本プロジェクト",
            start_date=date(2024, 1, 1),
        )

        # Assert
        assert project.claude_url is None


class TestInsertedProject:
    def test_inserted_project_creation(self):
        # Arrange & Act
        inserted_project = InsertedProject(
            id="test-id-123",
            name="保存されたプロジェクト",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
        )

        # Assert
        assert inserted_project.id == "test-id-123"
        assert inserted_project.name == "保存されたプロジェクト"
        assert inserted_project.start_date == date(2024, 1, 1)
        assert inserted_project.end_date == date(2024, 3, 31)

    def test_inserted_project_without_end_date(self):
        # Arrange & Act
        inserted_project = InsertedProject(
            id="test-id-456",
            name="終了日なしプロジェクト",
            start_date=date(2024, 1, 1),
        )

        # Assert
        assert inserted_project.id == "test-id-456"
        assert inserted_project.name == "終了日なしプロジェクト"
        assert inserted_project.start_date == date(2024, 1, 1)
        assert inserted_project.end_date is None

    def test_inserted_project_with_claude_url(self):
        # Arrange & Act
        inserted_project = InsertedProject(
            id="test-id-789",
            name="Claude連携プロジェクト",
            start_date=date(2024, 1, 1),
            claude_url="https://claude.ai/project/abc-123",
        )

        # Assert
        assert inserted_project.claude_url == "https://claude.ai/project/abc-123"
