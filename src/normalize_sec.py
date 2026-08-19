from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "companyfacts.json"
PROCESSED = ROOT / "data" / "processed"

CONCEPTS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"],
    "cost_of_revenue": ["CostOfRevenue", "CostOfGoodsAndServicesSold"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "assets": ["Assets"],
    "liabilities": ["Liabilities"],
}


def choose_concept(us_gaap: dict, candidates: list[str]) -> tuple[str, dict] | tuple[None, None]:
    for concept in candidates:
        if concept in us_gaap:
            return concept, us_gaap[concept]
    return None, None


def annual_observations(fact: dict) -> pd.DataFrame:
    units = fact.get("units", {})
    values = units.get("USD", [])
    df = pd.DataFrame(values)
    if df.empty:
        return df
    df = df[(df.get("fp") == "FY") & df.get("fy").notna()].copy()
    if df.empty:
        return df
    df["filed"] = pd.to_datetime(df["filed"], errors="coerce")
    # Prefer the most recently filed observation for each fiscal year.
    return df.sort_values("filed").drop_duplicates("fy", keep="last")


def main() -> None:
    payload = json.loads(RAW.read_text(encoding="utf-8"))
    us_gaap = payload["facts"]["us-gaap"]
    series = {}
    provenance = []
    for metric, candidates in CONCEPTS.items():
        concept, fact = choose_concept(us_gaap, candidates)
        if not fact:
            continue
        annual = annual_observations(fact)
        if annual.empty:
            continue
        series[metric] = annual.set_index("fy")["val"]
        provenance.append({"metric": metric, "sec_concept": concept})

    if "revenue" not in series:
        raise ValueError("No supported annual revenue concept found in SEC Company Facts.")

    frame = pd.DataFrame(series).sort_index().reset_index().rename(columns={"fy": "fiscal_year"})
    frame = frame[frame["fiscal_year"].between(2015, 2100)].copy()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    frame.to_csv(PROCESSED / "annual_financials.csv", index=False)
    pd.DataFrame(provenance).to_csv(PROCESSED / "concept_provenance.csv", index=False)
    print(f"Normalized {len(frame)} fiscal years for {payload.get('entityName')}")


if __name__ == "__main__":
    main()
