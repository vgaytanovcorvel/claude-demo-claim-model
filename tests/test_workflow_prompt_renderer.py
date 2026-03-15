from pathlib import Path

import pytest
import yaml

from workflows.prompt_renderer import WorkflowPromptRenderer
from workflows.schema.workflow_spec import WorkflowSpec

YAML_DIR = Path(__file__).resolve().parent.parent / "workflows" / "yaml"
YAML_FILES = sorted(YAML_DIR.glob("*.yaml"))
YAML_IDS = [f.stem for f in YAML_FILES]


@pytest.mark.parametrize("yaml_path", YAML_FILES, ids=YAML_IDS)
class TestWorkflowPromptRendering:
    def _load_spec(self, yaml_path: Path) -> WorkflowSpec:
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        return WorkflowSpec(**raw)

    def test_has_role_preamble(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = WorkflowPromptRenderer.render(spec)
        assert "You are a claim processing assistant" in prompt

    def test_has_branches_section(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = WorkflowPromptRenderer.render(spec)
        assert "BRANCHES:" in prompt

    def test_has_all_branch_names(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = WorkflowPromptRenderer.render(spec)
        for branch in spec.branches:
            assert branch.name in prompt, (
                f"Branch '{branch.name}' not in rendered prompt"
            )

    def test_has_all_branch_triggers(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = WorkflowPromptRenderer.render(spec)
        for branch in spec.branches:
            # Check first few words of trigger appear
            words = branch.trigger.split()[:3]
            key = " ".join(words)
            assert key in prompt, f"Trigger text '{key}' not in prompt"

    def test_has_exclusions_section(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = WorkflowPromptRenderer.render(spec)
        assert "EXCLUSIONS:" in prompt

    def test_has_owner_guidance_section(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = WorkflowPromptRenderer.render(spec)
        assert "OWNER GUIDANCE:" in prompt

    def test_has_owner_values(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = WorkflowPromptRenderer.render(spec)
        for og in spec.owner_guidance:
            assert og.owner.value in prompt

    def test_has_tool_instructions(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = WorkflowPromptRenderer.render(spec)
        assert "AVAILABLE TOOLS:" in prompt
        assert "add_open_item" in prompt
        assert "terminate_todo_item" in prompt
        assert "start_workflow" in prompt

    def test_has_footer(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = WorkflowPromptRenderer.render(spec)
        assert "If no branches match" in prompt

    def test_has_category_in_preamble(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = WorkflowPromptRenderer.render(spec)
        category_label = (
            spec.category.value.upper() if spec.category else spec.workflow_id.upper()
        )
        assert category_label in prompt


class TestDefaultsRendering:
    def _load_spec(self, name: str) -> WorkflowSpec:
        raw = yaml.safe_load((YAML_DIR / name).read_text(encoding="utf-8"))
        return WorkflowSpec(**raw)

    def test_litigation_has_important_section(self):
        spec = self._load_spec("litigation.yaml")
        prompt = WorkflowPromptRenderer.render(spec)
        assert "IMPORTANT:" in prompt
        assert "leave the item open" in prompt

    def test_financial_has_important_section(self):
        spec = self._load_spec("financial.yaml")
        prompt = WorkflowPromptRenderer.render(spec)
        assert "IMPORTANT:" in prompt

    def test_coverage_has_important_section(self):
        spec = self._load_spec("coverage.yaml")
        prompt = WorkflowPromptRenderer.render(spec)
        assert "IMPORTANT:" in prompt
        assert "Coverage must be affirmatively established" in prompt
