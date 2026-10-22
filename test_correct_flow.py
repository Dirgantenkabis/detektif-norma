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

async def test_correct():
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
        ws_url = tabs[0]["webSocketDebuggerUrl"]

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

            # Select Team 1
            await eval_js("document.querySelectorAll('.team-card-btn')[0].click()")
            await asyncio.sleep(0.3)

            # Click correct stamp!
            correct_norma = await eval_js("State.sessionCases[State.currentCaseIndex].jawabanId")
            print("Correct norma for case 1:", correct_norma)
            await eval_js(f"document.querySelector('.norma-stamp[data-norma=\"{correct_norma}\"]').click()")
            await asyncio.sleep(1.0)

            # Check after correct answer
            data = await eval_js("""(() => {
                const feedbackBar = document.getElementById('case-feedback-bar');
                const reasonPanel = document.getElementById('reason-panel');
                const btnNext = document.getElementById('btn-next-case');
                const stampSolved = document.getElementById('stamp-terpecahkan');
                return {
                    feedbackDisplay: window.getComputedStyle(feedbackBar).display,
                    reasonDisplay: window.getComputedStyle(reasonPanel).display,
                    nextBtnDisplay: btnNext ? window.getComputedStyle(btnNext).display : null,
                    stampSolvedHasShow: stampSolved.classList.contains('show'),
                    feedbackText: document.getElementById('feedback-text').textContent
                };
            })()""")
            print("CORRECT ANSWER EVALUATION STATE:", json.dumps(data, indent=2))

            # Capture screenshot
            shot = await cmd("Page.captureScreenshot", {"format": "png"})
            with open("screenshot_landscape_correct_solved.png", "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print("Saved screenshot_landscape_correct_solved.png")

            # Click Kasus Berikutnya!
            await eval_js("document.getElementById('btn-next-case').click()")
            await asyncio.sleep(0.8)

            # Check Case 2 state
            case2_data = await eval_js("""(() => {
                const feedbackBar = document.getElementById('case-feedback-bar');
                const reasonPanel = document.getElementById('reason-panel');
                const progressText = document.getElementById('case-progress-text').textContent;
                const stamps = Array.from(document.querySelectorAll('.norma-stamp')).map(s => {
                    const r = s.getBoundingClientRect();
                    return {
                        norma: s.dataset.norma,
                        visible: r.width > 0 && r.height > 0,
                        disabled: s.disabled
                    };
                });
                return {
                    progressText,
                    feedbackDisplay: window.getComputedStyle(feedbackBar).display,
                    reasonDisplay: window.getComputedStyle(reasonPanel).display,
                    stampsAllVisible: stamps.every(s => s.visible),
                    stampsAllDisabled: stamps.every(s => s.disabled)
                };
            })()""")
            print("CASE 2 STARTED STATE:", json.dumps(case2_data, indent=2))

            shot2 = await cmd("Page.captureScreenshot", {"format": "png"})
            with open("screenshot_landscape_case2.png", "wb") as f:
                f.write(base64.b64decode(shot2["data"]))
            print("Saved screenshot_landscape_case2.png")

    finally:
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(test_correct())
