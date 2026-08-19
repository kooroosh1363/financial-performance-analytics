from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_JSON = ROOT / "data" / "raw" / "companyfacts.json"
RAW_PINNED = ROOT / "data" / "raw" / "annual_financials_source.csv"
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
    values = fact.get("units", {}).get("USD", [])
    df = pd.DataFrame(values)
    if df.empty or "fy" not in df or "fp" not in df:
        return pd.DataFrame()
    df = df[(df["fp"] == "FY") & df["fy"].notna()].copy()
    if df.empty:
        return df
    df["filed"] = pd.to_datetime(df["filed"], errors="coerce")
    return df.sort_values("filed").drop_duplicates("fy", keep="last")


def normalize_live_companyfacts() -> tuple[pd.DataFrame, pd.DataFrame]:
    payload = json.loads(RAW_JSON.read_text(encoding="utf-8"))
    us_gaap = payload["facts"]["us-gaap"]
    series, provenance = {}, []
    for metric, candidates in CONCEPTS.items():
        concept, fact = choose_concept(us_gaap, candidates)
        if not fact:
            continue
        annual = annual_observations(fact)
        if annual.empty:
            continue
        series[metric] = annual.set_index("fy")["val"]
        provenance.append({"metric": metric, "source": "SEC Company Facts", "sec_concept": concept})
    if "revenue" not in series:
        raise ValueError("No supported annual revenue concept found in SEC Company Facts.")
    frame = pd.DataFrame(series).sort_index().reset_index().rename(columns={"fy": "fiscal_year"})
    frame = frame[frame["fiscal_year"].between(2015, 2100)].copy()
    return frame, pd.DataFrame(provenance)


def normalize_pinned_snapshot() -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = pd.read_csv(RAW_PINNED)
    required = {"fiscal_year", "revenue", "cost_of_revenue", "operating_income", "net_income", "operating_cash_flow", "assets", "liabilities"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Pinned SEC snapshot missing required columns: {missing}")
    provenance = pd.DataFrame([
        {"metric": metric, "source": "Apple 2025 Form 10-K pinned filing snapshot", "sec_concept": "filing-statement value"}
        for metric in sorted(required - {"fiscal_year"})
    ])
    return frame.sort_values("fiscal_year"), provenance


def main() -> None:
    if RAW_JSON.exists():
        frame, provenance = normalize_live_companyfacts()
        source = "live SEC Company Facts"
    elif RAW_PINNED.exists():
        frame, provenance = normalize_pinned_snapshot()
        source = "pinned SEC filing snapshot"
    else:
        raise FileNotFoundError("No SEC source data found. Run python -m src.download_data first.")

    PROCESSED.mkdir(parents=True, exist_ok=True)
    frame.to_csv(PROCESSED / "annual_financials.csv", index=False)
    provenance.to_csv(PROCESSED / "concept_provenance.csv", index=False)
    print(f"Normalized {len(frame)} fiscal years from {source}")


if __name__ == "__main__":
    main()
