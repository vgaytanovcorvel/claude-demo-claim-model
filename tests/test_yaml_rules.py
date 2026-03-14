from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from models.owner import Owner
from models.todo_item_category import TodoItemCategory
from rules.category_rules import CategoryRules
from rules.prompt_renderer import PromptRenderer
from rules.schema.category_rule_spec import CategoryRuleSpec
from rules.yaml_loader import YamlRuleLoader

YAML_DIR = Path(__file__).resolve().parent.parent / "rules" / "yaml"
YAML_FILES = sorted(YAML_DIR.glob("*.yaml"))
YAML_IDS = [f.stem for f in YAML_FILES]


# ── Schema validation ────────────────────────────────────────────────


@pytest.mark.parametrize("yaml_path", YAML_FILES, ids=YAML_IDS)
class TestYamlSchemaValidation:
    def test_yaml_parses(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        assert isinstance(raw, dict)

    def test_spec_validates(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = CategoryRuleSpec(**raw)
        assert spec.category.value == yaml_path.stem

    def test_has_close_rules(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = CategoryRuleSpec(**raw)
        assert len(spec.close_rules) > 0

    def test_has_cancel_rules(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = CategoryRuleSpec(**raw)
        assert len(spec.cancel_rules) > 0

    def test_has_triggers(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = CategoryRuleSpec(**raw)
        assert len(spec.open_rules.triggers) > 0

    def test_has_exclusions(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = CategoryRuleSpec(**raw)
        assert len(spec.open_rules.exclusions) > 0

    def test_has_owner_guidance(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = CategoryRuleSpec(**raw)
        assert len(spec.owner_guidance) > 0

    def test_owners_are_valid(self, yaml_path: Path):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        spec = CategoryRuleSpec(**raw)
        valid_owners = set(Owner)
        for og in spec.owner_guidance:
            assert og.owner in valid_owners


# ── All five categories are present ──────────────────────────────────


class TestAllCategoriesCovered:
    def test_five_yaml_files_exist(self):
        assert len(YAML_FILES) == 5

    def test_every_category_has_yaml(self):
        stems = {f.stem for f in YAML_FILES}
        for cat in TodoItemCategory:
            assert cat.value in stems, f"Missing YAML for {cat.value}"


# ── Loader produces CategoryRules ────────────────────────────────────


@pytest.mark.parametrize("yaml_path", YAML_FILES, ids=YAML_IDS)
class TestYamlLoader:
    def test_loader_returns_category_rules(self, yaml_path: Path):
        result = YamlRuleLoader.load(yaml_path)
        assert isinstance(result, CategoryRules)

    def test_category_matches_filename(self, yaml_path: Path):
        result = YamlRuleLoader.load(yaml_path)
        assert result.category.value == yaml_path.stem

    def test_prompts_are_nonempty(self, yaml_path: Path):
        result = YamlRuleLoader.load(yaml_path)
        assert len(result.close_cancel_system_prompt) > 100
        assert len(result.open_items_system_prompt) > 100


# ── Prompt rendering contains key phrases ────────────────────────────


@pytest.mark.parametrize("yaml_path", YAML_FILES, ids=YAML_IDS)
class TestPromptRendering:
    def _load_spec(self, yaml_path: Path) -> CategoryRuleSpec:
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        return CategoryRuleSpec(**raw)

    def test_close_cancel_has_section_headers(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = PromptRenderer.render_close_cancel(spec)
        assert "CLOSING RULES" in prompt
        assert "CANCELLATION RULES" in prompt

    def test_close_cancel_has_role_preamble(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = PromptRenderer.render_close_cancel(spec)
        assert "You are a claim processing assistant" in prompt
        assert spec.category.value.upper() in prompt

    def test_close_cancel_has_footer(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = PromptRenderer.render_close_cancel(spec)
        assert "close_todo_item" in prompt
        assert "cancel_todo_item" in prompt

    def test_open_items_has_section_headers(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = PromptRenderer.render_open_items(spec)
        assert "OPENING RULES" in prompt
        assert "OWNER GUIDANCE" in prompt

    def test_open_items_has_role_preamble(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = PromptRenderer.render_open_items(spec)
        assert "You are a claim processing assistant" in prompt
        assert spec.category.value.upper() in prompt

    def test_open_items_has_footer(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = PromptRenderer.render_open_items(spec)
        assert "add_open_item" in prompt
        assert "milestone-protecting" in prompt

    def test_open_items_has_owner_values(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = PromptRenderer.render_open_items(spec)
        for og in spec.owner_guidance:
            assert og.owner.value in prompt

    def test_open_items_has_trigger_text(self, yaml_path: Path):
        spec = self._load_spec(yaml_path)
        prompt = PromptRenderer.render_open_items(spec)
        for trigger in spec.open_rules.triggers:
            # At least some key words from each trigger should appear
            words = trigger.when.split()[:3]
            key = " ".join(words)
            assert key in prompt, f"Trigger text '{key}' not in open_items prompt"


# ── Financial-specific checks ────────────────────────────────────────


class TestFinancialSpecific:
    def _load_financial(self) -> CategoryRuleSpec:
        raw = yaml.safe_load(
            (YAML_DIR / "financial.yaml").read_text(encoding="utf-8")
        )
        return CategoryRuleSpec(**raw)

    def test_has_mandatory_triggers(self):
        spec = self._load_financial()
        mandatory = [t for t in spec.open_rules.triggers if t.mandatory]
        assert len(mandatory) == 8

    def test_has_duplication_rules(self):
        spec = self._load_financial()
        assert spec.open_rules.duplication_rules is not None
        assert len(spec.open_rules.duplication_rules) > 0

    def test_mandatory_triggers_in_prompt(self):
        spec = self._load_financial()
        prompt = PromptRenderer.render_open_items(spec)
        assert "MANDATORY RESERVE REVIEW TRIGGERS" in prompt

    def test_duplication_rules_in_prompt(self):
        spec = self._load_financial()
        prompt = PromptRenderer.render_open_items(spec)
        assert "DUPLICATION RULES" in prompt

    def test_defaults_important_section(self):
        spec = self._load_financial()
        prompt = PromptRenderer.render_close_cancel(spec)
        assert "IMPORTANT" in prompt
        assert "leave the item open" in prompt


# ── Litigation-specific checks ───────────────────────────────────────


class TestLitigationSpecific:
    def _load_litigation(self) -> CategoryRuleSpec:
        raw = yaml.safe_load(
            (YAML_DIR / "litigation.yaml").read_text(encoding="utf-8")
        )
        return CategoryRuleSpec(**raw)

    def test_has_action_triggers(self):
        spec = self._load_litigation()
        action_triggers = [t for t in spec.open_rules.triggers if t.action]
        assert len(action_triggers) == 5

    def test_action_triggers_in_prompt(self):
        spec = self._load_litigation()
        prompt = PromptRenderer.render_open_items(spec)
        assert "Valid triggers and the items they produce" in prompt

    def test_defaults_important_section(self):
        spec = self._load_litigation()
        prompt = PromptRenderer.render_close_cancel(spec)
        assert "IMPORTANT" in prompt
        assert "postponement" in prompt.lower() or "continuance" in prompt.lower()


# ── Malformed YAML raises ValidationError ────────────────────────────


class TestMalformedYaml:
    def test_missing_category_raises(self):
        with pytest.raises(ValidationError):
            CategoryRuleSpec(
                description="test",
                close_rules=[],
                cancel_rules=[],
                open_rules={"triggers": [], "exclusions": []},
                owner_guidance=[],
            )

    def test_invalid_category_raises(self):
        with pytest.raises(ValidationError):
            CategoryRuleSpec(
                category="not_a_category",
                description="test",
                close_rules=[],
                cancel_rules=[],
                open_rules={"triggers": [], "exclusions": []},
                owner_guidance=[],
            )

    def test_invalid_owner_raises(self):
        with pytest.raises(ValidationError):
            CategoryRuleSpec(
                category="treatment",
                description="test",
                close_rules=[{"when": "x"}],
                cancel_rules=[{"when": "x"}],
                open_rules={"triggers": [{"when": "x"}], "exclusions": ["x"]},
                owner_guidance=[{"owner": "invalid_owner", "when": "x"}],
            )
