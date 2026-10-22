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

async def run_test():
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
            async def send_cmd(method, params=None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
                while True:
                    resp = json.loads(await ws.recv())
                    if resp.get("id") == cid:
                        r = resp.get("result", {})
                        if "result" in r and "value" in r["result"]:
                            return r["result"]["value"]
                        return r

            async def eval_js(expression):
                return await send_cmd("Runtime.evaluate", {"expression": expression, "returnByValue": True})

            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")
            await send_cmd("DOM.enable")

            file_path = os.path.abspath("index.html").replace("\\", "/")
            await send_cmd("Page.navigate", {"url": f"file:///{file_path}"})
            await asyncio.sleep(1.0)

            # Viewport iPhone 16 Landscape: 852 x 393
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 852,
                "height": 393,
                "deviceScaleFactor": 1,
                "mobile": True,
                "screenOrientation": {"type": "landscapePrimary", "angle": 90}
            })
            await asyncio.sleep(0.5)

            # Follow real UI flow:
            # 1. Click Mulai Petualangan Baru
            await eval_js("document.getElementById('btn-start-game').click();")
            await asyncio.sleep(0.4)

            # 2. Click 4 Groups
            await eval_js("document.querySelector('.btn-count-choice[data-count=\"4\"]').click();")
            await asyncio.sleep(0.4)

            # 3. If role reminder modal is open, click Siap
            await eval_js("""
                const btnReady = document.getElementById('btn-proceed-to-game');
                if (btnReady) btnReady.click();
            """)
            await asyncio.sleep(0.5)

            # Check screen-board state
            check_data = await eval_js("""
                (() => {
                    const board = document.getElementById('screen-board');
                    const isBoardActive = board.classList.contains('active');
                    const stamps = Array.from(document.querySelectorAll('.norma-stamp')).map(s => {
                        const r = s.getBoundingClientRect();
                        const handle = s.querySelector('.stamp-wood-handle');
                        const hr = handle ? handle.getBoundingClientRect() : null;
                        const name = s.querySelector('.stamp-name');
                        const desc = s.querySelector('.stamp-desc');
                        return {
                            norma: s.dataset.norma,
                            top: Math.round(r.top),
                            bottom: Math.round(r.bottom),
                            height: Math.round(r.height),
                            visible: r.width > 0 && r.height > 0 && window.getComputedStyle(s).display !== 'none',
                            handleVisible: handle && hr.height > 0 && window.getComputedStyle(handle).display !== 'none',
                            handleHeight: hr ? Math.round(hr.height) : 0,
                            name: name ? name.textContent.trim() : '',
                            desc: desc ? desc.textContent.trim() : ''
                        };
                    });

                    const feedbackBar = document.getElementById('case-feedback-bar');
                    const reasonPanel = document.getElementById('reason-panel');
                    const fbComputed = window.getComputedStyle(feedbackBar);
                    const rpComputed = window.getComputedStyle(reasonPanel);

                    return {
                        isBoardActive,
                        viewport: { w: window.innerWidth, h: window.innerHeight },
                        allStampsVisible: stamps.every(s => s.visible),
                        allHandlesVisible: stamps.every(s => s.handleVisible),
                        stamps,
                        feedbackBarDisplay: fbComputed.display,
                        reasonPanelDisplay: rpComputed.display
                    };
                })()
            """)
            print("REAL UI BOARD CHECK (Case 1 Started):", json.dumps(check_data, indent=2))

            # Screenshot initial case
            shot1 = await send_cmd("Page.captureScreenshot", {"format": "png"})
            with open("screenshot_landscape_case1.png", "wb") as f:
                f.write(base64.b64decode(shot1["data"]))
            print("Saved screenshot_landscape_case1.png")

            # Click Team 1 to activate stamps
            await eval_js("document.querySelectorAll('.team-card-btn')[0].click();")
            await asyncio.sleep(0.3)

            active_check = await eval_js("""
                (() => {
                    const activeStamps = Array.from(document.querySelectorAll('.norma-stamp.active')).map(s => s.dataset.norma);
                    const targetText = document.getElementById('case-target-indicator').textContent;
                    return { activeStamps, targetText };
                })()
            """)
            print("AFTER SELECTING TEAM 1:", json.dumps(active_check, indent=2))

            # Screenshot after selecting team (stamps active!)
            shot2 = await send_cmd("Page.captureScreenshot", {"format": "png"})
            with open("screenshot_landscape_case1_active.png", "wb") as f:
                f.write(base64.b64decode(shot2["data"]))
            print("Saved screenshot_landscape_case1_active.png")

            # Now answer the case by clicking the active stamp matching the case
            await eval_js("""
                (() => {
                    const caseText = document.getElementById('folder-case-text').textContent;
                    // Find the matching stamp by clicking the first active stamp (e.g., agama)
                    // Or let's click the actual correct one:
                    const caseIdx = parseInt(document.getElementById('case-progress-text').textContent.match(/\\d+/)[0]) - 1;
                    // Let's click any active stamp
                    const firstActive = document.querySelector('.norma-stamp.active');
                    if (firstActive) firstActive.click();
                })()
            """)
            await asyncio.sleep(1.0)

            # Check after answer
            check_answered = await eval_js("""
                (() => {
                    const feedbackBar = document.getElementById('case-feedback-bar');
                    const reasonPanel = document.getElementById('reason-panel');
                    const fbComputed = window.getComputedStyle(feedbackBar);
                    const rpComputed = window.getComputedStyle(reasonPanel);
                    const feedbackText = document.getElementById('feedback-text').textContent;
                    return {
                        feedbackText,
                        feedbackBarDisplay: fbComputed.display,
                        reasonPanelDisplay: rpComputed.display
                    };
                })()
            """)
            print("AFTER ANSWER:", json.dumps(check_answered, indent=2))

            # Screenshot after answer
            shot3 = await send_cmd("Page.captureScreenshot", {"format": "png"})
            with open("screenshot_landscape_case1_answered.png", "wb") as f:
                f.write(base64.b64decode(shot3["data"]))
            print("Saved screenshot_landscape_case1_answered.png")

    finally:
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(run_test())
