from pydantic import BaseModel

from models.todo_item import TodoItem


class TodoItemDelta(BaseModel):
    add: list[TodoItem] = []
    update: list[TodoItem] = []
    delete: list[str] = []  # todo_item_id
