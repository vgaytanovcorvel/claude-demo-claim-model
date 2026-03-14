from pathlib import Path

from models.todo_item_category import TodoItemCategory
from workflows.workflow import Workflow
from workflows.yaml_loader import WorkflowYamlLoader

_WORKFLOWS_DIR = Path(__file__).parent / "yaml"

_all_workflows: list[Workflow] = [
    WorkflowYamlLoader.load(path) for path in sorted(_WORKFLOWS_DIR.glob("*.yaml"))
]

ALL_WORKFLOWS: dict[TodoItemCategory, Workflow] = {
    w.category: w for w in _all_workflows if w.category is not None
}

WORKFLOW_INDEX: dict[str, Workflow] = {w.workflow_id: w for w in _all_workflows}
