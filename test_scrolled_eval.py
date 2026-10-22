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

async def test_scrolled_eval():
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

            # Start game 4 groups
            await eval_js("document.getElementById('btn-start-game').click()")
            await asyncio.sleep(0.3)
            await eval_js("document.querySelector('.btn-count-choice[data-count=\"4\"]').click()")
            await asyncio.sleep(0.3)
            await eval_js("const b = document.getElementById('btn-proceed-to-game'); if(b) b.click();")
            await asyncio.sleep(0.5)

            # Select Team 1 & Answer
            await eval_js("document.querySelectorAll('.team-card-btn')[0].click()")
            await asyncio.sleep(0.3)
            correct_norma = await eval_js("State.sessionCases[State.currentCaseIndex].jawabanId")
            await eval_js(f"document.querySelector('.norma-stamp[data-norma=\"{correct_norma}\"]').click()")
            await asyncio.sleep(0.8)

            # Scroll folder down to bottom or scroll evaluation buttons into view
            scroll_info = await eval_js("""(() => {
                const folder = document.getElementById('case-folder');
                const btnSensible = document.getElementById('btn-reason-sensible');
                const btnPass = document.getElementById('btn-reason-pass');
                const stampSolved = document.getElementById('stamp-terpecahkan');
                
                // Scroll folder to bottom
                folder.scrollTop = folder.scrollHeight;
                
                const br1 = btnSensible.getBoundingClientRect();
                const br2 = btnPass.getBoundingClientRect();
                const sr = stampSolved ? stampSolved.getBoundingClientRect() : null;
                
                return {
                    folderScrollTop: folder.scrollTop,
                    folderScrollHeight: folder.scrollHeight,
                    btnSensible: { top: Math.round(br1.top), bottom: Math.round(br1.bottom), width: Math.round(br1.width), height: Math.round(br1.height) },
                    btnPass: { top: Math.round(br2.top), bottom: Math.round(br2.bottom), width: Math.round(br2.width), height: Math.round(br2.height) },
                    stampSolved: sr ? { top: Math.round(sr.top), bottom: Math.round(sr.bottom), width: Math.round(sr.width), height: Math.round(sr.height) } : null
                };
            })()""")
            print("SCROLL INFO:", json.dumps(scroll_info, indent=2))

            shot = await cmd("Page.captureScreenshot", {"format": "png"})
            with open("screenshot_landscape_eval_scrolled.png", "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print("Saved screenshot_landscape_eval_scrolled.png")

    finally:
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(test_scrolled_eval())
