import pandas as pd

from src.analytics import build_financial_kpis, variance_summary


def sample_financials():
    return pd.DataFrame({
        "fiscal_year": [2023, 2024],
        "revenue": [1000.0, 1200.0],
        "cost_of_revenue": [600.0, 660.0],
        "operating_income": [200.0, 300.0],
        "net_income": [150.0, 240.0],
        "operating_cash_flow": [220.0, 330.0],
        "assets": [2000.0, 2400.0],
        "liabilities": [1000.0, 1080.0],
    })


def test_margin_calculations():
    x = build_financial_kpis(sample_financials())
    latest = x.iloc[-1]
    assert latest["gross_profit_derived"] == 540.0
    assert latest["gross_margin_pct"] == 45.0
    assert latest["operating_margin_pct"] == 25.0
    assert latest["net_margin_pct"] == 20.0


def test_growth_and_balance_sheet_ratio():
    x = build_financial_kpis(sample_financials())
    latest = x.iloc[-1]
    assert latest["revenue_growth_pct"] == 20.0
    assert latest["liabilities_to_assets_pct"] == 45.0


def test_variance_reconciles_to_year_difference():
    x = build_financial_kpis(sample_financials())
    v = variance_summary(x).set_index("metric")
    assert v.loc["revenue", "absolute_variance"] == 200.0
    assert v.loc["net_income", "absolute_variance"] == 90.0
