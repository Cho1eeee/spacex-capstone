# -*- coding: utf-8 -*-
"""
Plotly Dash Application
=======================
Interactive analytics dashboard:
  - Pie chart: success vs failure counts (overall or per site)
  - Scatter:   payload mass vs landing success, site dropdown filter
Run:  python 07_dash_app.py  ->  http://127.0.0.1:8050
"""
import os, sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

BASE = os.path.join(os.path.dirname(__file__), "..")
df = pd.read_csv(os.path.join(BASE, "data", "dataset_part_2.csv"))

_DEFAULT_SITE = os.environ.get("SITE_FILTER", "ALL")

app = Dash(__name__)
app.title = "SpaceX Launch Analytics Dashboard"
app.layout = html.Div(style={"fontFamily": "Segoe UI, Arial", "margin": "20px"}, children=[
    html.H1("SpaceX Falcon 9 Launch Analytics", style={"textAlign": "center", "color": "#1a3c6e"}),
    html.P("Data Science Capstone - landing success analysis",
           style={"textAlign": "center", "color": "#666"}),
    dcc.Dropdown(
        id="site-dropdown",
        options=[{"label": "All Sites", "value": "ALL"}] +
                [{"label": s, "value": s} for s in sorted(df.LaunchSite.unique())],
        value=_DEFAULT_SITE, clearable=False, style={"width": "60%", "margin": "auto"}),
    html.Br(),
    dcc.Graph(id="success-pie-chart"),
    html.Br(),
    dcc.Graph(id="payload-scatter-chart"),
])


@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value"))
def update_pie(site):
    d = df if site == "ALL" else df[df.LaunchSite == site]
    counts = d.Class.value_counts().rename(index={1: "Success", 0: "Failure"})
    fig = px.pie(values=counts.values, names=counts.index,
                 title=f"Landing Outcomes - {site}",
                 color_discrete_sequence=["#2ca02c", "#d62728"])
    return fig


@app.callback(
    Output("payload-scatter-chart", "figure"),
    Input("site-dropdown", "value"))
def update_scatter(site):
    d = df[df.PayloadMass > 0]
    if site != "ALL":
        d = d[d.LaunchSite == site]
    fig = px.scatter(d, x="PayloadMass", y="Class", color="BoosterVersion",
                     title="Payload Mass vs Landing Success",
                     labels={"Class": "Landing Outcome (0 fail / 1 success)"})
    fig.update_yaxes(tickvals=[0, 1])
    return fig


if __name__ == "__main__":
    port = int(os.environ.get("DASH_PORT", 8050))
    print(f"Dash running on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
