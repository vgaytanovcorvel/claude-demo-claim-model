from pydantic import BaseModel

from models.todo_item_category import TodoItemCategory


class CategoryRules(BaseModel):
    category: TodoItemCategory
    close_cancel_system_prompt: str
    open_items_system_prompt: str
