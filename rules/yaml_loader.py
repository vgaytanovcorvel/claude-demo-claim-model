from pathlib import Path

import yaml

from rules.category_rules import CategoryRules
from rules.prompt_renderer import PromptRenderer
from rules.schema.category_rule_spec import CategoryRuleSpec


class YamlRuleLoader:
    """Loads a YAML rule file, validates it, and returns a CategoryRules instance."""

    @staticmethod
    def load(path: Path) -> CategoryRules:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        spec = CategoryRuleSpec(**raw)
        return CategoryRules(
            category=spec.category,
            close_cancel_system_prompt=PromptRenderer.render_close_cancel(spec),
            open_items_system_prompt=PromptRenderer.render_open_items(spec),
        )
