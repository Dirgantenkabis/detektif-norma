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

async def run_podium_test():
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

            # Setup State.groups for 4 teams and trigger finish
            await eval_js("""
                (() => {
                    State.groups = [
                        { id: 1, nama: 'Kelompok 1', warna: '#E65100', skor: 32, correctCount: 7, correctTimes: [2.5, 3.1, 4.0, 3.2, 2.9, 3.5, 3.0], badges: [] },
                        { id: 2, nama: 'Kelompok 2', warna: '#1565C0', skor: 24, correctCount: 5, correctTimes: [3.5, 4.2, 5.1, 3.8, 4.5], badges: [] },
                        { id: 3, nama: 'Kelompok 3', warna: '#2E7D32', skor: 18, correctCount: 4, correctTimes: [4.1, 5.0, 4.8, 5.2], badges: [] },
                        { id: 4, nama: 'Kelompok 4', warna: '#6A1B9A', skor: 10, correctCount: 2, correctTimes: [6.0, 7.2], badges: [] }
                    ];
                    State.sessionCases = Array.from({length: 12}, (_, i) => ({ id: i+1 }));
                    State.unsolvedCases = [];
                    renderResultScreen();
                    showScreen('screen-result');
                })()
            """)
            # Wait for ceremony animations to reveal all columns
            await asyncio.sleep(2.5)

            check_data = await eval_js("""
                (() => {
                    const result = document.getElementById('screen-result');
                    const cols = Array.from(document.querySelectorAll('.podium-col')).map(col => {
                        const r = col.getBoundingClientRect();
                        const teamName = col.querySelector('.podium-team-name');
                        const card = col.querySelector('.podium-card');
                        const cr = card ? card.getBoundingClientRect() : null;
                        const ped = col.querySelector('.podium-pedestal');
                        const pr = ped ? ped.getBoundingClientRect() : null;
                        return {
                            name: teamName ? teamName.textContent.trim() : '',
                            colWidth: Math.round(r.width),
                            colHeight: Math.round(r.height),
                            cardHeight: cr ? Math.round(cr.height) : 0,
                            pedHeight: pr ? Math.round(pr.height) : 0,
                            top: Math.round(r.top),
                            bottom: Math.round(r.bottom)
                        };
                    });
                    const remaining = document.getElementById('result-remaining-container');
                    const remDisplay = remaining ? window.getComputedStyle(remaining).display : 'none';
                    const footer = document.querySelector('.result-actions-footer');
                    const fr = footer ? footer.getBoundingClientRect() : null;

                    return {
                        viewport: { w: window.innerWidth, h: window.innerHeight },
                        podiumCols: cols,
                        remainingDisplay: remDisplay,
                        footerBottom: fr ? Math.round(fr.bottom) : 0,
                        footerHeight: fr ? Math.round(fr.height) : 0
                    };
                })()
            """)
            print("PODIUM SCREEN CHECK:", json.dumps(check_data, indent=2))

            shot = await cmd("Page.captureScreenshot", {"format": "png"})
            with open("screenshot_landscape_podium.png", "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print("Saved screenshot_landscape_podium.png")

    finally:
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(run_podium_test())
