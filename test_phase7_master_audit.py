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

async def run_master_audit():
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

            # Viewport 1920x1080
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1920,
                "height": 1080,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            await asyncio.sleep(0.5)

            print("=== TEST 1: AUDIT TOMBOL NORMAL STATE ===")
            button_audit = await eval_js("""
                (() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const failedButtons = [];
                    buttons.forEach(btn => {
                        if (btn.offsetWidth > 0 && btn.offsetHeight > 0) {
                            const style = window.getComputedStyle(btn);
                            const bg = style.backgroundColor;
                            const isTransparent = bg === 'transparent' || bg === 'rgba(0, 0, 0, 0)';
                            if (isTransparent) {
                                failedButtons.push({ id: btn.id || btn.className, bg });
                            }
                        }
                    });
                    return { failedCount: failedButtons.length };
                })()
            """)
            assert button_audit["failedCount"] == 0, "All normal buttons must have solid background"
            print("PASS: Semua tombol memiliki warna dasar solid pada kondisi normal!\n")

            print("=== TEST 2: SIMULASI 12 KASUS PENUH (4 KELOMPOK) ===")
            # Mulai permainan baru 4 kelompok
            await eval_js("""
                window.showScreen('screen-setup');
                document.querySelector('.btn-count-choice[data-count=\"4\"]').click();
            """)
            await asyncio.sleep(0.3)

            # Tutup modal role reminder
            is_modal = await eval_js("document.getElementById('modal-role-reminder').classList.contains('active');")
            if is_modal:
                await eval_js("document.getElementById('btn-proceed-to-game').click();")
                await asyncio.sleep(0.4)

            # Selesaikan 12 kasus berturut-turut
            for c_idx in range(12):
                # Pilih tim yang dapat giliran: gunakan giliran tim bergantian (c_idx % 4)
                team_idx = c_idx % 4
                await eval_js(f"document.querySelectorAll('.team-card-btn')[{team_idx}].click();")
                await asyncio.sleep(0.15)

                if c_idx == 0:
                    # Uji salah tebak untuk menguji penguncian tim & norma
                    current_ans = await eval_js("State.sessionCases[State.currentCaseIndex].jawabanId")
                    wrong_ans = "hukum" if current_ans != "hukum" else "agama"
                    await eval_js(f"document.querySelector('.norma-stamp[data-norma=\"{wrong_ans}\"]').click();")
                    await asyncio.sleep(0.35)

                    is_team_locked = await eval_js(f"State.lockedGroupsForCase.has({team_idx})")
                    is_norma_locked = await eval_js(f"State.lockedNormasForCase.has('{wrong_ans}')")
                    assert is_team_locked == True, "Team must be locked after wrong guess"
                    assert is_norma_locked == True, "Norma stamp must be locked after wrong guess"

                    # Alihkan ke tim lain (tim 1)
                    await eval_js("document.querySelectorAll('.team-card-btn')[1].click();")
                    await asyncio.sleep(0.15)

                # Tebak jawaban benar
                correct_ans = await eval_js("State.sessionCases[State.currentCaseIndex].jawabanId")
                await eval_js(f"document.querySelector('.norma-stamp[data-norma=\"{correct_ans}\"]').click();")
                await asyncio.sleep(0.35)

                # Beri alasan
                await eval_js("evaluateReason(true);")
                await asyncio.sleep(0.2)

                # Lanjut ke kasus berikutnya
                await eval_js("document.getElementById('btn-next-case').click();")
                await asyncio.sleep(0.35)

            # Setelah 12 kasus selesai, pastikan transisi ke screen-result
            await asyncio.sleep(0.5)
            is_result = await eval_js("document.getElementById('screen-result').classList.contains('active')")
            print(f"Reached screen-result: {is_result}")
            assert is_result == True, "Must reach screen-result after 12 cases"
            print("PASS: 12 Kasus selesai mulus dan mendarat di Layar Hasil Podium!\n")

            print("=== TEST 3: VERIFIKASI PODIUM HASIL & BEBAS OVERFLOW ===")
            res_summary = await eval_js("""
                (() => {
                    const podiumCols = document.querySelectorAll('#result-podium-container .podium-col');
                    const remainingCards = document.querySelectorAll('#result-remaining-container .remaining-team-card');
                    const sh = document.documentElement.scrollHeight;
                    const ch = document.documentElement.clientHeight;
                    return {
                        podiumCols: podiumCols.length,
                        remainingCards: remainingCards.length,
                        hasVScroll: sh > ch
                    };
                })()
            """)
            print("Result Summary:", res_summary)
            assert res_summary["podiumCols"] == 3, "Podium must show 3 columns"
            assert res_summary["remainingCards"] == 1, "4 teams must have 1 remaining card below"
            assert res_summary["hasVScroll"] == False, "Result screen must have 0 scrollbar"
            print("PASS: Layar Hasil Podium terverifikasi sempurna!\n")

            print("=== TEST 4: AUDIT BEBAS SCROLLBAR 1366x768 ===")
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
            assert scroll_768["hasVScroll"] == False, "768p must be free of scrollbar"
            print("PASS: 1366x768 Bebas Scrollbar!\n")

            print("ALL AUDIT TESTS COMPLETED SUCCESSFULLY!")
    finally:
        proc.terminate()
        try: proc.wait(timeout=2)
        except: proc.kill()

if __name__ == "__main__":
    asyncio.run(run_master_audit())
