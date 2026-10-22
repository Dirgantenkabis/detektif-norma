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

            # Navigasi ke index.html
            file_path = os.path.abspath("index.html").replace("\\", "/")
            await send_cmd("Page.navigate", {"url": f"file:///{file_path}"})
            await asyncio.sleep(1.0)

            print("--- TEST 1: 5 Kelompok di 1920x1080 ---")
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1920,
                "height": 1080,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            await asyncio.sleep(0.5)

            await eval_js("""
                window.State.groups = [
                    { id: 'g1', nama: 'Tim Elang', warna: '#E74C3C', skor: 24, correctCount: 4, correctTimes: [12.2, 14.5, 11.0, 15.5] },
                    { id: 'g2', nama: 'Tim Harimau', warna: '#F39C12', skor: 24, correctCount: 3, correctTimes: [8.5, 9.2, 8.8] },
                    { id: 'g3', nama: 'Tim Kancil', warna: '#27AE60', skor: 18, correctCount: 3, correctTimes: [16.0, 15.0, 14.0] },
                    { id: 'g4', nama: 'Tim Banteng', warna: '#2980B9', skor: 12, correctCount: 2, correctTimes: [5.0, 6.0] },
                    { id: 'g5', nama: 'Tim Rusa', warna: '#8E44AD', skor: 6, correctCount: 0, correctTimes: [] }
                ];
                window.State.unsolvedCases = [
                    { id: 'k1', kasus: 'Membuang sampah ke sungai sembarangan', jawabanId: 'hukum', penjelasan: 'Ada sanksi resmi denda pemda.' },
                    { id: 'k2', kasus: 'Menyerobot antrean tiket bus', jawabanId: 'kesopanan', penjelasan: 'Tata krama hidup bermasyarakat.' }
                ];
                window.showScreen('screen-result');
                window.renderResultScreen();
            """)
            await asyncio.sleep(0.5)

            test_5_res = await eval_js("""
                (() => {
                    const podiumCols = document.querySelectorAll('#result-podium-container .podium-col');
                    const remainingCards = document.querySelectorAll('#result-remaining-container .remaining-team-card');
                    const unsolvedPills = document.querySelectorAll('#result-unsolved-box .unsolved-compact-pill');
                    const scrollHeight = document.documentElement.scrollHeight;
                    const clientHeight = document.documentElement.clientHeight;

                    const centerCol = document.querySelector('.podium-col.pos-center');
                    const leftCol = document.querySelector('.podium-col.pos-left');
                    const rightCol = document.querySelector('.podium-col.pos-right');

                    const centerName = centerCol ? centerCol.querySelector('.podium-team-name').textContent.trim() : '';
                    const centerRank = centerCol ? centerCol.querySelector('.pedestal-rank-num').textContent.trim() : '';
                    const centerBadges = centerCol ? Array.from(centerCol.querySelectorAll('.podium-badge')).map(b => b.textContent.trim()) : [];

                    const leftName = leftCol ? leftCol.querySelector('.podium-team-name').textContent.trim() : '';
                    const leftRank = leftCol ? leftCol.querySelector('.pedestal-rank-num').textContent.trim() : '';
                    const leftBadges = leftCol ? Array.from(leftCol.querySelectorAll('.podium-badge')).map(b => b.textContent.trim()) : [];

                    const rightName = rightCol ? rightCol.querySelector('.podium-team-name').textContent.trim() : '';
                    const rightRank = rightCol ? rightCol.querySelector('.pedestal-rank-num').textContent.trim() : '';

                    const bantengCard = remainingCards[0];
                    const bantengText = bantengCard ? bantengCard.textContent : '';

                    return {
                        podiumCount: podiumCols.length,
                        remainingCount: remainingCards.length,
                        unsolvedCount: unsolvedPills.length,
                        centerName,
                        centerRank,
                        centerBadges,
                        leftName,
                        leftRank,
                        leftBadges,
                        rightName,
                        rightRank,
                        bantengHasInsufficient: bantengText.includes('belum cukup 3 jawaban benar'),
                        hasScrollbar: scrollHeight > clientHeight
                    };
                })()
            """)
            print("Hasil Uji 5 Kelompok 1080p:", json.dumps(test_5_res, indent=2))
            assert test_5_res["podiumCount"] == 3, f"Expected 3 podium cols, got {test_5_res['podiumCount']}"
            assert test_5_res["remainingCount"] == 2, f"Expected 2 remaining teams, got {test_5_res['remainingCount']}"
            assert test_5_res["centerName"] == "Tim Harimau", f"Harimau should be center (faster tie): {test_5_res['centerName']}"
            assert test_5_res["centerRank"] == "#1", f"Harimau rank should be #1"
            assert "Skor Tertinggi" in " ".join(test_5_res["centerBadges"]), "Harimau should have Skor Tertinggi"
            assert "Tercepat" in " ".join(test_5_res["centerBadges"]), "Harimau should have Tercepat"
            assert test_5_res["leftName"] == "Tim Elang", f"Elang should be left (tied): {test_5_res['leftName']}"
            assert test_5_res["leftRank"] == "#1", f"Elang rank should be #1"
            assert "Skor Tertinggi" in " ".join(test_5_res["leftBadges"]), "Elang should have Skor Tertinggi"
            assert test_5_res["rightName"] == "Tim Kancil", f"Kancil should be right: {test_5_res['rightName']}"
            assert test_5_res["rightRank"] == "#3", f"Kancil rank should be #3"
            assert test_5_res["bantengHasInsufficient"] == True, "Banteng (< 3) should have insufficient badge text"
            assert test_5_res["hasScrollbar"] == False, "1080p should not have scrollbars"
            print("PASS: 5 Kelompok 1080p OK!")

            print("\n--- TEST 2: Responsivitas 1366x768 ---")
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1366,
                "height": 768,
                "deviceScaleFactor": 1,
                "mobile": False
            })
            await asyncio.sleep(0.5)

            test_768_res = await eval_js("""
                (() => {
                    const scrollHeight = document.documentElement.scrollHeight;
                    const clientHeight = document.documentElement.clientHeight;
                    const scrollWidth = document.documentElement.scrollWidth;
                    const clientWidth = document.documentElement.clientWidth;
                    return {
                        hasVScroll: scrollHeight > clientHeight,
                        hasHScroll: scrollWidth > clientWidth,
                        scrollHeight,
                        clientHeight
                    };
                })()
            """)
            print("Hasil Uji 768p:", test_768_res)
            assert test_768_res["hasVScroll"] == False, "768p should not have vertical scrollbar"
            assert test_768_res["hasHScroll"] == False, "768p should not have horizontal scrollbar"
            print("PASS: 1366x768 OK!")

            print("\n--- TEST 3: 2 Kelompok ---")
            await eval_js("""
                window.State.groups = [
                    { id: 'g1', nama: 'Tim Elang', warna: '#E74C3C', skor: 18, correctCount: 3, correctTimes: [10.0, 12.0, 14.0] },
                    { id: 'g2', nama: 'Tim Harimau', warna: '#F39C12', skor: 21, correctCount: 4, correctTimes: [9.0, 9.5, 8.0, 7.5] }
                ];
                window.State.unsolvedCases = [];
                window.renderResultScreen();
            """)
            await asyncio.sleep(0.5)

            test_2_res = await eval_js("""
                (() => {
                    const podiumCols = document.querySelectorAll('#result-podium-container .podium-col');
                    const remainingCards = document.querySelectorAll('#result-remaining-container .remaining-team-card');
                    const successMsg = document.querySelector('.unsolved-compact-success');
                    const col1Name = podiumCols[0] ? podiumCols[0].querySelector('.podium-team-name').textContent.trim() : '';
                    const col2Name = podiumCols[1] ? podiumCols[1].querySelector('.podium-team-name').textContent.trim() : '';
                    return {
                        podiumCount: podiumCols.length,
                        remainingCount: remainingCards.length,
                        hasSuccessMsg: !!successMsg,
                        col1Name,
                        col2Name
                    };
                })()
            """)
            print("Hasil Uji 2 Kelompok:", test_2_res)
            assert test_2_res["podiumCount"] == 2, f"Expected 2 podium cols, got {test_2_res['podiumCount']}"
            assert test_2_res["remainingCount"] == 0, "No remaining cards for 2 groups"
            assert test_2_res["col1Name"] == "Tim Harimau", "Harimau should be 1st"
            assert test_2_res["col2Name"] == "Tim Elang", "Elang should be 2nd"
            assert test_2_res["hasSuccessMsg"] == True, "0 unsolved cases shows success message"
            print("PASS: 2 Kelompok OK!")

            print("\n--- TEST 4: 3 Kelompok & Tombol Aksi ---")
            await eval_js("""
                window.State.groups = [
                    { id: 'g1', nama: 'Tim Elang', warna: '#E74C3C', skor: 15, correctCount: 3, correctTimes: [11.0, 12.0, 13.0] },
                    { id: 'g2', nama: 'Tim Harimau', warna: '#F39C12', skor: 21, correctCount: 3, correctTimes: [10.0, 9.0, 8.0] },
                    { id: 'g3', nama: 'Tim Kancil', warna: '#27AE60', skor: 9, correctCount: 2, correctTimes: [7.0, 6.0] }
                ];
                window.renderResultScreen();
            """)
            await asyncio.sleep(0.5)

            test_3_res = await eval_js("""
                (() => {
                    const podiumCols = document.querySelectorAll('#result-podium-container .podium-col');
                    const remainingContainer = document.getElementById('result-remaining-container');
                    const btnReplay = document.getElementById('btn-result-replay-same');
                    const btnLead = document.getElementById('btn-result-leaderboard');
                    return {
                        podiumCount: podiumCols.length,
                        remainingDisplay: remainingContainer ? remainingContainer.style.display : '',
                        btnReplayHeight: btnReplay ? btnReplay.offsetHeight : 0,
                        btnLeadHeight: btnLead ? btnLead.offsetHeight : 0,
                        btnReplayBigger: btnReplay && btnLead ? btnReplay.offsetHeight >= btnLead.offsetHeight : false
                    };
                })()
            """)
            print("Hasil Uji 3 Kelompok & Tombol:", test_3_res)
            assert test_3_res["podiumCount"] == 3, "Expected 3 podium cols"
            assert test_3_res["remainingDisplay"] == "none", "Remaining container should be hidden for 3 groups"
            assert test_3_res["btnReplayBigger"] == True, "Main Lagi button should be bigger and most prominent"
            print("PASS: 3 Kelompok & Tombol OK!")

            print("\nALL FASE 4 TESTS PASSED!")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    asyncio.run(run_test())
