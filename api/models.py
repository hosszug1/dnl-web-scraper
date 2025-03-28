from __future__ import annotations

from pydantic import BaseModel


class Product(BaseModel):
    make: str
    category: str
    model: str
    part_type: str | None
    part_number: str
