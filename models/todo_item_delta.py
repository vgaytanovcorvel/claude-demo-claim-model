from __future__ import annotations

from pydantic import BaseModel

from models.todo_item import TodoItem


class TodoItemDelta(BaseModel):
    add: list[TodoItem] = []
    update: list[TodoItem] = []
    delete: list[str] = []  # todo_item_id

    def merge(self, other: TodoItemDelta) -> TodoItemDelta:
        return TodoItemDelta(
            add=self.add + other.add,
            update=self.update + other.update,
            delete=self.delete + other.delete,
        )
