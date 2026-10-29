# -*- coding: utf-8 -*-
"""
SQL Analysis - sqlite3
Creates spacex.db, loads the cleaned dataset, and runs the
capstone-required queries. Results saved to sql/sql_results.txt
"""
import os, sys, sqlite3
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..")
df = pd.read_csv(os.path.join(BASE, "data", "dataset_part_2.csv"))
db_path = os.path.join(BASE, "data", "spacex.db")
conn = sqlite3.connect(db_path)
df.to_sql("SPACEXTBL", conn, if_exists="replace", index=False,
          dtype={"Date": "TEXT"})

QUERIES = [
    ("1. Unique launch site names",
     'SELECT DISTINCT LaunchSite FROM SPACEXTBL'),
    ("2. Total payload mass of launches on 2010-01-01 to 2024-12-31 (0-10000 kg, Falcon 9)",
     """SELECT SUM(PayloadMass) AS TotalPayloadMass
        FROM SPACEXTBL
        WHERE BoosterVersion LIKE 'Falcon 9%'
          AND PayloadMass BETWEEN 0 AND 10000"""),
    ("3. First launch date of each site",
     'SELECT LaunchSite, MIN(Date) AS FirstLaunch FROM SPACEXTBL GROUP BY LaunchSite'),
    ("4. Payload mass 4000-6000 kg",
     'SELECT BoosterVersion, LaunchSite, Date, PayloadMass FROM SPACEXTBL '
     'WHERE PayloadMass BETWEEN 4000 AND 6000'),
    ("5. Success rate by launch site (ranking)",
     """SELECT LaunchSite,
               COUNT(*) AS Attempts,
               SUM(Class) AS Successes,
               ROUND(100.0 * SUM(Class) / COUNT(*), 1) AS SuccessRate
        FROM SPACEXTBL GROUP BY LaunchSite
        ORDER BY SuccessRate DESC"""),
    ("6. Top 5 boosters (Serial) by total successful landings",
     """SELECT Serial, COUNT(*) AS Attempts, SUM(Class) AS Successes
        FROM SPACEXTBL WHERE Serial != 'Unknown'
        GROUP BY Serial ORDER BY Successes DESC LIMIT 5"""),
    ("7. Launches per year trend",
     """SELECT SUBSTR(Date, 1, 4) AS Year, COUNT(*) AS Launches,
               ROUND(100.0 * SUM(Class) / COUNT(*), 1) AS SuccessRate
        FROM SPACEXTBL GROUP BY Year ORDER BY Year"""),
    ("8. Average payload mass per orbit",
     'SELECT Orbit, ROUND(AVG(PayloadMass), 1) AS AvgPayload FROM SPACEXTBL '
     'GROUP BY Orbit ORDER BY AvgPayload DESC'),
]

lines = []
for title, q in QUERIES:
    lines.append("=" * 70)
    lines.append(title)
    lines.append("-" * 70)
    try:
        res = pd.read_sql_query(q, conn)
        lines.append(res.to_string(index=False))
    except Exception as e:
        lines.append(f"ERROR: {e}")
conn.close()

out = os.path.join(BASE, "sql", "sql_results.txt")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("\n".join(lines))
print(f"\nSaved -> {out}")
