"""Simple CLI 가계부 (expense tracker).

Stores transactions in a JSON file and supports add/list/summary/delete.
Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


DEFAULT_DATA_FILE = Path(__file__).resolve().parent / "expenses.json"
TX_TYPES = ("expense", "income")


def load_transactions(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return data


def save_transactions(path: Path, transactions: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)


def parse_date(value: str) -> str:
    return datetime.strptime(value, "%Y-%m-%d").date().isoformat()


def parse_month(value: str) -> str:
    datetime.strptime(value, "%Y-%m")
    return value


def filter_transactions(
    transactions: Iterable[dict],
    month: str | None = None,
    category: str | None = None,
    tx_type: str | None = None,
) -> list[dict]:
    result = []
    for tx in transactions:
        if month and not tx["date"].startswith(month):
            continue
        if category and tx["category"] != category:
            continue
        if tx_type and tx["type"] != tx_type:
            continue
        result.append(tx)
    return result


def format_amount(amount: float) -> str:
    if amount == int(amount):
        return f"{int(amount):,}"
    return f"{amount:,.2f}"


def cmd_add(args: argparse.Namespace) -> int:
    if args.amount <= 0:
        print("amount는 0보다 커야 합니다.", file=sys.stderr)
        return 2

    tx = {
        "id": uuid.uuid4().hex[:8],
        "date": args.date,
        "type": args.type,
        "category": args.category,
        "amount": args.amount,
        "description": args.description or "",
    }
    transactions = load_transactions(args.data_file)
    transactions.append(tx)
    transactions.sort(key=lambda t: (t["date"], t["id"]))
    save_transactions(args.data_file, transactions)

    sign = "-" if tx["type"] == "expense" else "+"
    print(
        f"추가됨 [{tx['id']}] {tx['date']} {tx['category']} "
        f"{sign}{format_amount(tx['amount'])}원"
        + (f" ({tx['description']})" if tx["description"] else "")
    )
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    transactions = load_transactions(args.data_file)
    rows = filter_transactions(
        transactions, month=args.month, category=args.category, tx_type=args.type
    )
    if not rows:
        print("표시할 거래가 없습니다.")
        return 0

    print(f"{'ID':<10}{'날짜':<12}{'구분':<8}{'카테고리':<14}{'금액':>14}  설명")
    print("-" * 72)
    for tx in rows:
        sign = "-" if tx["type"] == "expense" else "+"
        amount_str = f"{sign}{format_amount(tx['amount'])}"
        print(
            f"{tx['id']:<10}{tx['date']:<12}{tx['type']:<8}"
            f"{tx['category']:<14}{amount_str:>14}  {tx['description']}"
        )
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    transactions = load_transactions(args.data_file)
    rows = filter_transactions(transactions, month=args.month)

    income_total = sum(tx["amount"] for tx in rows if tx["type"] == "income")
    expense_total = sum(tx["amount"] for tx in rows if tx["type"] == "expense")
    balance = income_total - expense_total

    title = f"{args.month} 요약" if args.month else "전체 요약"
    print(f"=== {title} ===")
    print(f"수입 합계 : +{format_amount(income_total)}원")
    print(f"지출 합계 : -{format_amount(expense_total)}원")
    print(f"잔액      : {format_amount(balance)}원")

    by_category: dict[str, float] = {}
    for tx in rows:
        if tx["type"] != "expense":
            continue
        by_category[tx["category"]] = by_category.get(tx["category"], 0) + tx["amount"]

    if by_category:
        print("\n카테고리별 지출:")
        for cat, total in sorted(by_category.items(), key=lambda x: -x[1]):
            share = (total / expense_total * 100) if expense_total else 0
            print(f"  {cat:<14}{format_amount(total):>12}원  ({share:5.1f}%)")
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    transactions = load_transactions(args.data_file)
    remaining = [tx for tx in transactions if tx["id"] != args.id]
    if len(remaining) == len(transactions):
        print(f"ID {args.id} 를 찾지 못했습니다.", file=sys.stderr)
        return 1
    save_transactions(args.data_file, remaining)
    print(f"삭제됨 [{args.id}]")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="간단한 CLI 가계부")
    parser.add_argument(
        "--data-file",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="거래 내역 JSON 파일 경로 (기본: expenses.json)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="거래 추가")
    add_p.add_argument("amount", type=float, help="금액 (양수)")
    add_p.add_argument("category", help="카테고리 (예: 식비, 교통)")
    add_p.add_argument("-d", "--description", help="메모", default="")
    add_p.add_argument(
        "--date",
        type=parse_date,
        default=date.today().isoformat(),
        help="날짜 YYYY-MM-DD (기본: 오늘)",
    )
    add_p.add_argument(
        "--type", choices=TX_TYPES, default="expense", help="거래 종류 (기본: expense)"
    )
    add_p.set_defaults(func=cmd_add)

    list_p = sub.add_parser("list", help="거래 목록")
    list_p.add_argument("--month", type=parse_month, help="YYYY-MM 으로 필터")
    list_p.add_argument("--category", help="카테고리로 필터")
    list_p.add_argument("--type", choices=TX_TYPES, help="거래 종류로 필터")
    list_p.set_defaults(func=cmd_list)

    sum_p = sub.add_parser("summary", help="월별/전체 요약")
    sum_p.add_argument("--month", type=parse_month, help="YYYY-MM (기본: 전체)")
    sum_p.set_defaults(func=cmd_summary)

    del_p = sub.add_parser("delete", help="ID 로 거래 삭제")
    del_p.add_argument("id", help="거래 ID")
    del_p.set_defaults(func=cmd_delete)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
