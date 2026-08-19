# Data Source & Provenance

## Source

DA-08 uses public company financial statement facts from the **U.S. Securities and Exchange Commission (SEC) EDGAR Company Facts API**.

The case study is configured around a large U.S. public company and retrieves standardized US-GAAP facts such as revenue, cost of revenue, operating income, net income, assets, liabilities, and operating cash flow when those facts are available in the issuer's SEC filings.

## Why SEC data

This project deliberately avoids retail transaction datasets that contain sales price but no accounting cost basis. Financial profitability metrics should not be fabricated from incomplete commercial data. SEC filings provide a stronger provenance trail for financial-statement analytics and allow the repository to distinguish reported accounting measures from derived ratios.

## Reproducible acquisition

Run:

```bash
python -m src.download_data
```

The script calls the official SEC `data.sec.gov` Company Facts endpoint with a descriptive User-Agent and writes the raw JSON to `data/raw/`, which is excluded from Git history.

## Analytical grain

The normalized analytical table is **one row per fiscal year**. Annual facts are selected from SEC filing observations using fiscal period (`FY`) and filing metadata. Derived KPIs are calculated only after facts have been aligned to the same fiscal-year grain.

## Claim boundaries

- Values are reported public-company accounting facts, not internal management-accounting data.
- Derived margins and growth rates are analytical calculations, not company guidance.
- Missing accounting concepts are kept missing; they are not imputed or invented.
- The project does not claim product/customer-level profitability because SEC statements do not provide that grain.
- This is financial analytics, not investment advice or a valuation recommendation.

## Official references

- SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- Company Facts endpoint: https://data.sec.gov/api/xbrl/companyfacts/
