from sandpiper.plan.query.project_task_query import ProjectTaskDto


def group_next_project_tasks_by_project(project_task_dtos: list[ProjectTaskDto]) -> dict[str, ProjectTaskDto]:
    project_task_dict: dict[str, ProjectTaskDto] = {}
    for task in project_task_dtos:
        if task.project_page_id not in project_task_dict:
            project_task_dict[task.project_page_id] = task
    return project_task_dict
