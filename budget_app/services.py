# services.py
from __future__ import annotations
import uuid
from datetime import datetime
from .models import Transaction, Category
from .repositories import TransactionRepository, CategoryRepository


class AppError(Exception):
    """사용자에게 보여줄 친절한 에러"""
    def __init__(self, message: str, hint: str = ""):
        super().__init__(message)
        self.hint = hint

class TransactionService:
    def __init__(self, tx_repo: TransactionRepository, 
                 cat_repo: CategoryRepository):
        self.tx_repo = tx_repo
        self.cat_repo = cat_repo

    def add(self, date: str, amount: int, category: str, 
            kind: str, memo: str = "") -> Transaction:
        # 1. 검증
        if amount <= 0:
            raise AppError("금액은 0보다 커야 합니다", 
                          "예: --amount 1000")
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise AppError(f"잘못된 날짜: {date}", 
                          "형식: YYYY-MM-DD")
        if not self.cat_repo.exists(category):
            raise AppError(f"없는 카테고리: {category}",
                          "먼저 category add 로 등록하세요")
        
        # 2. 저장 (Repository에게 위임)
        tx = Transaction(
            id=str(uuid.uuid4())[:8],
            date=date, amount=amount,
            category=category, kind=kind, memo=memo
        )
        self.tx_repo.add(tx)
        return tx
    def list_filtered(
        self,
        date_from: str = None,
        date_to: str = None,
        category: str = None,
        kind: str = None,
        ):
        """조건에 맞는 거래만 반환 (제너레이터)"""
        for tx in self.tx_repo.stream():
            if date_from and tx.date < date_from:
                continue
            if date_to and tx.date > date_to:
                continue
            if category and tx.category != category:
                continue
            if kind and tx.kind != kind:
                continue
            yield tx

    # services.py 하단에 추가
class CategoryService:
    def __init__(self, cat_repo: CategoryRepository):
        self.cat_repo = cat_repo

    def add(self, name: str, kind: str) -> Category:
        # 검증
        if kind not in ("income", "expense"):
            raise AppError(f"잘못된 kind: {kind}", 
                          "income 또는 expense만 가능")
        if self.cat_repo.exists(name):
            raise AppError(f"이미 존재하는 카테고리: {name}",
                          "다른 이름을 사용하세요")
        
        # 저장
        cat = Category(name=name, kind=kind)
        self.cat_repo.add(cat)
        return cat

    def list_all(self) -> list[Category]:
        return self.cat_repo.all()