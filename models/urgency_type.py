from enum import StrEnum


class UrgencyType(StrEnum):
    MILESTONE_PROTECTING = "milestone-protecting"
    DEADLINE_DRIVEN = "deadline-driven"
    DISCRETIONARY = "discretionary"
