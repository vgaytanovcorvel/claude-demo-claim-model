from enum import StrEnum


class TodoItemCategory(StrEnum):
    COVERAGE = "coverage"
    TREATMENT = "treatment"
    EMPLOYMENT = "employment"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    LITIGATION = "litigation"
