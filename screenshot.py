#!/usr/bin/env python3
"""Takes a picture of the map (map.png) for the Discord bot's morning post.

Runs after update.py in the daily GitHub Action:  python screenshot.py
Needs:  pip install playwright && python -m playwright install --with-deps chromium
"""
import os, threading, http.server, socketserver, functools
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8765

def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd

def main():
    httpd = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1100, "height": 1200}, device_scale_factor=1.5)
            page.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="networkidle")
            page.wait_for_selector("#regs path", timeout=20000)
            page.add_style_tag(content="#zin,#zout,#zrs{display:none!important}")
            page.wait_for_timeout(1500)
            target = page.query_selector("#mapcard") or page.query_selector("#map")
            target.screenshot(path=os.path.join(HERE, "map.png"))
            browser.close()
        print("map.png written")
    finally:
        httpd.shutdown()

if __name__ == "__main__":
    main()
