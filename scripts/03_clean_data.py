# -*- coding: utf-8 -*-
"""
Data Wrangling / Cleaning
=========================
1. Load raw API dataset
2. Compute launch outcome label:  class = 1 (success) / 0 (failure)
3. Clean PayloadMass (missing -> mean of same booster version)
4. Parse dates -> Year column
5. One-hot encode BoosterVersion / Orbit / LaunchSite / LandingPad
Outputs: data/dataset_part_2.csv  (labelled, clean)
         data/dataset_part_3.csv  (one-hot features for ML)
"""
import os, sys
import numpy as np
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..", "data")


def main():
    print("[1/6] Loading raw data ...")
    df = pd.read_csv(os.path.join(BASE, "spacex_launch_data.csv"))
    print(f"      shape = {df.shape}")

    print("[2/6] Deriving outcome class (1 = booster landing success) ...")
    # Outcome looks like 'True ASDS' / 'False Ocean' / 'None None'
    outcome = df["Outcome"].astype(str)
    df["Class"] = outcome.str.startswith("True").astype(int)
    df["LandingAttempt"] = (~outcome.str.startswith("None")).astype(int)

    print("[3/6] Cleaning payload mass ...")
    n_missing = df["PayloadMass"].isna().sum()
    df["PayloadMass"] = df.groupby("BoosterVersion")["PayloadMass"] \
                          .transform(lambda s: s.fillna(s.mean()))
    df["PayloadMass"] = df["PayloadMass"].fillna(df["PayloadMass"].mean())
    df["PayloadMass"] = df["PayloadMass"].clip(lower=0, upper=30000)
    print(f"      filled {n_missing} missing values")

    print("[4/6] Parsing dates ...")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year

    print("[5/6] Filling categorical NaN ...")
    for c in ["Orbit", "LaunchSite", "LandingPad", "BoosterVersion", "Serial"]:
        df[c] = df[c].fillna("Unknown")

    part2 = os.path.join(BASE, "dataset_part_2.csv")
    df.to_csv(part2, index=False)
    print(f"Saved -> {part2}")

    print("[6/6] One-hot encoding features ...")
    features = df[["FlightNumber", "PayloadMass", "Orbit", "LaunchSite",
                   "Flights", "GridFins", "Reused", "Legs", "LandingPad",
                   "Block", "ReusedCount", "Serial"]]
    features = pd.get_dummies(features, columns=["Orbit", "LaunchSite", "LandingPad", "Serial"])
    features = pd.concat([features, df["Class"]], axis=1)
    features = features.fillna(0).astype({"Block": "float64"})
    part3 = os.path.join(BASE, "dataset_part_3.csv")
    features.to_csv(part3, index=False)
    print(f"Saved -> {part3}   shape = {features.shape}")

    print("\nClass distribution (landing attempts only):")
    print(df[df.LandingAttempt == 1]["Class"].value_counts())
    print("\nSuccess rate by site:")
    print(df.groupby("LaunchSite")["Class"].agg(["count", "mean"]).round(3))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
