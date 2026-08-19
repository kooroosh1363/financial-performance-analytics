from pathlib import Path

import pandas as pd

from .analytics import build_financial_kpis, executive_summary, variance_summary

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "annual_financials.csv"
OUT = ROOT / "outputs"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    financials = pd.read_csv(INPUT)
    kpis = build_financial_kpis(financials)
    kpis.to_csv(OUT / "financial_kpis_by_year.csv", index=False)
    variance_summary(kpis).to_csv(OUT / "latest_year_variance.csv", index=False)
    executive_summary(kpis).to_csv(OUT / "executive_summary.csv", index=False)
    print(executive_summary(kpis).to_string(index=False))


if __name__ == "__main__":
    main()
