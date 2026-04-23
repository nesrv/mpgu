# -*- coding: utf-8 -*-
"""
426_wide.md  — широкая таблица (как в отчёте).
426.tsv      — правки удобнее в Excel; UTF-8 с BOM.
426.md       — короткая сводка для просмотра в репозитории.

  py gen_426.py              — из 426_wide.md пересобрать 426.tsv и 426.md
  py gen_426.py --from-tsv   — только 426.md из актуального 426.tsv
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
WIDE = DIR / "426_wide.md"
TSV = DIR / "426.tsv"
MD = DIR / "426.md"

HEADER_TSV = [
    "no",
    "fio",
    "zachotka",
    "cicd",
    "saap",
    "ninja",
    "fapi",
    "dj",
    "rq",
    "cel",
    "rq2",
    "k8s",
    "gitops",
    "pgrep",
    "sum",
    "zach",
]


LAB_COUNT = 11


def _normalize_labs(raw: list[str]) -> list[str]:
    """Ровно LAB_COUNT ячеек работ (ci/cd … pg-peplic)."""
    labs = list(raw)
    if len(labs) < LAB_COUNT:
        labs.extend([""] * (LAB_COUNT - len(labs)))
    return labs[:LAB_COUNT]


def parse_wide_table(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    sum_re = re.compile(r"\d+\s*=\s*\d+")
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|") or "---" in s:
            continue
        if "Фамилия и инициалы" in s:
            continue
        parts = [p.strip() for p in s.split("|")]
        if len(parts) < 8:
            continue
        no = parts[1]
        if not no.isdigit():
            continue
        fio = parts[2]
        zk = parts[3]
        rest = parts[4:]
        sum_idx = next((i for i, p in enumerate(rest) if sum_re.search(p)), None)
        if sum_idx is not None:
            labs_raw = rest[:sum_idx]
            summ = rest[sum_idx]
            zach = rest[sum_idx + 1] if sum_idx + 1 < len(rest) else ""
        else:
            if len(rest) >= 2:
                labs_raw, summ, zach = rest[:-2], rest[-2], rest[-1]
            else:
                labs_raw, summ, zach = rest, "", ""
        labs = _normalize_labs(labs_raw)
        rows.append([no, fio, zk] + labs + [summ, zach])
    return rows


def write_tsv(rows: list[list[str]]) -> None:
    with TSV.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(HEADER_TSV)
        w.writerows(rows)


def write_short_md(rows: list[list[str]]) -> None:
    h = "| № | ФИО | зк | cd | sa | nj | fp | dj | rq | ce | r2 | k8 | git | pg | сумма | зч |"
    sep = "|" + "|".join(["---"] * 16) + "|"
    lines_out = [
        "Отчетность по лабораторным работам",
        "",
        "Редактирование: в первую очередь **`426.tsv`** (табуляция, UTF-8). В Excel — «Данные» → «Из текста/CSV», кодировка UTF-8.",
        "",
        "Обновить эту страницу из TSV: `py gen_426.py --from-tsv`. Полная широкая таблица — в **`426_wide.md`**; пересобрать TSV и эту сводку из неё: `py gen_426.py`.",
        "",
        "Колонки TSV: `no`, `fio`, `zachotka`, `cicd`, `saap`, `ninja`, `fapi`, `dj`, `rq`, `cel`, `rq2`, `k8s`, `gitops`, `pgrep`, `sum`, `zach`. Пусто = нет сдачи; в `zach` — `+` или пусто.",
        "",
        h,
        sep,
    ]
    for r in rows:
        # r: 0 no, 1 fio, 2 zk, 3..13 labs (11), 14 sum, 15 zach
        cells = [r[0], r[1].replace("|", "/"), r[2]] + [c if c else "" for c in r[3:14]] + [r[14], r[15]]
        lines_out.append("| " + " | ".join(cells) + " |")
    lines_out.append("")
    MD.write_text("\n".join(lines_out), encoding="utf-8")


def read_tsv_rows() -> list[list[str]]:
    with TSV.open(encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f, delimiter="\t")
        rows = list(r)
    if not rows:
        return []
    if rows[0][0].lower() == "no":
        rows = rows[1:]
    out: list[list[str]] = []
    for row in rows:
        if not row or not row[0].strip():
            continue
        # pad to 16 cols
        row = [c.strip() for c in row]
        while len(row) < 16:
            row.append("")
        out.append(row[:16])
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--from-tsv", action="store_true", help="only rebuild 426.md from 426.tsv")
    args = p.parse_args()

    if args.from_tsv:
        if not TSV.is_file():
            print("Missing", TSV, file=sys.stderr)
            return 1
        rows = read_tsv_rows()
        write_short_md(rows)
        print("Wrote", MD, "rows=", len(rows), "(from TSV)")
        return 0

    if not WIDE.is_file():
        print("Missing", WIDE, file=sys.stderr)
        return 1
    text = WIDE.read_text(encoding="utf-8")
    rows = parse_wide_table(text)
    if not rows:
        print("No data rows in", WIDE, file=sys.stderr)
        return 1
    write_tsv(rows)
    write_short_md(rows)
    print("Wrote", TSV, "and", MD, "rows=", len(rows), "(from wide)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
