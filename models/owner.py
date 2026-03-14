from enum import StrEnum


class Owner(StrEnum):
    ADJUSTER = "adjuster"
    EMPLOYER = "employer"
    PROVIDER = "provider"
    INJURED_WORKER = "injured-worker"
    OTHER = "other"
