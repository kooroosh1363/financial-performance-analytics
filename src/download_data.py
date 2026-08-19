from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CIK = os.getenv("SEC_CIK", "0000320193")  # Apple Inc. default case study
USER_AGENT = os.getenv("SEC_USER_AGENT", "DA-08 portfolio analytics contact@example.com")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK.zfill(10)}.json"
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "gzip, deflate"})
    with urlopen(request, timeout=60) as response:
        payload = json.load(response)
    output = RAW / "companyfacts.json"
    output.write_text(json.dumps(payload), encoding="utf-8")
    print(f"Saved SEC company facts for {payload.get('entityName')} to {output}")


if __name__ == "__main__":
    main()
