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

            print("--- TEST 1: Verifikasi Layar Awal 1920x1080 ---")
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1920,
                "height": 1080,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            await asyncio.sleep(0.5)

            # Simpan 5 grup di localStorage untuk menguji tombol resume
            await eval_js("""
                localStorage.setItem('detektif_norma_last_groups', JSON.stringify({
                    count: 5,
                    groups: [
                        { id: 'tim1', nama: 'Tim Elang', warna: '#E74C3C' },
                        { id: 'tim2', nama: 'Tim Harimau', warna: '#F39C12' },
                        { id: 'tim3', nama: 'Tim Kancil', warna: '#27AE60' },
                        { id: 'tim4', nama: 'Tim Banteng', warna: '#2980B9' },
                        { id: 'tim5', nama: 'Tim Rusa', warna: '#8E44AD' }
                    ]
                }));
                // Jalankan pengecekan resume
                window.location.reload();
            """)
            await asyncio.sleep(1.0)

            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1920,
                "height": 1080,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            await asyncio.sleep(0.5)

            hero_info = await eval_js("""
                (() => {
                    const titleEl = document.querySelector('.game-main-title');
                    const badgeEl = document.querySelector('.badge-sd');
                    const svgIllustration = document.querySelector('.hero-detective-svg');
                    const btnPlay = document.getElementById('btn-start-game');
                    const btnResume = document.getElementById('btn-resume-previous');
                    const resumeTitle = document.getElementById('label-resume-title');
                    const resumeSub = document.getElementById('label-resume-sub');
                    const titleComputed = window.getComputedStyle(titleEl);

                    const scrollHeight = document.documentElement.scrollHeight;
                    const clientHeight = document.documentElement.clientHeight;
                    const scrollWidth = document.documentElement.scrollWidth;
                    const clientWidth = document.documentElement.clientWidth;

                    return {
                        titleText: titleEl ? titleEl.textContent.trim() : '',
                        titleFontSizePx: parseFloat(titleComputed.fontSize),
                        badgeText: badgeEl ? badgeEl.textContent.trim() : '',
                        hasSvgIllustration: !!svgIllustration,
                        btnPlayHeight: btnPlay ? btnPlay.offsetHeight : 0,
                        btnResumeVisible: btnResume && window.getComputedStyle(btnResume).display !== 'none',
                        resumeTitleText: resumeTitle ? resumeTitle.textContent.trim() : '',
                        resumeSubText: resumeSub ? resumeSub.textContent.trim() : '',
                        hasVScroll: scrollHeight > clientHeight,
                        hasHScroll: scrollWidth > clientWidth
                    };
                })()
            """)
            print("Hero Info 1080p:", json.dumps(hero_info, indent=2))
            assert hero_info["titleText"] == "DETEKTIF NORMA", "Title should be DETEKTIF NORMA"
            assert hero_info["titleFontSizePx"] >= 70, f"Title font size should be enlarged (~1.5x, >= 70px at 1080p), got {hero_info['titleFontSizePx']}px"
            assert hero_info["badgeText"] == "PPKn KELAS 5 SD", f"Badge text should be strictly 'PPKn KELAS 5 SD', got '{hero_info['badgeText']}'"
            assert hero_info["hasSvgIllustration"] == True, "SVG detective illustration must exist"
            assert hero_info["btnPlayHeight"] >= 64, "Play button must be prominent height >= 64px"
            assert hero_info["btnResumeVisible"] == True, "Resume button must be visible when previous groups exist"
            assert hero_info["resumeTitleText"] == "Lanjutkan dengan 5 kelompok", f"Resume title must be concise, got '{hero_info['resumeTitleText']}'"
            assert "Tim Elang" in hero_info["resumeSubText"], "Resume sub must show team names"
            assert hero_info["hasVScroll"] == False, "1080p must not have vertical scrollbar"
            assert hero_info["hasHScroll"] == False, "1080p must not have horizontal scrollbar"
            print("PASS: Layar Awal 1080p OK!")

            print("\n--- TEST 2: Responsivitas Layar Awal 1366x768 ---")
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1366,
                "height": 768,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            await asyncio.sleep(0.5)

            hero_768 = await eval_js("""
                (() => {
                    const scrollHeight = document.documentElement.scrollHeight;
                    const clientHeight = document.documentElement.clientHeight;
                    const scrollWidth = document.documentElement.scrollWidth;
                    const clientWidth = document.documentElement.clientWidth;
                    const titleEl = document.querySelector('.game-main-title');
                    const titleFontSize = window.getComputedStyle(titleEl).fontSize;

                    return {
                        hasVScroll: scrollHeight > clientHeight,
                        hasHScroll: scrollWidth > clientWidth,
                        titleFontSize,
                        scrollHeight,
                        clientHeight
                    };
                })()
            """)
            print("Hero Info 768p:", hero_768)
            assert hero_768["hasVScroll"] == False, "768p must not have vertical scrollbar"
            assert hero_768["hasHScroll"] == False, "768p must not have horizontal scrollbar"
            print("PASS: Layar Awal 1366x768 OK!")

            print("\n--- TEST 3: Toolbar Kecil (Semua Ikon & Status) ---")
            toolbar_info = await eval_js("""
                (() => {
                    const soundBtn = document.getElementById('btn-sound-toggle');
                    const fsBtn = document.getElementById('btn-fullscreen-toggle');
                    const rulesBtn = document.getElementById('btn-how-to-play');
                    const leadBtn = document.getElementById('btn-view-leaderboard');
                    const aboutBtn = document.getElementById('btn-about');

                    return {
                        hasSound: !!soundBtn,
                        hasFs: !!fsBtn,
                        hasRules: !!rulesBtn,
                        hasLead: !!leadBtn,
                        hasAbout: !!aboutBtn,
                        soundHasIcon: !!soundBtn.querySelector('svg'),
                        rulesHasIcon: !!rulesBtn.querySelector('svg'),
                        leadHasIcon: !!leadBtn.querySelector('svg'),
                        aboutHasIcon: !!aboutBtn.querySelector('svg')
                    };
                })()
            """)
            print("Toolbar Info:", json.dumps(toolbar_info, indent=2))
            assert toolbar_info["hasSound"] and toolbar_info["hasFs"] and toolbar_info["hasRules"] and toolbar_info["hasLead"] and toolbar_info["hasAbout"], "All 5 toolbar buttons must exist"
            assert toolbar_info["soundHasIcon"] and toolbar_info["rulesHasIcon"] and toolbar_info["leadHasIcon"] and toolbar_info["aboutHasIcon"], "All toolbar buttons must use SVG icons"
            print("PASS: Toolbar Kecil OK!")

            print("\nALL FASE 6 TESTS PASSED!")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    asyncio.run(run_test())
