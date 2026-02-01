# Re-export from shared for backward compatibility
from sandpiper.shared.repository.project_task_repository import (
    InsertedProjectTask,
    ProjectTask,
)

__all__ = ["InsertedProjectTask", "ProjectTask"]
