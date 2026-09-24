"""
browser_qa.py
=============
Automated Chrome DevTools Protocol (CDP) browser test runner.
Controls Microsoft Edge in headless mode via CDP to capture actual rendered
browser screenshots and test responsiveness.
"""

import json
import time
import base64
import subprocess
from pathlib import Path
import urllib.request
import websocket


def get_edge_executable() -> str:
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    raise FileNotFoundError("No Chromium browser (Edge/Chrome) found on system.")


class CDPBrowser:
    def __init__(self, port=9222):
        self.port = port
        self.proc = None
        self.ws = None
        self.msg_id = 0

    def start(self, url="http://localhost:8501", width=1400, height=900):
        exe = get_edge_executable()
        cmd = [
            exe,
            "--headless=new",
            "--disable-gpu",
            f"--remote-debugging-port={self.port}",
            f"--window-size={width},{height}",
            url,
        ]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)

        # Get list of targets
        for _ in range(10):
            try:
                targets_data = urllib.request.urlopen(f"http://localhost:{self.port}/json").read()
                targets = json.loads(targets_data)
                page_target = next((t for t in targets if t.get("type") == "page" and "8501" in t.get("url", "")), None)
                if not page_target:
                    page_target = targets[0]
                ws_url = page_target["webSocketDebuggerUrl"]
                self.ws = websocket.create_connection(ws_url)
                return
            except Exception:
                time.sleep(1)
        raise RuntimeError("Failed to connect to browser CDP target.")

    def send_cdp(self, method: str, params: dict = None) -> dict:
        self.msg_id += 1
        msg = {"id": self.msg_id, "method": method, "params": params or {}}
        self.ws.send(json.dumps(msg))
        while True:
            res = json.loads(self.ws.recv())
            if res.get("id") == self.msg_id:
                return res

    def wait_for_selector(self, selector: str, timeout_sec: int = 20) -> bool:
        start = time.time()
        expr = f"document.querySelector('{selector}') !== null"
        while time.time() - start < timeout_sec:
            res = self.send_cdp("Runtime.evaluate", {"expression": expr, "returnByValue": True})
            val = res.get("result", {}).get("result", {}).get("value", False)
            if val:
                return True
            time.sleep(0.5)
        return False

    def wait_until_not_running(self, timeout_sec: int = 20) -> bool:
        """Waits until Streamlit finish running indicator disappears."""
        start = time.time()
        expr = "document.querySelector('[data-testid=\"stStatusWidget\"]') === null"
        while time.time() - start < timeout_sec:
            res = self.send_cdp("Runtime.evaluate", {"expression": expr, "returnByValue": True})
            val = res.get("result", {}).get("result", {}).get("value", False)
            if val:
                return True
            time.sleep(0.5)
        return False

    def capture_screenshot(self, out_path: str):
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        res = self.send_cdp("Page.captureScreenshot", {"format": "png"})
        img_b64 = res["result"]["data"]
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(img_b64))
        print(f"Screenshot saved to {out_path} ({Path(out_path).stat().st_size:,} bytes)")

    def set_viewport(self, width: int, height: int, mobile: bool = False):
        self.send_cdp("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": mobile,
        })
        time.sleep(1)

    def close(self):
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=3)
            except Exception:
                pass


if __name__ == "__main__":
    browser = CDPBrowser()
    try:
        print("Starting browser...")
        browser.start()
        print("Waiting for Streamlit metrics to render...")
        found = browser.wait_for_selector('[data-testid="stMetricValue"]', timeout_sec=25)
        print("Metric found:", found)
        time.sleep(3)  # Let Plotly charts render completely
        browser.capture_screenshot("screenshots/01_desktop_default.png")

        # Test mobile viewport
        print("Testing mobile viewport (390x844)...")
        browser.set_viewport(width=390, height=844, mobile=True)
        time.sleep(2)
        browser.capture_screenshot("screenshots/02_mobile_layout.png")

        print("CDP browser test completed successfully!")
    finally:
        browser.close()
