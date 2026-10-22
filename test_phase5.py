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

            print("--- TEST 1: Verifikasi Layout Layar Setup & Strip Nama ---")
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1920,
                "height": 1080,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            await asyncio.sleep(0.5)

            # Navigasi ke screen-setup
            await eval_js("window.showScreen('screen-setup');")
            await asyncio.sleep(0.3)

            setup_info = await eval_js("""
                (() => {
                    const topHeader = document.querySelector('#screen-setup .screen-header-simple');
                    const editInTopHeader = topHeader ? topHeader.querySelector('#btn-edit-group-names') : null;
                    const backInTopHeader = topHeader ? topHeader.querySelector('#btn-back-to-start') : null;

                    const strip = document.querySelector('.setup-names-strip');
                    const stripText = document.querySelector('#setup-names-list-text');
                    const btnEditInside = strip ? strip.querySelector('#btn-edit-group-names') : null;

                    const bottomBar = document.querySelector('.setup-bottom-bar');
                    const btnBackInBottom = bottomBar ? bottomBar.querySelector('#btn-back-to-start') : null;

                    const countChoices = document.querySelectorAll('.btn-count-choice');

                    return {
                        hasEditInTopHeader: !!editInTopHeader,
                        hasBackInTopHeader: !!backInTopHeader,
                        hasStrip: !!strip,
                        stripTextContent: stripText ? stripText.textContent.trim() : '',
                        hasBtnEditInside: !!btnEditInside,
                        hasBtnBackInBottom: !!btnBackInBottom,
                        countBtnHeights: Array.from(countChoices).map(b => b.offsetHeight)
                    };
                })()
            """)
            print("Setup Info:", json.dumps(setup_info, indent=2))
            assert setup_info["hasEditInTopHeader"] == False, "Ubah Nama must be removed from top header"
            assert setup_info["hasBackInTopHeader"] == False, "Menu Awal must be moved from top header"
            assert setup_info["hasStrip"] == True, "Names strip must exist inside prompt card"
            assert "Tim Elang" in setup_info["stripTextContent"], "Default names must appear in strip"
            assert setup_info["hasBtnEditInside"] == True, "Ubah button must exist inside names strip"
            assert setup_info["hasBtnBackInBottom"] == True, "Menu Awal button must be in bottom bar"
            assert all(h >= 100 for h in setup_info["countBtnHeights"]), "Count buttons must be enlarged >= 100px"
            print("PASS: Layout Layar Setup OK!")

            print("\n--- TEST 2: Ubah Nama & Sinkronisasi Instan ---")
            # Buka modal edit names
            await eval_js("document.getElementById('btn-edit-group-names').click();")
            await asyncio.sleep(0.3)

            modal_open = await eval_js("document.getElementById('modal-edit-names').classList.contains('active');")
            assert modal_open == True, "modal-edit-names should open"

            # Ubah nama kelompok 1 jadi 'Garuda Sakti' dan simpan
            await eval_js("""
                const input0 = document.getElementById('custom-name-0');
                if (input0) input0.value = 'Garuda Sakti';
                document.getElementById('btn-save-custom-names').click();
            """)
            await asyncio.sleep(0.3)

            strip_updated = await eval_js("document.getElementById('setup-names-list-text').textContent;")
            print("Updated Strip Text:", strip_updated)
            assert "Garuda Sakti" in strip_updated, "Strip text should immediately reflect the edited name"
            print("PASS: Ubah Nama & Sinkronisasi OK!")

            print("\n--- TEST 3: Modal Pengingat Peran (Satu Tombol, Tanpa X, Compact Roles) ---")
            # Klik tombol '3' kelompok
            await eval_js("document.querySelector('.btn-count-choice[data-count=\"3\"]').click();")
            await asyncio.sleep(0.4)

            role_modal_info = await eval_js("""
                (() => {
                    const modal = document.getElementById('modal-role-reminder');
                    const isActive = modal.classList.contains('active');
                    const closeBtn = modal.querySelector('.btn-close-modal');
                    const proceedBtn = modal.querySelector('#btn-proceed-to-game');
                    const goldenBanner = modal.querySelector('.golden-rule-banner');
                    const compactItems = modal.querySelectorAll('.role-compact-item');

                    return {
                        isActive,
                        hasCloseBtn: !!closeBtn,
                        proceedBtnText: proceedBtn ? proceedBtn.textContent.trim() : '',
                        hasGoldenBanner: !!goldenBanner,
                        goldenBannerText: goldenBanner ? goldenBanner.textContent.trim() : '',
                        compactItemsCount: compactItems.length
                    };
                })()
            """)
            print("Role Modal Info:", json.dumps(role_modal_info, indent=2))
            assert role_modal_info["isActive"] == True, "Role reminder modal should be active on first play"
            assert role_modal_info["hasCloseBtn"] == False, "Close 'X' button must be removed"
            assert role_modal_info["proceedBtnText"] == "Siap Menyelidiki Kasus", "Button text must be 'Siap Menyelidiki Kasus' without rocket"
            assert "Tidak boleh mengejek" in role_modal_info["goldenBannerText"], "Golden rule must remain highlighted"
            assert role_modal_info["compactItemsCount"] == 4, "4 compact role items should exist"
            print("PASS: Modal Pengingat Peran Struktur OK!")

            print("\n--- TEST 4: Modal Hanya Muncul 1 Kali Per Sesi Halaman ---")
            # Klik 'Siap Menyelidiki Kasus'
            await eval_js("document.getElementById('btn-proceed-to-game').click();")
            await asyncio.sleep(0.5)

            on_board = await eval_js("document.getElementById('screen-board').classList.contains('active');")
            assert on_board == True, "Should transition to board screen"

            # Sekarang kembali ke setup dan pilih kelompok lagi
            await eval_js("""
                window.showScreen('screen-setup');
                document.querySelector('.btn-count-choice[data-count=\"4\"]').click();
            """)
            await asyncio.sleep(0.5)

            second_play_info = await eval_js("""
                (() => {
                    const modal = document.getElementById('modal-role-reminder');
                    const isModalActive = modal.classList.contains('active');
                    const isBoardActive = document.getElementById('screen-board').classList.contains('active');
                    return { isModalActive, isBoardActive, hasShownRoleReminder: window.State.hasShownRoleReminder };
                })()
            """)
            print("Second Play Info:", json.dumps(second_play_info, indent=2))
            assert second_play_info["isModalActive"] == False, "Modal must NOT appear on subsequent sessions"
            assert second_play_info["isBoardActive"] == True, "Should go directly to screen-board on second session"
            assert second_play_info["hasShownRoleReminder"] == True, "hasShownRoleReminder should remain true in memory"
            print("PASS: Modal Hanya Muncul 1 Kali OK!")

            print("\nALL FASE 5 TESTS PASSED!")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    asyncio.run(run_test())
