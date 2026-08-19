from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PINNED = ROOT / "data" / "source" / "apple_2025_10k_financials.csv"
CIK = os.getenv("SEC_CIK", "0000320193")  # Apple Inc. default case study
USER_AGENT = os.getenv("SEC_USER_AGENT", "DA-08 portfolio analytics contact@example.com")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    mode = os.getenv("SEC_DATA_MODE", "live").lower()

    if mode == "pinned":
        output = RAW / "annual_financials_source.csv"
        shutil.copyfile(PINNED, output)
        print(f"Using pinned SEC-filing snapshot: {output}")
        return

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK.zfill(10)}.json"
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Encoding": "identity",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            payload = json.load(response)
    except (HTTPError, URLError) as exc:
        raise RuntimeError(
            "Live SEC Company Facts acquisition failed. SEC may throttle or block shared CI IPs. "
            "For deterministic validation use SEC_DATA_MODE=pinned; the pinned snapshot is transcribed "
            "from the cited Apple 2025 Form 10-K and remains auditable."
        ) from exc

    output = RAW / "companyfacts.json"
    output.write_text(json.dumps(payload), encoding="utf-8")
    print(f"Saved SEC company facts for {payload.get('entityName')} to {output}")


if __name__ == "__main__":
    main()
