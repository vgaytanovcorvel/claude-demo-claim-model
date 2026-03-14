from enum import StrEnum


class TodoItemCategory(StrEnum):
    TREATMENT = "treatment"
    EMPLOYMENT = "employment"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    LITIGATION = "litigation"
