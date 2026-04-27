"""
nlp/query_executor.py
Maps intent + entities → pandas operations → structured response.
Response types: "text" | "table" | "chart"
"""

import os
import base64
import numpy as np
import pandas as pd

from nlp.intent_classifier import classify_intent
from nlp.entity_extractor import extract_entities


def execute_query(
    query: str,
    df: pd.DataFrame,
    session_id: str,
    charts_dir: str,
) -> dict:
    """
    Returns:
      {
        "intent": str,
        "response_type": "text" | "table" | "chart",
        "data": ...
      }
    """

    columns = list(df.columns)
    intent = classify_intent(query)
    entities = extract_entities(query, columns)

    try:
        if intent == "summarize":
            return _summarize(df)

        elif intent == "filter":
            return _filter(df, entities)

        elif intent == "plot":
            return _plot(df, entities, session_id, charts_dir)

        elif intent == "correlate":
            return _correlate(df, entities)

        elif intent == "aggregate":
            return _aggregate(df, entities)

        elif intent == "top_n":
            return _top_n(df, entities)

        elif intent == "predict":
            return {
                "intent": intent,
                "response_type": "text",
                "data": "Prediction queries require running /api/analyze first and then specifying feature values. "
                        "This feature is coming soon.",
            }

        else:
            return {
                "intent": "unknown",
                "response_type": "text",
                "data": (
                    "Sorry, I didn't understand that query. Try things like:\n"
                    "• 'Show me a summary'\n"
                    "• 'Show rows where Age > 30'\n"
                    "• 'Plot the distribution of Salary'\n"
                    "• 'What is the average Income by City?'\n"
                    "• 'Show top 10 rows by Sales'"
                ),
            }

    except Exception as e:
        return {"intent": intent, "response_type": "text", "data": f"Error executing query: {str(e)}"}


# ── Intent handlers ───────────────────────────────────────────────────────────

def _summarize(df: pd.DataFrame) -> dict:
    desc = df.describe(include="all").fillna("").astype(str)
    return {
        "intent": "summarize",
        "response_type": "table",
        "data": desc.reset_index().to_dict(orient="records"),
    }


def _filter(df: pd.DataFrame, entities: dict) -> dict:
    cols = entities.get("columns", [])
    op = entities.get("operator")
    val = entities.get("value")

    if not cols or not op or val is None:
        return {
            "intent": "filter",
            "response_type": "text",
            "data": "Could not parse filter conditions. Example: 'Show rows where Age > 30'",
        }

    col = cols[0]
    if op == "contains":
        result = df[df[col].astype(str).str.contains(str(val), na=False)]
    else:
        result = df.query(f"`{col}` {op} {val}")

    return {
        "intent": "filter",
        "response_type": "table",
        "data": result.head(50).replace({float("nan"): None}).to_dict(orient="records"),
        "matched_rows": len(result),
    }


def _plot(df: pd.DataFrame, entities: dict, session_id: str, charts_dir: str) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    cols = entities.get("columns", [])
    if not cols:
        return {"intent": "plot", "response_type": "text", "data": "Specify a column to plot."}

    col = cols[0]
    if col not in df.columns:
        return {"intent": "plot", "response_type": "text", "data": f"Column '{col}' not found."}

    out_path = os.path.join(charts_dir, session_id, f"nlp_plot_{col}.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5), facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")

    if pd.api.types.is_numeric_dtype(df[col]):
        sns.histplot(df[col].dropna(), kde=True, ax=ax, color="#e94560")
    else:
        counts = df[col].value_counts().head(15)
        sns.barplot(x=counts.index.astype(str), y=counts.values, ax=ax, palette="magma")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", color="white")

    ax.set_title(f"Plot of {col}", color="white")
    ax.tick_params(colors="white")
    fig.savefig(out_path, dpi=120, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close(fig)

    with open(out_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return {"intent": "plot", "response_type": "chart", "data": b64, "column": col}


def _correlate(df: pd.DataFrame, entities: dict) -> dict:
    numeric = df.select_dtypes(include=[np.number])
    cols = entities.get("columns", [])
    if cols and cols[0] in numeric.columns:
        corr_series = numeric.corr()[cols[0]].drop(cols[0]).sort_values(ascending=False)
        return {
            "intent": "correlate",
            "response_type": "table",
            "data": [{"column": k, "correlation": round(v, 4)} for k, v in corr_series.items()],
        }
    corr = numeric.corr().round(4)
    return {
        "intent": "correlate",
        "response_type": "table",
        "data": corr.reset_index().to_dict(orient="records"),
    }


def _aggregate(df: pd.DataFrame, entities: dict) -> dict:
    cols = entities.get("columns", [])
    agg = entities.get("aggregation", "mean")
    group_col = entities.get("group_col")

    if not cols:
        return {"intent": "aggregate", "response_type": "text",
                "data": "Specify a column. Example: 'What is the average Salary by Department?'"}

    col = cols[0]
    if col not in df.columns:
        return {"intent": "aggregate", "response_type": "text", "data": f"Column '{col}' not found."}

    if group_col and group_col in df.columns:
        result = df.groupby(group_col)[col].agg(agg).reset_index()
        result.columns = [group_col, f"{agg}_{col}"]
        return {"intent": "aggregate", "response_type": "table",
                "data": result.to_dict(orient="records")}

    val = getattr(df[col], agg)()
    return {
        "intent": "aggregate",
        "response_type": "text",
        "data": f"{agg.capitalize()} of {col} = {round(float(val), 4)}",
    }


def _top_n(df: pd.DataFrame, entities: dict) -> dict:
    n = entities.get("n", 10)
    cols = entities.get("columns", [])
    sort_col = cols[0] if cols else df.columns[0]

    ascending = "bottom" in str(entities.get("_raw_query", "")).lower()
    result = df.nlargest(n, sort_col) if not ascending else df.nsmallest(n, sort_col)

    return {
        "intent": "top_n",
        "response_type": "table",
        "data": result.replace({float("nan"): None}).to_dict(orient="records"),
    }
