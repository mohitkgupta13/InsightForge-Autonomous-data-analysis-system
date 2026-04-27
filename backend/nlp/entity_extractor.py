"""
nlp/entity_extractor.py
Extracts:
  - column name (matched against actual dataset columns)
  - operator    (>, <, =, >=, <=, contains)
  - value       (numeric or string)
  - aggregation type (mean, sum, count, max, min, median)
  - n           (for top_n queries)
  - group_col   (for groupby aggregations)
"""

import re
import pandas as pd


_OPERATORS = {
    ">=": ">=",
    "<=": "<=",
    ">":  ">",
    "<":  "<",
    "=":  "==",
    "==": "==",
    "contains": "contains",
    "equals": "==",
    "is": "==",
}

_AGG_WORDS = {
    "average": "mean", "mean": "mean",
    "sum": "sum", "total": "sum",
    "count": "count",
    "max": "max", "maximum": "max", "highest": "max", "largest": "max",
    "min": "min", "minimum": "min", "lowest": "min", "smallest": "min",
    "median": "median",
}


def extract_entities(query: str, columns: list[str]) -> dict:
    q = query.lower()
    entities: dict = {}

    # ── Column matching ──────────────────────────────────────────────────────
    matched_cols = []
    for col in sorted(columns, key=len, reverse=True):  # longest first avoids sub-matches
        if col.lower() in q:
            matched_cols.append(col)
    entities["columns"] = matched_cols

    # ── Operator ─────────────────────────────────────────────────────────────
    for op_str, op_sym in _OPERATORS.items():
        if op_str in q:
            entities["operator"] = op_sym
            break

    # ── Numeric value ─────────────────────────────────────────────────────────
    num_match = re.search(r"[-+]?\d*\.?\d+", q)
    if num_match:
        try:
            entities["value"] = float(num_match.group())
        except ValueError:
            pass

    # ── Aggregation type ──────────────────────────────────────────────────────
    for word, func in _AGG_WORDS.items():
        if word in q:
            entities["aggregation"] = func
            break

    # ── N (for top_n) ────────────────────────────────────────────────────────
    top_n_match = re.search(r"\btop\s+(\d+)\b|\bbottom\s+(\d+)\b", q)
    if top_n_match:
        n = top_n_match.group(1) or top_n_match.group(2)
        entities["n"] = int(n)

    # ── Group-by column ───────────────────────────────────────────────────────
    by_match = re.search(r"\bby\s+(\w+)\b", q)
    if by_match:
        by_word = by_match.group(1)
        for col in columns:
            if col.lower() == by_word:
                entities["group_col"] = col
                break

    return entities
