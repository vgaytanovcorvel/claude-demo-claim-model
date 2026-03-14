import pytest
from pydantic import ValidationError

from rules.schema.cancel_rule import CancelRule
from rules.schema.category_rule_spec import CategoryRuleSpec
from rules.schema.close_rule import CloseRule
from rules.schema.sub_category_spec import SubCategorySpec


class TestSubCategorySpec:
    def test_basic_construction(self):
        sc = SubCategorySpec(
            name="acute-care",
            close_rules=[CloseRule(when="diagnosis established")],
            cancel_rules=[CancelRule(when="not needed")],
        )
        assert sc.name == "acute-care"
        assert len(sc.close_rules) == 1
        assert len(sc.cancel_rules) == 1

    def test_empty_rules_defaults(self):
        sc = SubCategorySpec(name="test")
        assert sc.close_rules == []
        assert sc.cancel_rules == []

    def test_trigger_sub_category_must_match(self):
        with pytest.raises(ValidationError, match="sub_category"):
            CategoryRuleSpec(
                category="treatment",
                description="test",
                close_rules=[{"when": "x"}],
                cancel_rules=[{"when": "x"}],
                open_rules={
                    "triggers": [
                        {
                            "when": "x",
                            "action": "do something",
                            "sub_category": "nonexistent",
                        }
                    ],
                    "exclusions": ["x"],
                },
                owner_guidance=[{"owner": "adjuster", "when": "x"}],
                sub_categories=[{"name": "acute-care"}],
            )

    def test_trigger_sub_category_valid(self):
        spec = CategoryRuleSpec(
            category="treatment",
            description="test",
            close_rules=[{"when": "x"}],
            cancel_rules=[{"when": "x"}],
            open_rules={
                "triggers": [
                    {
                        "when": "x",
                        "action": "do something",
                        "sub_category": "acute-care",
                    }
                ],
                "exclusions": ["x"],
            },
            owner_guidance=[{"owner": "adjuster", "when": "x"}],
            sub_categories=[{"name": "acute-care"}],
        )
        assert spec.open_rules.triggers[0].sub_category == "acute-care"

    def test_trigger_none_sub_category_always_valid(self):
        spec = CategoryRuleSpec(
            category="treatment",
            description="test",
            close_rules=[{"when": "x"}],
            cancel_rules=[{"when": "x"}],
            open_rules={
                "triggers": [{"when": "x", "action": "do something"}],
                "exclusions": ["x"],
            },
            owner_guidance=[{"owner": "adjuster", "when": "x"}],
            sub_categories=[{"name": "acute-care"}],
        )
        assert spec.open_rules.triggers[0].sub_category is None
