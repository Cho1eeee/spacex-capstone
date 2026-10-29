# -*- coding: utf-8 -*-
"""
Data Collection - Web Scraping (NextSpaceFlight.com)
====================================================
Scrapes the public launches listing page with requests + BeautifulSoup:
  requests.get(url)  ->  raw HTML  ->  soup.find_all(...)  ->  DataFrame
Extracts: mission name, rocket family, launch provider, launch location.
Then cross-validates against the SpaceX API dataset (launch sites).
Outputs: data/spacex_web_scraped.csv
"""
import os, sys, re
import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://nextspaceflight.com/launches/"
OUT = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)


def scrape():
    print("[1/4] requests.get() downloading page HTML ...")
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (capstone-etl)"}, timeout=60)
    r.raise_for_status()
    print(f"      -> HTTP {r.status_code}, {len(r.text):,} chars")

    print("[2/4] BeautifulSoup parsing ...")
    soup = BeautifulSoup(r.text, "lxml")
    rows = []
    for h3 in soup.find_all("h3"):
        card = h3.find_parent("a")
        card = card.find_parent("div") if card else h3.find_parent("div")
        if not card:
            continue
        spans = [s.get_text(" ", strip=True) for s in card.find_all("span")]
        rocket = next((s for s in spans if "|" in s), "")
        loc = next((s for s in spans if re.search(r"^[A-Z].*, .*, (USA|CHN|NZL|RUS|FRA|IND|JPN)$", s)), "")
        if not rocket:
            continue
        rows.append({
            "Mission": h3.get_text(" ", strip=True),
            "Rocket": rocket.split("|")[0].strip(),
            "Provider": rocket.split("|")[-1].strip(),
            "LaunchLocation": loc,
        })
    df = pd.DataFrame(rows)
    df["Country"] = df["LaunchLocation"].str.extract(r"([A-Z]{3}$)")
    return df


def main():
    df = scrape()
    print(f"[3/4] Parsed {len(df)} launch cards")
    print(df.head(8).to_string())

    print("[4/4] Saving + cross-validation with API dataset ...")
    out_csv = os.path.join(OUT, "spacex_web_scraped.csv")
    df.to_csv(out_csv, index=False)

    api_df = pd.read_csv(os.path.join(OUT, "spacex_launch_data.csv"))
    scraped_spacex = df[df.Provider == "SpaceX"]
    print(f"\nScraped SpaceX launches on listing page: {len(scraped_spacex)}")
    print("Scraped launch locations (SpaceX):",
          sorted(set(scraped_spacex.LaunchLocation))[:6])
    print("API dataset launch sites:", sorted(set(api_df.LaunchSite)))
    f9 = api_df[api_df.BoosterVersion == "Falcon 9"]
    print(f"API dataset: {len(f9)} Falcon 9 records, "
          f"success rate {f9.Class.mean():.1%}")
    print(f"Saved -> {out_csv}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
