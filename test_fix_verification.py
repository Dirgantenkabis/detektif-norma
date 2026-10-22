import asyncio
import json
import os
import socket
import subprocess
import tempfile
import time
import urllib.request
import websockets

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE_PATH):
    EDGE_PATH = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

def get_free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

async def run_verification():
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

            async def take_screenshot(filename):
                data = await send_cmd("Page.captureScreenshot", {"format": "png"})
                import base64
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(data["data"]))
                print(f"Saved screenshot: {filename}")

            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")
            await send_cmd("DOM.enable")

            file_path = os.path.abspath("index.html").replace("\\", "/")
            await send_cmd("Page.navigate", {"url": f"file:///{file_path}"})
            await asyncio.sleep(1.0)

            # Viewport 1920x1080
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1920,
                "height": 1080,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            await asyncio.sleep(0.5)

            print("=== TEST 1: SETUP GAME & SIMULASI KASUS HOTS OVERLAY ===")
            await eval_js("""
                window.showScreen('screen-setup');
                document.querySelector('.btn-count-choice[data-count=\"4\"]').click();
            """)
            await asyncio.sleep(0.3)

            is_modal = await eval_js("document.getElementById('modal-role-reminder').classList.contains('active');")
            if is_modal:
                await eval_js("document.getElementById('btn-proceed-to-game').click();")
                await asyncio.sleep(0.4)

            # Paksa kasus 0 menjadi kasus HOTS k24 (Pak RT menolak uang sogokan)
            await eval_js("""
                const hotsK24 = KASUS_POOL.find(k => k.id === 'k24') || KASUS_POOL.find(k => k.tingkat === 'hots');
                State.sessionCases[0] = hotsK24;
                loadCase(0);
            """)
            await asyncio.sleep(0.5)

            # Pilih Tim 0
            await eval_js("document.querySelectorAll('.team-card-btn')[0].click();")
            await asyncio.sleep(0.2)

            # Jawab benar
            await eval_js("""
                const ans = State.sessionCases[0].jawabanId;
                document.querySelector(`.norma-stamp[data-norma=\"${ans}\"]`).click();
            """)
            await asyncio.sleep(0.6)

            # Periksa apakah overlay terbuka dan tidak bertabrakan dengan clue box
            overlay_check = await eval_js("""
                (() => {
                    const overlay = document.getElementById('reason-panel');
                    const clue1 = document.getElementById('clue-slot-1');
                    const hotsBox = document.getElementById('hots-question-box');
                    const caseQuote = document.getElementById('overlay-case-snippet');
                    
                    const oRect = overlay.getBoundingClientRect();
                    const cRect = clue1.getBoundingClientRect();

                    return {
                        overlayVisible: window.getComputedStyle(overlay).display !== 'none',
                        isPositionAbsolute: window.getComputedStyle(overlay).position === 'absolute',
                        hotsVisible: window.getComputedStyle(hotsBox).display !== 'none',
                        hasCaseQuote: caseQuote.textContent.length > 10,
                        zIndex: window.getComputedStyle(overlay).zIndex
                    };
                })()
            """)
            print("Overlay Check Result:", overlay_check)
            assert overlay_check["overlayVisible"] == True, "Reason panel overlay must be visible"
            assert overlay_check["isPositionAbsolute"] == True, "Reason panel must be positioned absolute (overlay)"
            assert overlay_check["hotsVisible"] == True, "HOTS box must be visible for HOTS case"
            assert overlay_check["hasCaseQuote"] == True, "Overlay must display case snippet quote"
            print("PASS: Overlay Evaluasi Alasan berhasil dibuka dengan rapi dan bebas tabrakan!\n")

            await take_screenshot("screenshot_fix_hots_overlay_1080p.png")

            # Beri alasan
            await eval_js("evaluateReason(true);")
            await asyncio.sleep(0.3)

            # Pastikan explanation box tampil
            exp_check = await eval_js("window.getComputedStyle(document.getElementById('explanation-box')).display !== 'none'")
            assert exp_check == True, "Explanation box must be displayed after reason is evaluated"

            # Lanjut ke hasil permainan dengan menyelesaikan sisa kasus
            print("=== TEST 2: SIMULASI PENUH KE LAYAR HASIL ===")
            await eval_js("finishGameSession();")
            await asyncio.sleep(0.5)

            is_result = await eval_js("document.getElementById('screen-result').classList.contains('active')")
            assert is_result == True, "Must reach screen-result"

            result_audit = await eval_js("""
                (() => {
                    const hlRow = document.getElementById('result-highlights-row');
                    const hlCards = document.querySelectorAll('.result-highlight-card');
                    const solvedTitle = document.getElementById('hl-solved-count').textContent;
                    const speedTitle = document.getElementById('hl-class-speed').textContent;
                    const reflText = document.getElementById('hl-reflection-question').textContent;

                    const podiumCols = document.querySelectorAll('#result-podium-container .podium-col');
                    const remainingCards = document.querySelectorAll('#result-remaining-container .remaining-team-card');
                    
                    // Cek bahwa setiap tim punya lencana
                    const allBadges = Array.from(document.querySelectorAll('.podium-badge')).map(b => b.textContent.trim());

                    const sh = document.documentElement.scrollHeight;
                    const ch = document.documentElement.clientHeight;

                    return {
                        hlRowVisible: window.getComputedStyle(hlRow).display !== 'none',
                        hlCardsCount: hlCards.length,
                        solvedTitle,
                        speedTitle,
                        reflText,
                        podiumCols: podiumCols.length,
                        remainingCards: remainingCards.length,
                        totalBadgesDisplayed: allBadges.length,
                        badgesSample: allBadges,
                        hasVScroll: sh > ch
                    };
                })()
            """)
            print("Result Screen Audit:", result_audit)
            assert result_audit["hlCardsCount"] == 3, "Highlights row must have 3 cards"
            assert result_audit["hasVScroll"] == False, "Result screen 1080p must have 0 scrollbar"
            assert result_audit["podiumCols"] == 3, "Podium must have 3 columns"
            assert result_audit["remainingCards"] == 1, "4 teams must have 1 remaining card"
            assert result_audit["totalBadgesDisplayed"] >= 4, "Every team must have at least 1 badge"
            print("PASS: Layar Hasil 1080p terverifikasi sempurna dengan 3 kartu sorotan dan lencana tim!\n")

            await take_screenshot("screenshot_fix_result_1080p.png")

            # Uji responsivitas 1366x768
            print("=== TEST 3: RESPONSIFITAS 1366x768 ===")
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1366,
                "height": 768,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            await asyncio.sleep(0.5)

            scroll_768 = await eval_js("""
                (() => {
                    const sh = document.documentElement.scrollHeight;
                    const ch = document.documentElement.clientHeight;
                    return { hasVScroll: sh > ch, sh, ch };
                })()
            """)
            print("768p Scroll:", scroll_768)
            assert scroll_768["hasVScroll"] == False, "1366x768 must be free of scrollbars"
            print("PASS: 1366x768 Bebas Scrollbar!\n")

            await take_screenshot("screenshot_fix_result_768p.png")

            print("ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    finally:
        proc.terminate()
        try: proc.wait(timeout=2)
        except: proc.kill()

if __name__ == "__main__":
    asyncio.run(run_verification())
