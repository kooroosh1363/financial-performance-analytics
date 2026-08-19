# Data Source & Provenance

## Source

DA-08 uses public financial-statement data from the **U.S. Securities and Exchange Commission (SEC) EDGAR**. The default case study is Apple Inc. (CIK `0000320193`).

The repository supports two source modes:

1. **Live Company Facts mode** — `python -m src.download_data` requests standardized US-GAAP facts from the official SEC `data.sec.gov` Company Facts endpoint.
2. **Pinned filing mode** — `SEC_DATA_MODE=pinned python -m src.download_data` uses a small, auditable snapshot transcribed from Apple's 2025 Form 10-K comparative financial statements for fiscal 2023–2025.

The pinned snapshot exists because SEC can throttle or return HTTP 403 to shared cloud/CI IP ranges. CI therefore validates the analytics deterministically against the cited filing instead of pretending that an external network dependency is reliable.

## Why SEC data

This project deliberately avoids retail transaction datasets that contain sales price but no accounting cost basis. Financial profitability metrics should not be fabricated from incomplete commercial data. SEC filings provide reported revenue, cost, income, cash-flow, asset, and liability values that support defensible financial-statement analytics.

## Analytical grain

The normalized analytical table is **one row per fiscal year**. Derived KPIs are calculated only after facts have been aligned to the same fiscal-year grain. The pinned snapshot stores USD millions exactly as displayed in the comparative statements; ratios and growth rates are unit-invariant.

## Metrics supported

- revenue and year-over-year growth
- cost of revenue / cost of sales
- derived gross profit and gross margin
- operating income and operating margin
- net income and net margin
- operating cash flow and cash-flow margin
- assets, liabilities, and liabilities/assets ratio
- latest-year absolute and percentage variance

## Claim boundaries

- Values are reported public-company accounting facts, not internal management-accounting data.
- Derived margins and growth rates are analytical calculations, not company guidance.
- Missing accounting concepts remain missing in live mode; they are not invented.
- The project does not claim product/customer-level profitability because SEC statements do not provide that grain.
- This is financial analytics, not investment advice or a valuation recommendation.

## Official references

- SEC EDGAR APIs: `https://www.sec.gov/search-filings/edgar-application-programming-interfaces`
- SEC Company Facts endpoint: `https://data.sec.gov/api/xbrl/companyfacts/`
- Apple 2025 Form 10-K: `https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm`
