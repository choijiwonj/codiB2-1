# cli.py
from __future__ import annotations
import argparse
from pathlib import Path
from .repositories import TransactionRepository, CategoryRepository
from .services import TransactionService, CategoryService, AppError
from .decorators import handle_errors

DATA_DIR = Path("data")

def build_parser():
    parser = argparse.ArgumentParser(prog="budget_app")
    sub = parser.add_subparsers(dest="command", required=True)
    
    # --- 카테고리 명령어 ---
    cat = sub.add_parser("category", help="카테고리 관리")
    cat_sub = cat.add_subparsers(dest="action", required=True)
    
    cat_add = cat_sub.add_parser("add", help="카테고리 추가")
    cat_add.add_argument("--name", required=True)
    cat_add.add_argument("--kind", choices=["income", "expense"], required=True)
    
    cat_sub.add_parser("list", help="카테고리 목록")
    
    # --- 거래 명령어 ---
    tx = sub.add_parser("tx", help="거래 관리")
    tx_sub = tx.add_subparsers(dest="action", required=True)
    
    tx_add = tx_sub.add_parser("add", help="거래 추가")
    tx_add.add_argument("--date", required=True)
    tx_add.add_argument("--amount", type=int, required=True)
    tx_add.add_argument("--category", required=True)
    tx_add.add_argument("--kind", choices=["income", "expense"], required=True)
    tx_add.add_argument("--memo", default="")
    
    tx_list = tx_sub.add_parser("list", help="거래 목록")
    tx_list.add_argument("--date-from", help="시작 날짜 (YYYY-MM-DD)")
    tx_list.add_argument("--date-to", help="종료 날짜 (YYYY-MM-DD)")
    tx_list.add_argument("--category", help="카테고리로 필터")
    tx_list.add_argument("--kind", choices=["income", "expense"], help="수입/지출 필터")
    
    return parser

@handle_errors
def main():
    args = build_parser().parse_args()
    
    # 1. 의존성 조립 (Dependency Injection을 수동으로)
    tx_repo = TransactionRepository(DATA_DIR / "transactions.jsonl")
    cat_repo = CategoryRepository(DATA_DIR / "categories.jsonl")
    tx_service = TransactionService(tx_repo, cat_repo)
    cat_service = CategoryService(cat_repo)
    
    # 2. 명령어 분기
    try:
        if args.command == "category":
            if args.action == "add":
                cat = cat_service.add(args.name, args.kind)
                print(f"✅ 카테고리 추가: {cat.name} ({cat.kind})")
            elif args.action == "list":
                for c in cat_service.list_all():
                    print(f"- {c.name} ({c.kind})")
        
        elif args.command == "tx":
            if args.action == "add":
                tx = tx_service.add(args.date, args.amount, 
                                    args.category, args.kind, args.memo)
                print(f"✅ 거래 추가: [{tx.id}] {tx.date} {tx.amount}원")
            elif args.action == "list":
                results = tx_service.list_filtered(
                    date_from=args.date_from,
                    date_to=args.date_to,
                    category=args.category,
                    kind=args.kind,
                )
                count = 0
                for t in results:
                    print(f"[{t.id}] {t.date} | {t.kind:7s} | {t.category} | {t.amount:>10,}원 | {t.memo}")
                    count += 1
                print(f"\n📊 총 {count}건") 
    
    except AppError as e:
        print(f"❌ 오류: {e}")
        if e.hint:
            print(f"💡 힌트: {e.hint}")
        return 1
    return 0