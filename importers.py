"""한국 카드사·은행 엑셀 명세서 import 어댑터.

지원:
- hyundai : 현대카드 이용내역 엑셀
- bc_ibk  : 기업은행 발급 BC카드 이용내역 엑셀
- ibk_bank: 기업은행 계좌 거래내역 엑셀

각 카드사·은행의 엑셀 컬럼명은 미세하게 다를 수 있어 키워드 매칭으로 유연하게
처리합니다. 첫 import 때 컬럼이 안 맞으면 ADAPTERS 의 columns alias 를 보강하세요.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

try:
    import openpyxl
except ImportError as e:
    raise SystemExit(
        "openpyxl 가 필요합니다. 'pip install -r requirements.txt' 를 먼저 실행하세요."
    ) from e


ADAPTERS: dict[str, dict] = {
    "hyundai": {
        "label": "현대카드",
        "match_filename": ["현대", "hyundai"],
        "match_content": ["현대카드"],
        "columns": {
            "date": ["이용일자", "이용일", "매입일", "거래일자", "승인일자"],
            "merchant": ["이용가맹점", "가맹점", "이용내역", "이용처", "가맹점명"],
            "amount": ["이용금액", "승인금액", "매입금액", "금액"],
        },
        "tx_type": "expense",
    },
    "bc_ibk": {
        "label": "기업은행 BC카드",
        "match_filename": ["bc", "비씨"],
        "match_content": ["BC카드", "비씨카드"],
        "columns": {
            "date": ["이용일자", "이용일", "거래일자", "매입일"],
            "merchant": ["가맹점명", "가맹점", "이용가맹점", "이용처"],
            "amount": ["이용금액", "승인금액", "금액"],
        },
        "tx_type": "expense",
    },
    "ibk_bank": {
        "label": "기업은행 거래내역",
        "match_filename": ["기업은행", "거래내역", "ibk"],
        "match_content": ["거래일시", "기업은행"],
        "columns": {
            "date": ["거래일시", "거래일자", "거래일"],
            "description": ["적요", "내용", "거래내용", "기재내용", "거래메모"],
            "withdraw": ["출금", "출금액", "지급액", "찾으신금액"],
            "deposit": ["입금", "입금액", "받은금액", "맡기신금액"],
        },
        "is_bank": True,
    },
}

# 은행 거래에서 카드 결제일 출금은 카드 명세서로 이미 잡히므로 이중 카운트 방지용 제외
BANK_SKIP_KEYWORDS = [
    "이용대금", "카드대금", "신용카드", "현대카드", "BC카드", "비씨카드",
    "삼성카드", "신한카드", "KB카드", "국민카드", "롯데카드", "하나카드",
    "NH카드", "농협카드", "우리카드",
]


def _load_rows(path: Path) -> list[tuple]:
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb.active
    rows = [row for row in ws.iter_rows(values_only=True)]
    wb.close()
    return rows


def _find_header_by_columns(
    rows: list[tuple], column_alias_groups: list[list[str]]
) -> tuple[int, int | None, list[str]]:
    """필요한 컬럼들의 alias 가 가장 많이 매칭되는 행을 헤더로 뽑는다.

    Returns (score, row_index, header_cells).
    """
    best_score = 0
    best_idx: int | None = None
    best_cells: list[str] = []
    for i, row in enumerate(rows):
        cells = [str(c) if c is not None else "" for c in row]
        if not any(cells):
            continue
        score = 0
        for aliases in column_alias_groups:
            for cell in cells:
                if any(a and a in cell for a in aliases):
                    score += 1
                    break
        if score > best_score:
            best_score = score
            best_idx = i
            best_cells = cells
    return best_score, best_idx, best_cells


def _col(header: list[str], aliases: list[str]) -> int | None:
    for i, cell in enumerate(header):
        for alias in aliases:
            if alias and alias in cell:
                return i
    return None


def _parse_date(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    s = str(value).strip().split(" ")[0]
    s = s.replace(".", "-").replace("/", "-")
    parts = s.split("-")
    if len(parts) == 3:
        try:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            return datetime(y, m, d).date().isoformat()
        except ValueError:
            return None
    if len(s) == 8 and s.isdigit():
        try:
            return datetime.strptime(s, "%Y%m%d").date().isoformat()
        except ValueError:
            return None
    return None


def _parse_amount(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        v = abs(float(value))
        return v if v > 0 else None
    s = str(value).strip().replace(",", "").replace("원", "").replace(" ", "")
    if not s or s in ("-", "0", "0.0"):
        return None
    try:
        v = abs(float(s))
        return v if v > 0 else None
    except ValueError:
        return None


def _hash_id(*parts) -> str:
    s = "|".join(str(p) for p in parts)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def _classify(description: str, rules: dict[str, str]) -> str:
    if not description:
        return "미분류"
    matches = [(p, c) for p, c in rules.items() if p and p in description]
    if not matches:
        return "미분류"
    matches.sort(key=lambda x: -len(x[0]))
    return matches[0][1]


def detect_adapter(path: Path) -> str | None:
    name = path.name.lower()
    for ad_name, cfg in ADAPTERS.items():
        for pat in cfg.get("match_filename", []):
            if pat.lower() in name:
                return ad_name
    try:
        rows = _load_rows(path)[:50]
    except Exception:
        return None
    text = " ".join(str(c) for row in rows for c in row if c is not None)
    for ad_name, cfg in ADAPTERS.items():
        for pat in cfg.get("match_content", []):
            if pat in text:
                return ad_name
    return None


def _parse_card(rows: list[tuple], cfg: dict, source: str, rules: dict[str, str]) -> tuple[list[dict], str | None]:
    cols = cfg["columns"]
    score, h_idx, header = _find_header_by_columns(
        rows, [cols["date"], cols["merchant"], cols["amount"]]
    )
    if h_idx is None or score < 3:
        return [], f"{cfg['label']}: 헤더 매칭 실패 (score={score})"
    c_date = _col(header, cols["date"])
    c_merchant = _col(header, cols["merchant"])
    c_amount = _col(header, cols["amount"])
    if c_date is None or c_merchant is None or c_amount is None:
        return [], (
            f"{cfg['label']}: 컬럼 매핑 실패 "
            f"(date={c_date}, merchant={c_merchant}, amount={c_amount}) header={header}"
        )
    out = []
    for row in rows[h_idx + 1:]:
        if not row or all(c is None for c in row):
            continue
        date = _parse_date(row[c_date]) if c_date < len(row) else None
        merchant = row[c_merchant] if c_merchant < len(row) else None
        amount = _parse_amount(row[c_amount]) if c_amount < len(row) else None
        if not date or not merchant or not amount:
            continue
        merchant = str(merchant).strip()
        out.append({
            "id": _hash_id(date, amount, merchant, source),
            "date": date,
            "type": cfg["tx_type"],
            "category": _classify(merchant, rules),
            "amount": amount,
            "description": merchant,
            "source": source,
        })
    return out, None


def _parse_bank(rows: list[tuple], cfg: dict, source: str, rules: dict[str, str]) -> tuple[list[dict], str | None]:
    cols = cfg["columns"]
    score, h_idx, header = _find_header_by_columns(
        rows, [cols["date"], cols["description"], cols["withdraw"], cols["deposit"]]
    )
    # 4 groups; require at least 3 (withdraw 또는 deposit 중 하나만 있어도 OK)
    if h_idx is None or score < 3:
        return [], f"{cfg['label']}: 헤더 매칭 실패 (score={score})"
    c_date = _col(header, cols["date"])
    c_desc = _col(header, cols["description"])
    c_out = _col(header, cols["withdraw"])
    c_in = _col(header, cols["deposit"])
    if c_date is None or c_desc is None or (c_out is None and c_in is None):
        return [], (
            f"{cfg['label']}: 컬럼 매핑 실패 "
            f"(date={c_date}, desc={c_desc}, out={c_out}, in={c_in}) header={header}"
        )
    out: list[dict] = []
    skipped = 0
    for row in rows[h_idx + 1:]:
        if not row or all(c is None for c in row):
            continue
        date = _parse_date(row[c_date]) if c_date < len(row) else None
        desc_raw = row[c_desc] if c_desc < len(row) else None
        if not date or desc_raw is None:
            continue
        desc = str(desc_raw).strip()
        out_amt = _parse_amount(row[c_out]) if c_out is not None and c_out < len(row) else None
        in_amt = _parse_amount(row[c_in]) if c_in is not None and c_in < len(row) else None

        if out_amt:
            if any(kw in desc for kw in BANK_SKIP_KEYWORDS):
                skipped += 1
                continue
            out.append({
                "id": _hash_id(date, out_amt, desc, source, "out"),
                "date": date,
                "type": "expense",
                "category": _classify(desc, rules),
                "amount": out_amt,
                "description": desc,
                "source": source,
            })
        elif in_amt:
            out.append({
                "id": _hash_id(date, in_amt, desc, source, "in"),
                "date": date,
                "type": "income",
                "category": _classify(desc, rules),
                "amount": in_amt,
                "description": desc,
                "source": source,
            })
    note = f"카드대금 출금 {skipped}건 자동 제외" if skipped else None
    return out, note


def import_file(
    path: Path, adapter: str | None, rules: dict[str, str]
) -> tuple[list[dict], str | None, str | None]:
    """엑셀 파일 1개를 파싱한다.

    Returns (transactions, adapter_used, note_or_error).
    """
    if adapter is None:
        adapter = detect_adapter(path)
        if adapter is None:
            return [], None, f"{path.name}: 어댑터 자동 감지 실패 — --source 로 지정하세요"
    if adapter not in ADAPTERS:
        return [], None, f"알 수 없는 어댑터: {adapter} (사용 가능: {', '.join(ADAPTERS)})"
    cfg = ADAPTERS[adapter]
    rows = _load_rows(path)
    if cfg.get("is_bank"):
        txs, note = _parse_bank(rows, cfg, adapter, rules)
    else:
        txs, note = _parse_card(rows, cfg, adapter, rules)
    return txs, adapter, note
