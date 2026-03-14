from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from models.owner import Owner
from models.todo_item_category import TodoItemCategory
from workflows.schema.workflow_spec import WorkflowSpec
from workflows.workflow import Workflow
from workflows.yaml_loader import WorkflowYamlLoader

YAML_DIR = Path(__file__).resolve().parent.parent / "workflows" / "yaml"
YAML_FILES = sorted(YAML_DIR.glob("*.yaml"))
YAML_IDS = [f.stem for f in YAML_FILES]


# -- Schema validation -------------------------------------------------------


@pytest.mark.parametrize("yaml_path", YAML_FILES, ids=YAML_IDS)
class TestWorkflowSchemaValidation:
    def test_yaml_parses(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        assert isinstance(raw, dict)

    def test_spec_validates(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = WorkflowSpec(**raw)
        assert spec.workflow_id == yaml_path.stem

    def test_has_branches(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = WorkflowSpec(**raw)
        assert len(spec.branches) > 0

    def test_branches_have_name_trigger_instructions(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = WorkflowSpec(**raw)
        for branch in spec.branches:
            assert branch.name, f"Branch missing name in {yaml_path.stem}"
            assert branch.trigger, f"Branch '{branch.name}' missing trigger"
            assert branch.instructions, f"Branch '{branch.name}' missing instructions"

    def test_branch_names_unique(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = WorkflowSpec(**raw)
        names = [b.name for b in spec.branches]
        assert len(names) == len(set(names)), (
            f"{yaml_path.stem} has duplicate branch names"
        )

    def test_has_exclusions(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = WorkflowSpec(**raw)
        assert len(spec.exclusions) > 0

    def test_has_owner_guidance(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = WorkflowSpec(**raw)
        assert len(spec.owner_guidance) > 0

    def test_owners_are_valid(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = WorkflowSpec(**raw)
        valid_owners = set(Owner)
        for og in spec.owner_guidance:
            assert og.owner in valid_owners


# -- All categories covered ---------------------------------------------------


class TestAllCategoriesCovered:
    def test_six_yaml_files_exist(self):
        assert len(YAML_FILES) == 6

    def test_every_category_has_yaml(self):
        stems = {f.stem for f in YAML_FILES}
        for cat in TodoItemCategory:
            assert cat.value in stems, f"Missing YAML for {cat.value}"


# -- Loader produces Workflow -------------------------------------------------


@pytest.mark.parametrize("yaml_path", YAML_FILES, ids=YAML_IDS)
class TestWorkflowLoader:
    def test_loader_returns_workflow(self, yaml_path: Path):
        result = WorkflowYamlLoader.load(yaml_path)
        assert isinstance(result, Workflow)

    def test_workflow_id_matches_filename(self, yaml_path: Path):
        result = WorkflowYamlLoader.load(yaml_path)
        assert result.workflow_id == yaml_path.stem

    def test_category_matches_filename(self, yaml_path: Path):
        result = WorkflowYamlLoader.load(yaml_path)
        assert result.category is not None
        assert result.category.value == yaml_path.stem

    def test_prompt_is_nonempty(self, yaml_path: Path):
        result = WorkflowYamlLoader.load(yaml_path)
        assert len(result.system_prompt) > 100


# -- Registry -----------------------------------------------------------------


class TestRegistry:
    def test_all_workflows_has_six_entries(self):
        from workflows.registry import ALL_WORKFLOWS

        assert len(ALL_WORKFLOWS) == 6

    def test_workflow_index_has_six_entries(self):
        from workflows.registry import WORKFLOW_INDEX

        assert len(WORKFLOW_INDEX) == 6

    def test_all_categories_in_all_workflows(self):
        from workflows.registry import ALL_WORKFLOWS

        for cat in TodoItemCategory:
            assert cat in ALL_WORKFLOWS, f"Missing workflow for {cat.value}"

    def test_workflow_index_keys_match_ids(self):
        from workflows.registry import WORKFLOW_INDEX

        for wf_id, wf in WORKFLOW_INDEX.items():
            assert wf.workflow_id == wf_id


# -- Malformed YAML raises ValidationError -----------------------------------


class TestMalformedWorkflowYaml:
    def test_missing_workflow_id_raises(self):
        with pytest.raises(ValidationError):
            WorkflowSpec(
                description="test",
                branches=[],
            )

    def test_invalid_category_raises(self):
        with pytest.raises(ValidationError):
            WorkflowSpec(
                workflow_id="test",
                category="not_a_category",
                description="test",
                branches=[],
            )

    def test_invalid_owner_raises(self):
        with pytest.raises(ValidationError):
            WorkflowSpec(
                workflow_id="test",
                description="test",
                branches=[{"name": "b", "trigger": "t", "instructions": "i"}],
                owner_guidance=[{"owner": "invalid_owner", "when": "x"}],
            )
