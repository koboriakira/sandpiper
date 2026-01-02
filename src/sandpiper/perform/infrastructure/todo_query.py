# from typing import Protocol

# from lotion import Lotion

# from sandpiper.perform.domain.todo import ToDo


# class TodoQuery(Protocol):
#     def find(self, page_id: str) -> ToDo: ...


# class NotionTodoQuery:
#     def __init__(self):
#         self._client = Lotion.get_instance()

#     def find(self, page_id: str) -> ToDo:
#         page = self._client.retrieve_page(page_id)
#         # Convert the Notion page to a ToDo domain object
#         todo = ToDo(
#             title=page.title,
#             # Add other fields as necessary
#         )
#         return todo
