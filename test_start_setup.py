import asyncio
import json
import os
import socket
import subprocess
import tempfile
import urllib.request
import websockets
import base64

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE_PATH):
    EDGE_PATH = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

def get_free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

async def test_start_setup():
    port = get_free_port()
    tmp_dir = tempfile.mkdtemp()
    proc = subprocess.Popen([
        EDGE_PATH,
        "--headless=new",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={tmp_dir}",
        "--disable-extensions",
        "--disable-gpu",
        "--no-sandbox"
    ])
    await asyncio.sleep(2.0)

    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json")
        tabs = json.loads(req.read().decode())
        page_tab = next(t for t in tabs if t.get("type") == "page")
        ws_url = page_tab["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
            msg_id = 1
            async def cmd(m, p=None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                await ws.send(json.dumps({"id": cid, "method": m, "params": p or {}}))
                while True:
                    resp = json.loads(await ws.recv())
                    if resp.get("id") == cid:
                        r = resp.get("result", {})
                        if "result" in r and "value" in r["result"]:
                            return r["result"]["value"]
                        return r

            async def eval_js(expr):
                return await cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True})

            file_path = os.path.abspath("index.html").replace("\\", "/")
            await cmd("Page.navigate", {"url": f"file:///{file_path}"})
            await asyncio.sleep(1.0)

            # Viewport iPhone 16 Landscape: 852 x 393
            await cmd("Emulation.setDeviceMetricsOverride", {
                "width": 852,
                "height": 393,
                "deviceScaleFactor": 1,
                "mobile": True,
                "screenOrientation": {"type": "landscapePrimary", "angle": 90}
            })
            await asyncio.sleep(0.3)

            # 1. Screenshot Start Screen
            shot1 = await cmd("Page.captureScreenshot", {"format": "png"})
            with open("screenshot_landscape_start.png", "wb") as f:
                f.write(base64.b64decode(shot1["data"]))
            print("Saved screenshot_landscape_start.png")

            # 2. Click Start Game to go to Setup Screen
            await eval_js("document.getElementById('btn-start-game').click()")
            await asyncio.sleep(0.5)

            shot2 = await cmd("Page.captureScreenshot", {"format": "png"})
            with open("screenshot_landscape_setup.png", "wb") as f:
                f.write(base64.b64decode(shot2["data"]))
            print("Saved screenshot_landscape_setup.png")

    finally:
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(test_start_setup())
