from pathlib import Path

import yaml

from workflows.prompt_renderer import WorkflowPromptRenderer
from workflows.schema.workflow_spec import WorkflowSpec
from workflows.workflow import Workflow


class WorkflowYamlLoader:
    """Loads a workflow YAML file, validates it, and returns a Workflow instance."""

    @staticmethod
    def load(path: Path) -> Workflow:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        spec = WorkflowSpec(**raw)
        return Workflow(
            workflow_id=spec.workflow_id,
            category=spec.category,
            system_prompt=WorkflowPromptRenderer.render(spec),
        )
