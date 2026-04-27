"""
nlp/intent_classifier.py
Keyword-based intent classifier supporting 7 core intents.
"""

import re
from typing import Literal

INTENTS = Literal[
    "summarize", "filter", "plot", "correlate",
    "aggregate", "predict", "top_n", "unknown"
]

_INTENT_KEYWORDS: dict[str, list[str]] = {
    "summarize":  ["summary", "summarize", "describe", "overview", "info", "statistics", "stats"],
    "filter":     ["filter", "where", "show rows", "rows where", "select where", "find rows", "entries where"],
    "plot":       ["plot", "chart", "histogram", "distribution", "visualize", "graph", "draw", "show distribution"],
    "correlate":  ["correlate", "correlation", "related", "relationship", "associated"],
    "aggregate":  ["average", "mean", "sum", "count", "max", "min", "median", "group by", "total", "aggregate"],
    "predict":    ["predict", "estimate", "forecast", "what would", "what will", "what is the predicted"],
    "top_n":      ["top", "bottom", "highest", "lowest", "best", "worst", "largest", "smallest"],
}


def classify_intent(query: str) -> str:
    q = query.lower().strip()
    scores: dict[str, int] = {intent: 0 for intent in _INTENT_KEYWORDS}

    for intent, keywords in _INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in q:
                scores[intent] += 1

    best_intent = max(scores, key=lambda k: scores[k])
    if scores[best_intent] == 0:
        return "unknown"
    return best_intent
