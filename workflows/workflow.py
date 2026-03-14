from pydantic import BaseModel

from models.todo_item_category import TodoItemCategory


class Workflow(BaseModel):
    workflow_id: str
    category: TodoItemCategory | None = None
    system_prompt: str
