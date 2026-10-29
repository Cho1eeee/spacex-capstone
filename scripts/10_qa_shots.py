# -*- coding: utf-8 -*-
"""Quick visual QA: screenshot selected slides."""
import os
from playwright.sync_api import sync_playwright

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HTML = "file:///" + os.path.join(BASE, "slides", "slides.html").replace("\\", "/")
QA = os.path.join(BASE, "slides", "qa")
os.makedirs(QA, exist_ok=True)
IDX = [1, 2, 5, 7, 12]

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    page = b.new_page(viewport={"width": 1280, "height": 720})
    page.goto(HTML, wait_until="networkidle")
    page.wait_for_timeout(2000)
    slides = page.locator(".slide")
    for i in IDX:
        slides.nth(i).screenshot(path=os.path.join(QA, f"slide_{i+1:02d}.png"))
    b.close()
print("QA shots saved:", sorted(os.listdir(QA)))
