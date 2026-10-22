import asyncio
import json
import os
import socket
import subprocess
import tempfile
import time
import websockets

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

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
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        "--autoplay-policy=no-user-gesture-required"
    ])
    print(f"Launched Edge on port {port}, waiting 2s...", flush=True)
    time.sleep(2)

    try:
        import urllib.request
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json") as resp:
            data = json.loads(resp.read().decode())
            page_target = next(item for item in data if item.get('type') == 'page')
            ws_url = page_target['webSocketDebuggerUrl']

        async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
            msg_id = 1
            async def send(method, params=None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
                while True:
                    res = json.loads(await ws.recv())
                    if res.get("id") == cid:
                        r = res.get("result", {})
                        if "result" in r and "value" in r["result"]:
                            return r["result"]["value"]
                        return r

            await send("Page.enable")
            await send("Runtime.enable")
            await send("DOM.enable")

            # 1920x1080 Viewport
            await send("Emulation.setDeviceMetricsOverride", {
                "width": 1920,
                "height": 1080,
                "deviceScaleFactor": 1,
                "mobile": False
            })

            file_path = os.path.abspath("index.html").replace("\\", "/")
            await send("Page.navigate", {"url": f"file:///{file_path}"})
            await asyncio.sleep(1.2)

            # Start game with 3 groups
            await send("Runtime.evaluate", {"expression": "document.getElementById('btn-start-game').click()"})
            await asyncio.sleep(0.4)
            await send("Runtime.evaluate", {"expression": "document.querySelector('.btn-count-choice[data-count=\"3\"]').click()"})
            await asyncio.sleep(0.4)
            await send("Runtime.evaluate", {"expression": "document.getElementById('btn-proceed-to-game').click()"})
            await asyncio.sleep(0.8)

            # 1. TEST KONDISI (A): MENUNGGU GILIRAN
            state_a = await send("Runtime.evaluate", {"expression": """
                (() => {
                    const stamps = document.querySelectorAll('.norma-stamp');
                    const results = [];
                    stamps.forEach(s => {
                        const r = s.getBoundingClientRect();
                        const cs = window.getComputedStyle(s);
                        const handle = s.querySelector('.stamp-wood-handle');
                        const pad = s.querySelector('.stamp-pad-body');
                        results.push({
                            norma: s.dataset.norma,
                            height: Math.round(r.height),
                            isOver80: r.height >= 80,
                            disabled: s.disabled,
                            hasDisabledClass: s.classList.contains('disabled'),
                            hasActiveClass: s.classList.contains('active'),
                            hasLockedClass: s.classList.contains('locked'),
                            opacity: cs.opacity,
                            hasHandle: !!handle,
                            hasPad: !!pad
                        });
                    });
                    return {
                        href: location.href,
                        stampCount: stamps.length,
                        results: results
                    };
                })()
            """, "returnByValue": True})
            print("KONDISI (A) WAITING CHECK:", json.dumps(state_a, indent=2), flush=True)

            # Screenshot waiting state
            ss_wait = await send("Page.captureScreenshot")
            import base64
            with open("screenshot_phase3_waiting.png", "wb") as f:
                f.write(base64.b64decode(ss_wait["data"]))

            # 2. TEST KONDISI (B): AKTIF SETELAH GURU MEMILIH KELOMPOK
            await send("Runtime.evaluate", {"expression": "document.querySelector('.team-card-btn').click()"})
            await asyncio.sleep(0.4)

            state_b = await send("Runtime.evaluate", {"expression": """
                (() => {
                    const stamps = document.querySelectorAll('.norma-stamp');
                    const results = [];
                    stamps.forEach(s => {
                        const cs = window.getComputedStyle(s);
                        results.push({
                            norma: s.dataset.norma,
                            disabled: s.disabled,
                            hasActiveClass: s.classList.contains('active'),
                            borderColor: cs.borderColor,
                            cursor: cs.cursor,
                            animationName: cs.animationName
                        });
                    });
                    return results;
                })()
            """, "returnByValue": True})
            print("KONDISI (B) ACTIVE CHECK:", json.dumps(state_b, indent=2), flush=True)

            # Screenshot active state
            ss_active = await send("Page.captureScreenshot")
            with open("screenshot_phase3_active.png", "wb") as f:
                f.write(base64.b64decode(ss_active["data"]))

            # 3. TEST KONDISI (C): TERKUNCI SETELAH SALAH
            # Intentionally pick wrong norma
            wrong_res = await send("Runtime.evaluate", {"expression": """
                (() => {
                    const st = window.__DETEKTIF_STATE__;
                    const c = st.sessionCases[st.currentCaseIndex];
                    const allNormas = ['agama', 'kesusilaan', 'kesopanan', 'hukum'];
                    const wrongNorma = allNormas.find(n => n !== c.jawabanId);
                    const btn = document.querySelector(`.norma-stamp[data-norma="${wrongNorma}"]`);
                    btn.click();
                    return { chosenWrong: wrongNorma, correctIs: c.jawabanId };
                })()
            """, "returnByValue": True})
            print("CHOSE WRONG NORMA:", wrong_res, flush=True)
            await asyncio.sleep(0.6)

            # Now select second group so stamps are enabled, but the wrong norma should stay locked!
            await send("Runtime.evaluate", {"expression": """
                (() => {
                    const cards = document.querySelectorAll('.team-card-btn');
                    if (cards[1]) cards[1].click();
                })()
            """})
            await asyncio.sleep(0.4)

            state_c = await send("Runtime.evaluate", {"expression": """
                (() => {
                    const stamps = document.querySelectorAll('.norma-stamp');
                    const results = [];
                    stamps.forEach(s => {
                        const cs = window.getComputedStyle(s);
                        const lockIcon = s.querySelector('.stamp-lock-icon');
                        const lockDisplay = lockIcon ? window.getComputedStyle(lockIcon).display : 'none';
                        results.push({
                            norma: s.dataset.norma,
                            disabled: s.disabled,
                            hasActiveClass: s.classList.contains('active'),
                            hasLockedClass: s.classList.contains('locked'),
                            lockIconVisible: lockDisplay !== 'none',
                            opacity: cs.opacity,
                            filter: cs.filter
                        });
                    });
                    return results;
                })()
            """, "returnByValue": True})
            print("KONDISI (C) LOCKED CHECK (Team 2 active, wrong norma locked):", json.dumps(state_c, indent=2), flush=True)

            # Screenshot locked state
            ss_locked = await send("Page.captureScreenshot")
            with open("screenshot_phase3_locked.png", "wb") as f:
                f.write(base64.b64decode(ss_locked["data"]))

            # 4. Check in 1366x768 resolution
            await send("Emulation.setDeviceMetricsOverride", {
                "width": 1366,
                "height": 768,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            await asyncio.sleep(0.4)

            height_768 = await send("Runtime.evaluate", {"expression": """
                (() => {
                    const stamps = document.querySelectorAll('.norma-stamp');
                    return Array.from(stamps).map(s => {
                        const r = s.getBoundingClientRect();
                        return { norma: s.dataset.norma, h: Math.round(r.height), isOver80: r.height >= 80 };
                    });
                })()
            """, "returnByValue": True})
            print("768p HEIGHT CHECK (All >= 80px):", json.dumps(height_768, indent=2), flush=True)

    finally:
        proc.terminate()
        try:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass

asyncio.run(run_test())
