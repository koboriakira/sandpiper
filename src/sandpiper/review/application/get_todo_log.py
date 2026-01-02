from sandpiper.review.query.done_todo_dto import DoneTodoDto
from sandpiper.review.query.todo_query import TodoQuery


class GetTodoLog:
    def __init__(self, todo_query: TodoQuery) -> None:
        self.todo_query = todo_query

    def execute(self) -> list[DoneTodoDto]:
        done_todos = self.todo_query.fetch_done_todos()

        # perform_range.0の昇順でソート
        done_todos.sort(key=lambda dto: dto.perform_range[0])
        return done_todos
