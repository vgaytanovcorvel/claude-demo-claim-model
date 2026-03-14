from models.todo_item_category import TodoItemCategory
from rules.category_rules import CategoryRules
from rules.compliance_rules import COMPLIANCE_RULES
from rules.employment_rules import EMPLOYMENT_RULES
from rules.financial_rules import FINANCIAL_RULES
from rules.litigation_rules import LITIGATION_RULES
from rules.treatment_rules import TREATMENT_RULES

ALL_CATEGORY_RULES: dict[TodoItemCategory, CategoryRules] = {
    TodoItemCategory.TREATMENT: TREATMENT_RULES,
    TodoItemCategory.EMPLOYMENT: EMPLOYMENT_RULES,
    TodoItemCategory.FINANCIAL: FINANCIAL_RULES,
    TodoItemCategory.COMPLIANCE: COMPLIANCE_RULES,
    TodoItemCategory.LITIGATION: LITIGATION_RULES,
}
