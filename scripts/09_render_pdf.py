# -*- coding: utf-8 -*-
"""
Render slides.html -> final PDF (1280x720 per page) using the system
Edge browser via playwright's channel='msedge' (no browser download needed).
Output: report/SpaceX_Capstone_报告.pdf
"""
import os, sys
from playwright.sync_api import sync_playwright

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SLIDE_FILE = sys.argv[1] if len(sys.argv) > 1 else "slides.html"
OUT_FILE = sys.argv[2] if len(sys.argv) > 2 else "SpaceX_Capstone_Report.pdf"
HTML = "file:///" + os.path.join(BASE, "slides", SLIDE_FILE).replace("\\", "/")
OUT = os.path.join(BASE, "report", OUT_FILE)
os.makedirs(os.path.dirname(OUT), exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.goto(HTML, wait_until="networkidle")
    page.wait_for_timeout(2500)
    page.pdf(path=OUT, width="1280px", height="720px",
             print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    browser.close()
print("PDF saved ->", OUT)
