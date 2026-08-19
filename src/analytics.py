from __future__ import annotations

import numpy as np
import pandas as pd


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.replace(0, np.nan)
    return numerator / denominator


def build_financial_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate decision-ready KPIs from fiscal-year-aligned accounting facts."""
    out = df.sort_values("fiscal_year").copy()

    if {"revenue", "cost_of_revenue"}.issubset(out.columns):
        out["gross_profit_derived"] = out["revenue"] - out["cost_of_revenue"]
        out["gross_margin_pct"] = (
            100 * safe_divide(out["gross_profit_derived"], out["revenue"])
        ).round(2)

    if {"operating_income", "revenue"}.issubset(out.columns):
        out["operating_margin_pct"] = (
            100 * safe_divide(out["operating_income"], out["revenue"])
        ).round(2)

    if {"net_income", "revenue"}.issubset(out.columns):
        out["net_margin_pct"] = (
            100 * safe_divide(out["net_income"], out["revenue"])
        ).round(2)

    if "revenue" in out:
        out["revenue_growth_pct"] = (100 * out["revenue"].pct_change()).round(2)
        out["revenue_yoy_change"] = out["revenue"].diff()

    if "operating_income" in out:
        out["operating_income_yoy_change"] = out["operating_income"].diff()

    if "net_income" in out:
        out["net_income_yoy_change"] = out["net_income"].diff()

    if {"operating_cash_flow", "revenue"}.issubset(out.columns):
        out["operating_cash_flow_margin_pct"] = (
            100 * safe_divide(out["operating_cash_flow"], out["revenue"])
        ).round(2)

    if {"liabilities", "assets"}.issubset(out.columns):
        out["liabilities_to_assets_pct"] = (
            100 * safe_divide(out["liabilities"], out["assets"])
        ).round(2)

    return out


def variance_summary(kpis: pd.DataFrame) -> pd.DataFrame:
    """Return latest-year absolute and percentage variances vs prior fiscal year."""
    x = kpis.sort_values("fiscal_year")
    if len(x) < 2:
        return pd.DataFrame()
    current, prior = x.iloc[-1], x.iloc[-2]
    rows = []
    for metric in ["revenue", "cost_of_revenue", "operating_income", "net_income", "operating_cash_flow"]:
        if metric not in x.columns or pd.isna(current.get(metric)) or pd.isna(prior.get(metric)):
            continue
        absolute = current[metric] - prior[metric]
        pct = np.nan if prior[metric] == 0 else 100 * absolute / abs(prior[metric])
        rows.append({
            "metric": metric,
            "current_fiscal_year": int(current["fiscal_year"]),
            "prior_fiscal_year": int(prior["fiscal_year"]),
            "current_value": current[metric],
            "prior_value": prior[metric],
            "absolute_variance": absolute,
            "variance_pct": round(pct, 2) if not pd.isna(pct) else np.nan,
        })
    return pd.DataFrame(rows)


def executive_summary(kpis: pd.DataFrame) -> pd.DataFrame:
    """Compact latest-year table for executive review."""
    if kpis.empty:
        return pd.DataFrame()
    latest = kpis.sort_values("fiscal_year").iloc[-1]
    fields = [
        "fiscal_year", "revenue", "revenue_growth_pct", "gross_margin_pct",
        "operating_margin_pct", "net_margin_pct", "operating_cash_flow_margin_pct",
        "assets", "liabilities", "liabilities_to_assets_pct",
    ]
    return pd.DataFrame([{f: latest.get(f, np.nan) for f in fields}])
