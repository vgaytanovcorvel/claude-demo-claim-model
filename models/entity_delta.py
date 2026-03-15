from __future__ import annotations

from pydantic import BaseModel

from models.entity import Entity


class EntityDelta(BaseModel):
    add: list[Entity] = []
    update: list[Entity] = []
    delete: list[str] = []  # entity_id

    def merge(self, other: EntityDelta) -> EntityDelta:
        return EntityDelta(
            add=self.add + other.add,
            update=self.update + other.update,
            delete=self.delete + other.delete,
        )
