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
        "--autoplay-policy=no-user-gesture-required"
    ])
    print(f"Launched Edge on port {port}, waiting 2s...", flush=True)
    time.sleep(2)

    try:
        import urllib.request
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json") as resp:
            data = json.loads(resp.read().decode())
            ws_url = data[0]['webSocketDebuggerUrl']

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

            # Strict 1920x1080 Viewport
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
            await asyncio.sleep(0.5)
            await send("Runtime.evaluate", {"expression": "document.querySelector('.btn-count-choice[data-count=\"3\"]').click()"})
            await asyncio.sleep(0.5)
            await send("Runtime.evaluate", {"expression": "document.getElementById('btn-proceed-to-game').click()"})
            await asyncio.sleep(1.0)

            # Check case board initial layout in 1920x1080
            res = await send("Runtime.evaluate", {"expression": """
                (() => {
                    const caseText = document.getElementById('folder-case-text');
                    const clue1 = document.querySelector('#clue-slot-1 .clue-text');
                    const guideText = document.querySelector('.stamps-guide-text');
                    const timerBadge = document.querySelector('.timer-badge');
                    const stampZone = document.querySelector('.case-stamp-zone');
                    
                    const caseRect = caseText ? caseText.getBoundingClientRect() : { bottom: 0 };
                    const stampZoneRect = stampZone ? stampZone.getBoundingClientRect() : { top: 0 };
                    
                    return {
                        winW: window.innerWidth,
                        winH: window.innerHeight,
                        caseFontSize: caseText ? window.getComputedStyle(caseText).fontSize : '',
                        clueFontSize: clue1 ? window.getComputedStyle(clue1).fontSize : '',
                        guideFontSize: guideText ? window.getComputedStyle(guideText).fontSize : '',
                        timerFontSize: timerBadge ? window.getComputedStyle(timerBadge).fontSize : '',
                        caseBottom: Math.round(caseRect.bottom),
                        stampZoneTop: Math.round(stampZoneRect.top)
                    };
                })()
            """, "returnByValue": True})
            print("1080p LAYOUT STATS:", json.dumps(res, indent=2), flush=True)

            # Select group 0
            await send("Runtime.evaluate", {"expression": "document.querySelector('.team-card-btn').click()"})
            await asyncio.sleep(0.5)

            # Answer with the correct norma
            ans_res = await send("Runtime.evaluate", {"expression": """
                (() => {
                    const st = window.__DETEKTIF_STATE__;
                    const currentCase = st.sessionCases[st.currentCaseIndex];
                    const btn = document.querySelector(`.norma-stamp[data-norma="${currentCase.jawabanId}"]`);
                    if (btn) btn.click();
                    return { jawabanId: currentCase.jawabanId };
                })()
            """, "returnByValue": True})
            print("ANSWERED WITH:", ans_res, flush=True)

            # Wait for stamp animation and sound
            await asyncio.sleep(0.8)

            # Check solved stamp state and overlap at 1080p
            stamp_res = await send("Runtime.evaluate", {"expression": """
                (() => {
                    const stamp = document.getElementById('stamp-terpecahkan');
                    const caseText = document.getElementById('folder-case-text');
                    const clues = document.querySelector('.clues-container');
                    const reasonPanel = document.getElementById('reason-panel');
                    const feedbackBar = document.getElementById('case-feedback-bar');
                    
                    if (!stamp) return { error: 'No stamp element' };
                    
                    const sRect = stamp.getBoundingClientRect();
                    const cRect = caseText ? caseText.getBoundingClientRect() : { left:0, right:0, top:0, bottom:0, width:0, height:0 };
                    const clRect = clues ? clues.getBoundingClientRect() : { left:0, right:0, top:0, bottom:0, width:0, height:0 };
                    const rRect = reasonPanel ? reasonPanel.getBoundingClientRect() : { left:0, right:0, top:0, bottom:0, width:0, height:0 };
                    const fRect = feedbackBar ? feedbackBar.getBoundingClientRect() : { left:0, right:0, top:0, bottom:0, width:0, height:0 };
                    
                    function overlaps(r1, r2) {
                        if (!r2 || r2.width === 0 || r2.height === 0) return false;
                        return !(r1.right < r2.left || r1.left > r2.right || r1.bottom < r2.top || r1.top > r2.bottom);
                    }
                    
                    return {
                        hasShowClass: stamp.classList.contains('show'),
                        opacity: window.getComputedStyle(stamp).opacity,
                        visibility: window.getComputedStyle(stamp).visibility,
                        mixBlendMode: window.getComputedStyle(stamp).mixBlendMode,
                        stampRect: { x: Math.round(sRect.x), y: Math.round(sRect.y), w: Math.round(sRect.width), h: Math.round(sRect.height) },
                        feedbackRect: { x: Math.round(fRect.x), y: Math.round(fRect.y), w: Math.round(fRect.width), h: Math.round(fRect.height) },
                        reasonRect: { x: Math.round(rRect.x), y: Math.round(rRect.y), w: Math.round(rRect.width), h: Math.round(rRect.height) },
                        overlapsCaseText: overlaps(sRect, cRect),
                        overlapsClues: overlaps(sRect, clRect),
                        overlapsReasonPanel: overlaps(sRect, rRect),
                        overlapsFeedback: overlaps(sRect, fRect)
                    };
                })()
            """, "returnByValue": True})
            print("SOLVED STAMP CHECK (1080p):", json.dumps(stamp_res, indent=2), flush=True)

            # Screenshot at 1080p
            ss = await send("Page.captureScreenshot")
            import base64
            with open("screenshot_phase2_1080p.png", "wb") as f:
                f.write(base64.b64decode(ss["data"]))
            print("Saved screenshot_phase2_1080p.png", flush=True)

            # Switch to 1366x768
            await send("Emulation.setDeviceMetricsOverride", {
                "width": 1366,
                "height": 768,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            await asyncio.sleep(0.5)

            # Check overlap at 1366x768
            stamp_768 = await send("Runtime.evaluate", {"expression": """
                (() => {
                    const stamp = document.getElementById('stamp-terpecahkan');
                    const caseText = document.getElementById('folder-case-text');
                    const clues = document.querySelector('.clues-container');
                    const reasonPanel = document.getElementById('reason-panel');
                    const feedbackBar = document.getElementById('case-feedback-bar');
                    
                    const sRect = stamp.getBoundingClientRect();
                    const cRect = caseText ? caseText.getBoundingClientRect() : null;
                    const clRect = clues ? clues.getBoundingClientRect() : null;
                    const rRect = reasonPanel ? reasonPanel.getBoundingClientRect() : null;
                    const fRect = feedbackBar ? feedbackBar.getBoundingClientRect() : null;
                    
                    function overlaps(r1, r2) {
                        if (!r2 || r2.width === 0 || r2.height === 0) return false;
                        return !(r1.right < r2.left || r1.left > r2.right || r1.bottom < r2.top || r1.top > r2.bottom);
                    }
                    
                    return {
                        winW: window.innerWidth,
                        winH: window.innerHeight,
                        stampRect: { x: Math.round(sRect.x), y: Math.round(sRect.y), w: Math.round(sRect.width), h: Math.round(sRect.height) },
                        overlapsCaseText: overlaps(sRect, cRect),
                        overlapsClues: overlaps(sRect, clRect),
                        overlapsReasonPanel: overlaps(sRect, rRect),
                        overlapsFeedback: overlaps(sRect, fRect)
                    };
                })()
            """, "returnByValue": True})
            print("768p OVERLAP CHECK:", json.dumps(stamp_768, indent=2), flush=True)

            ss768 = await send("Page.captureScreenshot")
            with open("screenshot_phase2_768p.png", "wb") as f:
                f.write(base64.b64decode(ss768["data"]))
            print("Saved screenshot_phase2_768p.png", flush=True)

            # Check next case reset
            await send("Runtime.evaluate", {"expression": "document.getElementById('btn-next-case').click()"})
            await asyncio.sleep(0.5)

            next_res = await send("Runtime.evaluate", {"expression": """
                (() => {
                    const stamp = document.getElementById('stamp-terpecahkan');
                    const st = window.__DETEKTIF_STATE__;
                    return {
                        hasShowClass: stamp ? stamp.classList.contains('show') : false,
                        isReset: stamp ? !stamp.classList.contains('show') : true,
                        currentCaseIndex: st.currentCaseIndex
                    };
                })()
            """, "returnByValue": True})
            print("NEXT CASE RESET CHECK:", json.dumps(next_res, indent=2), flush=True)

    finally:
        proc.terminate()
        try:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass

asyncio.run(run_test())
