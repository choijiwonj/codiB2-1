# repositories.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Iterator
from .models import Transaction, Category


class TransactionRepository:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def add(self, tx: Transaction) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(tx.__dict__, ensure_ascii=False) + "\n")

    def stream(self) -> Iterator[Transaction]:
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield Transaction(**json.loads(line))

    def all(self) -> list[Transaction]:
        return list(self.stream())


class CategoryRepository:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def add(self, category: Category) -> None:
        """카테고리 한 줄 추가"""
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(category.__dict__, ensure_ascii=False) + "\n")

    def stream(self) -> Iterator[Category]:
        """카테고리 한 줄씩 읽기"""
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield Category(**json.loads(line))

    def all(self) -> list[Category]:
        return list(self.stream())

    def exists(self, name: str) -> bool:
        """해당 이름의 카테고리가 존재하는지 확인"""
        return any(c.name == name for c in self.stream())