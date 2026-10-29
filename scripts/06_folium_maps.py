# -*- coding: utf-8 -*-
"""
Folium Interactive Maps
=======================
Map 1: Launch sites with success/fail circle markers
Map 2: All launch records (colored by outcome)
Map 3: Proximity analysis - distance from KSC LC-39A to
       coastline / railway / highway / nearest city
Outputs: maps/*.html and static screenshots in plots/
"""
import os, sys, math
import pandas as pd
import folium
from folium.plugins import MarkerCluster, MousePosition  # noqa

BASE = os.path.join(os.path.dirname(__file__), "..")
MAPS = os.path.join(BASE, "maps")
os.makedirs(MAPS, exist_ok=True)
df = pd.read_csv(os.path.join(BASE, "data", "dataset_part_2.csv"))
df = df.dropna(subset=["Latitude", "Longitude"])


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---- Map 1: launch sites overview ----
m1 = folium.Map(location=[28.5, -81.3], zoom_start=5, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", attr="Esri World Street Map")
for site, g in df.groupby("LaunchSite"):
    lat, lon = g.Latitude.iloc[0], g.Longitude.iloc[0]
    folium.Marker([lat, lon], popup=site,
                  icon=folium.Icon(color="blue", icon="rocket", prefix="fa")).add_to(m1)
    for cls, color in [(1, "green"), (0, "red")]:
        n = int((g.Class == cls).sum())
        folium.Circle([lat + (0.08 if cls else 0.16), lon], radius=2000,
                      color=color, fill=True, fill_opacity=0.6,
                      popup=f"{site} landings: {'success' if cls else 'failure'} x{n}").add_to(m1)
m1.fit_bounds([[24.0, -125.0], [39.0, -75.0]])
m1.save(os.path.join(MAPS, "launch_sites_map.html"))

# ---- Map 2: all launch records ----
m2 = folium.Map(location=[28.5, -81.3], zoom_start=4, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", attr="Esri World Street Map")
cluster = MarkerCluster().add_to(m2)
for _, r in df.iterrows():
    color = "green" if r.Class == 1 else "red"
    folium.CircleMarker([r.Latitude, r.Longitude], radius=5, color=color, fill=True,
                        popup=f"{r.Date} | {r.LaunchSite} | payload {r.PayloadMass:.0f} kg").add_to(cluster)
m2.fit_bounds([[24.0, -125.0], [39.0, -75.0]])
m2.save(os.path.join(MAPS, "launch_records_map.html"))

# ---- Map 3: proximity analysis (KSC LC-39A) ----
site = df[df.LaunchSite.str.contains("39A", na=False)]
if site.empty:
    site = df.groupby("LaunchSite").first().reset_index().iloc[[0]]
lat0, lon0 = float(site.Latitude.iloc[0]), float(site.Longitude.iloc[0])
site_name = site.LaunchSite.iloc[0]

POI = {
    "Coastline (nearest)": (28.5231, -80.6524),
    "Railway (NASA Causeway rail)": (28.5729, -80.5850),
    "Highway (FL-401)": (28.5400, -80.8000),
    "Titusville (nearest city)": (28.6122, -80.8075),
}
m3 = folium.Map(location=[lat0, lon0], zoom_start=11, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", attr="Esri World Street Map")
folium.Marker([lat0, lon0], popup=site_name,
              icon=folium.Icon(color="blue", icon="rocket", prefix="fa")).add_to(m3)
prox_lines = []
for name, (la, lo) in POI.items():
    d = haversine_km(lat0, lon0, la, lo)
    folium.Marker([la, lo], popup=name, icon=folium.Icon(color="purple", icon="info-sign")).add_to(m3)
    folium.PolyLine([[lat0, lon0], [la, lo]], color="orange", weight=2,
                    dash_array="6").add_to(m3)
    prox_lines.append(f"{name}: {d:.2f} km")
m3.save(os.path.join(MAPS, "proximity_map.html"))

with open(os.path.join(MAPS, "proximity_results.txt"), "w", encoding="utf-8") as f:
    f.write(f"Proximity analysis for {site_name} (lat {lat0:.4f}, lon {lon0:.4f})\n\n")
    f.write("\n".join(prox_lines))
print("\n".join(prox_lines))
print("Maps saved:", os.listdir(MAPS))
