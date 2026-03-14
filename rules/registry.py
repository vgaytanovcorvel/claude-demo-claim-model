from pathlib import Path

from models.todo_item_category import TodoItemCategory
from rules.category_rules import CategoryRules
from rules.yaml_loader import YamlRuleLoader

_RULES_DIR = Path(__file__).parent / "yaml"

ALL_CATEGORY_RULES: dict[TodoItemCategory, CategoryRules] = {
    r.category: r
    for r in [
        YamlRuleLoader.load(_RULES_DIR / "treatment.yaml"),
        YamlRuleLoader.load(_RULES_DIR / "employment.yaml"),
        YamlRuleLoader.load(_RULES_DIR / "financial.yaml"),
        YamlRuleLoader.load(_RULES_DIR / "compliance.yaml"),
        YamlRuleLoader.load(_RULES_DIR / "litigation.yaml"),
    ]
}
