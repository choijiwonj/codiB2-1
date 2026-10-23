# models.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Category:
    name: str
    kind: str  # "income" or "expense"

@dataclass
class Transaction:
    id: str
    date: str          # "2024-01-15"
    amount: int
    category: str
    kind: str          # "income" or "expense"
    memo: str = ""
    tags: list[str] = field(default_factory=list)