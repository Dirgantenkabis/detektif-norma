import asyncio, websockets, json, subprocess, tempfile, urllib.request, os, base64
from PIL import Image, ImageChops

EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(EDGE_PATH): EDGE_PATH = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

def count_diff_pixels(img_path1, img_path2):
    im1 = Image.open(img_path1).convert('RGB')
    im2 = Image.open(img_path2).convert('RGB')
    if im1.size != im2.size:
        return -1
    diff = ImageChops.difference(im1, im2)
    bbox = diff.getbbox()
    if not bbox:
        return 0
    diff_pixels = 0
    data1 = im1.load()
    data2 = im2.load()
    w, h = im1.size
    for x in range(w):
        for y in range(h):
            if data1[x, y] != data2[x, y]:
                diff_pixels += 1
    return diff_pixels

async def main():
    tmp = tempfile.mkdtemp()
    p = subprocess.Popen([
        EDGE_PATH,
        '--headless=new',
        '--remote-debugging-port=9499',
        f'--user-data-dir={tmp}',
        '--disable-extensions',
        '--disable-gpu',
        '--no-sandbox'
    ])

    try:
        await asyncio.sleep(1.8)
        with urllib.request.urlopen('http://localhost:9499/json') as r:
            pages = json.loads(r.read())
        ws_url = pages[0]['webSocketDebuggerUrl']

        async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
            msg_id = 0
            console_errors = []

            async def call(method, params=None):
                nonlocal msg_id
                msg_id += 1
                await ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
                while True:
                    resp = json.loads(await ws.recv())
                    if resp.get('method') == 'Runtime.consoleAPICalled':
                        args = resp.get('params', {})
                        if args.get('type') == 'error':
                            console_errors.append(str(args))
                    elif resp.get('method') == 'Runtime.exceptionThrown':
                        console_errors.append(str(resp.get('params', {})))
                    if resp.get('id') == msg_id:
                        return resp.get('result', {})

            async def eval_js(expr):
                res = await call('Runtime.evaluate', {'expression': expr, 'returnByValue': True})
                return res.get('result', {}).get('value')

            async def take_screenshot(path):
                res = await call('Page.captureScreenshot', {'format': 'png'})
                img_data = base64.b64decode(res['data'])
                with open(path, 'wb') as f:
                    f.write(img_data)

            await call('Page.enable')
            await call('Runtime.enable')

            fp = os.path.abspath('index.html').replace('\\', '/')

            # =================================================================
            # 1. REGRESI TV: 0 PIXEL DIFF & 3 SESI BERTURUT-TURUT TANPA RELOAD
            # =================================================================
            print("\n=======================================================")
            print("1. MEMERIKSA REGRESI TV: 0 PIXEL DIFF & 3 SESI TANPA RELOAD")
            print("=======================================================")

            for label, w, h in [('1080p', 1920, 1080), ('768p', 1366, 768)]:
                await call('Page.navigate', {'url': f'file:///{fp}'})
                await asyncio.sleep(0.5)
                await call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': False})
                await asyncio.sleep(0.3)

                # Start Screen Diff
                test_start = f"baseline_tv/test_qa_start_{label}.png"
                base_start = f"baseline_tv/start_{label}.png"
                await take_screenshot(test_start)
                diff_start = count_diff_pixels(base_start, test_start)
                print(f"Start Screen ({label}): {diff_start} piksel berbeda")
                assert diff_start == 0, f"ERROR: Pixel diff Start {label} is {diff_start}!"

                # Board Screen Diff
                await eval_js("""
                    window.showScreen('screen-setup');
                    document.querySelector('.btn-count-choice[data-count="4"]').click();
                    const btnProceed = document.getElementById('btn-proceed-to-game');
                    if (btnProceed) btnProceed.click();
                    window.State.sessionCases = [KASUS_POOL[0]];
                    window.State.currentCaseIndex = 0;
                    window.loadCase(0);
                    if (window.State.timerInterval) clearInterval(window.State.timerInterval);
                    window.State.timerSeconds = 0;
                    const timerVal = document.getElementById('board-timer-val');
                    if (timerVal) timerVal.textContent = '00';
                """)
                await asyncio.sleep(0.4)
                test_board = f"baseline_tv/test_qa_board_{label}.png"
                base_board = f"baseline_tv/board_{label}.png"
                await take_screenshot(test_board)
                diff_board = count_diff_pixels(base_board, test_board)
                print(f"Board Screen ({label}): {diff_board} piksel berbeda")
                assert diff_board == 0, f"ERROR: Pixel diff Board {label} is {diff_board}!"

                # Result Screen Diff
                await eval_js("""
                    window.State.groups = [
                        { id: 'g1', nama: 'Tim Elang', warna: '#1E6B4C', skor: 15, correctTimes: [4.0, 4.2, 4.4], correctCount: 3 },
                        { id: 'g2', nama: 'Tim Harimau', warna: '#8B1E22', skor: 12, correctTimes: [5.0, 5.2, 5.4], correctCount: 3 },
                        { id: 'g3', nama: 'Tim Kancil', warna: '#1A4472', skor: 9, correctTimes: [6.0, 6.2, 6.4], correctCount: 3 },
                        { id: 'g4', nama: 'Tim Banteng', warna: '#9C651F', skor: 6, correctTimes: [7.0, 7.2], correctCount: 2 }
                    ];
                    window.State.sessionCases = [
                        { id: 'k01', tingkat: 'dasar', kasus: 'Kasus 1' },
                        { id: 'k15', tingkat: 'hots', kasus: 'Kasus 15', pertanyaanLanjutan: 'Refleksi' }
                    ];
                    window.State.currentCaseIndex = 1;
                    window.State.unsolvedCases = [];
                    window.launchConfetti = () => {};
                    window.renderResultScreen();
                    window.showScreen('screen-result');
                    const pod = document.querySelector('.result-podium-container');
                    if (pod) {
                        pod.classList.remove('ceremony-active');
                        pod.querySelectorAll('.podium-col').forEach(c => {
                            c.classList.add('revealed');
                            c.style.transition = 'none';
                        });
                    }
                    const canvas = document.getElementById('confetti-canvas');
                    if (canvas) {
                        canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
                    }
                """)
                await asyncio.sleep(0.4)
                test_result = f"baseline_tv/test_qa_result_{label}.png"
                base_result = f"baseline_tv/result_{label}.png"
                await take_screenshot(test_result)
                diff_result = count_diff_pixels(base_result, test_result)
                print(f"Result Screen ({label}): {diff_result} piksel berbeda")
                assert diff_result == 0, f"ERROR: Pixel diff Result {label} is {diff_result}!"

            print("-> Verifikasi Selisih Piksel TV Lolos: 0 Piksel Berbeda!")

            # Pengujian 3 sesi berturut-turut tanpa reload di TV
            print("\n-> Menjalankan 3 Sesi Berturut-turut Tanpa Reload di TV 1080p...")
            for session_num in range(1, 4):
                res = await eval_js(f"""
                    (() => {{
                        if ({session_num} === 1) {{
                            window.showScreen('screen-setup');
                            document.querySelector('.btn-count-choice[data-count="4"]').click();
                            const p = document.getElementById('btn-proceed-to-game');
                            if (p) p.click();
                        }} else {{
                            document.getElementById('btn-result-replay-same').click();
                        }}

                        // Simulasi 12 kasus cepat
                        for (let i = 0; i < 12; i++) {{
                            window.State.currentCaseIndex = i;
                            window.loadCase(i);
                            const answerNorma = window.State.sessionCases[i].jawabanId;
                            window.handleStampAnswer(answerNorma);
                            if (window.State.sessionCases[i].tingkat === 'hots') {{
                                window.evaluateReason(true);
                            }}
                            if (i < 11) {{
                                const nextBtn = document.getElementById('btn-next-case');
                                if (nextBtn) nextBtn.click();
                            }} else {{
                                window.finishGameSession();
                            }}
                        }}

                        return {{
                            activeScreen: document.querySelector('.screen.active').id,
                            groupsCount: window.State.groups.length,
                            totalAnswered: window.State.groups.reduce((acc, g) => acc + g.correctCount, 0)
                        }};
                    }})()
                """)
                print(f"   Sesi #{session_num}: Layar={res['activeScreen']}, Tim={res['groupsCount']}, Jawaban Benar={res['totalAnswered']}")
                assert res['activeScreen'] == 'screen-result', f"ERROR: Sesi {session_num} gagal mencapai layar hasil!"

            print("-> 3 Sesi Berturut-turut Tanpa Reload di TV: 100% Lolos!")

            # =================================================================
            # 2. MATRIKS UJI CDP: 12 UKURAN HP & TABLET (TEGAK DAN MENDATAR)
            # =================================================================
            print("\n=======================================================")
            print("2. MEMERIKSA MATRIKS RESPONSIF HP & TABLET (12 RESOLUSI)")
            print("=======================================================")

            device_matrix = [
                # HP Tegak
                {"name": "Android Small Portrait (360x640)", "w": 360, "h": 640, "mobile": True},
                {"name": "iPhone SE Portrait (375x667)", "w": 375, "h": 667, "mobile": True},
                {"name": "iPhone 13/14 Portrait (390x844)", "w": 390, "h": 844, "mobile": True},
                {"name": "Android Medium Portrait (412x915)", "w": 412, "h": 915, "mobile": True},
                {"name": "iPhone Pro Max Portrait (430x932)", "w": 430, "h": 932, "mobile": True},
                {"name": "iPad Portrait (768x1024)", "w": 768, "h": 1024, "mobile": True},

                # HP Mendatar
                {"name": "Android Small Landscape (640x360)", "w": 640, "h": 360, "mobile": True},
                {"name": "iPhone SE Landscape (667x375)", "w": 667, "h": 375, "mobile": True},
                {"name": "iPhone 13/14 Landscape (844x390)", "w": 844, "h": 390, "mobile": True},
                {"name": "Android Medium Landscape (915x412)", "w": 915, "h": 412, "mobile": True},
                {"name": "iPhone Pro Max Landscape (932x430)", "w": 932, "h": 430, "mobile": True},
                {"name": "iPad Landscape (1024x768)", "w": 1024, "h": 768, "mobile": False}
            ]

            screens_to_check = ['screen-start', 'screen-setup', 'screen-board', 'screen-result', 'screen-leaderboard']
            modals_to_check = ['modal-rules', 'modal-about', 'modal-role-reminder', 'modal-edit-names']

            for dev in device_matrix:
                await call('Emulation.setDeviceMetricsOverride', {
                    'width': dev['w'],
                    'height': dev['h'],
                    'deviceScaleFactor': 1,
                    'mobile': dev['mobile']
                })
                await call('Emulation.setTouchEmulationEnabled', {'enabled': dev['mobile']})
                await asyncio.sleep(0.2)

                # Reset to start
                await eval_js("window.showScreen('screen-start');")

                # Periksa tiap layar
                for scr in screens_to_check:
                    if scr == 'screen-board':
                        # Setup kasus normal dan HOTS
                        await eval_js("""
                            window.State.groups = [
                                { id: 'g1', nama: 'Tim Elang', warna: '#1E6B4C', skor: 0, correctTimes: [], correctCount: 0 },
                                { id: 'g2', nama: 'Tim Harimau', warna: '#8B1E22', skor: 0, correctTimes: [], correctCount: 0 }
                            ];
                            window.State.sessionCases = [KASUS_POOL[0], KASUS_POOL.find(k => k.tingkat === 'hots')];
                            window.State.currentCaseIndex = 0;
                            window.loadCase(0);
                            window.showScreen('screen-board');
                        """)
                    elif scr == 'screen-result':
                        await eval_js("""
                            window.State.groups = [
                                { id: 'g1', nama: 'Tim Elang', warna: '#1E6B4C', skor: 15, correctTimes: [3.5, 4.0, 4.5], correctCount: 3 },
                                { id: 'g2', nama: 'Tim Harimau', warna: '#8B1E22', skor: 12, correctTimes: [4.5, 5.0, 5.5], correctCount: 3 },
                                { id: 'g3', nama: 'Tim Kancil', warna: '#1A4472', skor: 9, correctTimes: [5.5, 6.0, 6.5], correctCount: 3 },
                                { id: 'g4', nama: 'Tim Banteng', warna: '#9C651F', skor: 6, correctTimes: [6.5, 7.0], correctCount: 2 },
                                { id: 'g5', nama: 'Tim Rusa', warna: '#6B2D5C', skor: 3, correctTimes: [7.5], correctCount: 1 }
                            ];
                            window.State.unsolvedCases = [];
                            window.launchConfetti = () => {};
                            window.renderResultScreen();
                            window.showScreen('screen-result');
                        """)
                    elif scr == 'screen-leaderboard':
                        await eval_js("""
                            window.renderLeaderboardTable();
                            window.showScreen('screen-leaderboard');
                        """)
                    else:
                        await eval_js(f"window.showScreen('{scr}');")

                    await asyncio.sleep(0.15)

                    # Validasi metrik layout
                    metrics = await eval_js(f"""
                        (() => {{
                            const doc = document.documentElement;
                            const winW = window.innerWidth;
                            const winH = window.innerHeight;
                            const scrEl = document.getElementById('{scr}');
                            const rScr = scrEl.getBoundingClientRect();

                            // Tombol-tombol yang terlihat
                            const visibleBtns = Array.from(scrEl.querySelectorAll('button:not([style*="display: none"]), .btn:not([style*="display: none"])'))
                                .filter(b => b.offsetWidth > 0 && b.offsetHeight > 0);
                            const minBtnH = visibleBtns.length > 0 ? Math.min(...visibleBtns.map(b => b.offsetHeight)) : 44;

                            return {{
                                hasDocScroll: doc.scrollHeight > winH || doc.scrollWidth > winW,
                                scrRight: rScr.right,
                                scrBottom: rScr.bottom,
                                fitsInViewport: rScr.left >= 0 && rScr.right <= winW + 2,
                                minBtnH: minBtnH
                            }};
                        }})()
                    """)

                    assert not metrics['hasDocScroll'], f"ERROR: Doc scrollbar on {dev['name']} at {scr}!"
                    assert metrics['fitsInViewport'], f"ERROR: Screen {scr} overflows width on {dev['name']}!"
                    if dev['mobile']:
                        assert metrics['minBtnH'] >= 32, f"ERROR: Button < 32px on {dev['name']} at {scr} ({metrics['minBtnH']}px)!"

                # Periksa modal-modal
                for mid in modals_to_check:
                    await eval_js(f"window.openModal('{mid}');")
                    await asyncio.sleep(0.1)
                    m_metrics = await eval_js(f"""
                        (() => {{
                            const modal = document.getElementById('{mid}');
                            const card = modal.querySelector('.modal-card');
                            const body = modal.querySelector('.modal-body');
                            const winH = window.innerHeight;
                            const winW = window.innerWidth;
                            const rCard = card.getBoundingClientRect();
                            const bOverflow = window.getComputedStyle(body).overflowY;

                            return {{
                                heightPct: (rCard.height / winH) * 100,
                                fitsW: rCard.left >= 0 && rCard.right <= winW + 2,
                                bodyScrollable: bOverflow === 'auto' || bOverflow === 'scroll'
                            }};
                        }})()
                    """)
                    assert m_metrics['heightPct'] <= 92.0, f"ERROR: {mid} height exceeds 92dvh on {dev['name']} ({m_metrics['heightPct']:.1f}%)!"
                    assert m_metrics['fitsW'], f"ERROR: {mid} card overflows width on {dev['name']}!"
                    await eval_js(f"window.closeModal('{mid}');")

                print(f"[{dev['name']}] Semua layar & modal: Bebas scroll luar, elemen muat, touch target valid.")

            print("-> Matriks 12 Resolusi HP/Tablet 100% Lolos!")

            # =================================================================
            # 3. SIMULASI SESI PENUH 12 KASUS DENGAN 2 DAN 5 KELOMPOK
            # =================================================================
            print("\n=======================================================")
            print("3. MEMERIKSA SESI PENUH 12 KASUS (2 DAN 5 TIM DI TEGAK & MENDATAR)")
            print("=======================================================")

            for mode_name, w, h in [("HP Tegak (390x844)", 390, 844), ("HP Mendatar (844x390)", 844, 390)]:
                await call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': True})
                await call('Emulation.setTouchEmulationEnabled', {'enabled': True})

                for team_count in [2, 5]:
                    sim_res = await eval_js(f"""
                        (() => {{
                            window.showScreen('screen-setup');
                            document.querySelector('.btn-count-choice[data-count="{team_count}"]').click();
                            const p = document.getElementById('btn-proceed-to-game');
                            if (p) p.click();

                            // Mainkan 12 kasus
                            for (let i = 0; i < 12; i++) {{
                                window.State.currentCaseIndex = i;
                                window.loadCase(i);
                                const answerNorma = window.State.sessionCases[i].jawabanId;
                                window.handleStampAnswer(answerNorma);
                                if (window.State.sessionCases[i].tingkat === 'hots') {{
                                    window.evaluateReason(true);
                                }}
                                if (i < 11) {{
                                    const nextBtn = document.getElementById('btn-next-case');
                                    if (nextBtn) nextBtn.click();
                                }} else {{
                                    window.finishGameSession();
                                }}
                            }}

                            const pod = document.querySelector('.result-podium-container');
                            const cards = document.querySelectorAll('.remaining-team-card');
                            return {{
                                activeScreen: document.querySelector('.screen.active').id,
                                teamCount: window.State.groups.length,
                                podiumColumns: pod ? pod.querySelectorAll('.podium-col').length : 0,
                                remainingCards: cards.length
                            }};
                        }})()
                    """)
                    print(f"[{mode_name} - {team_count} Tim] Selesai 12 Kasus -> Layar: {sim_res['activeScreen']}, Podium Cols: {sim_res['podiumColumns']}, Rem Cards: {sim_res['remainingCards']}")
                    assert sim_res['activeScreen'] == 'screen-result', f"ERROR: Sesi gagal di {mode_name} dengan {team_count} tim!"
                    if team_count == 2:
                        assert sim_res['podiumColumns'] == 2, f"ERROR: Podium harus 2 kolom untuk 2 tim!"
                        assert sim_res['remainingCards'] == 0, f"ERROR: Sisa kartu harus 0 untuk 2 tim!"
                    elif team_count == 5:
                        assert sim_res['podiumColumns'] == 3, f"ERROR: Podium harus 3 kolom untuk 5 tim!"
                        assert sim_res['remainingCards'] == 2, f"ERROR: Sisa kartu harus 2 untuk 5 tim!"

            print("-> Simulasi 12 Kasus Penuh (2 dan 5 tim di Tegak & Mendatar): 100% Lolos!")

            # =================================================================
            # 4. MEMERIKSA ERROR CONSOLE
            # =================================================================
            print("\n=======================================================")
            print("4. MEMERIKSA KONSOL PERAMBAN DARI ERROR/EXCEPTION")
            print("=======================================================")
            print(f"Total Console Errors Terdeteksi: {len(console_errors)}")
            if console_errors:
                for err in console_errors:
                    print(f"  [Console Error]: {err}")
            assert len(console_errors) == 0, f"ERROR: Terdeteksi error pada konsol browser!"
            print("-> Bebas Error Konsol: 100% Lolos!")

            print("\n=======================================================")
            print("SEMUA PENGUJIAN FASE 5 (QA & REGRESI) LOLOS 100%!")
            print("=======================================================")

    finally:
        p.terminate()

if __name__ == '__main__':
    asyncio.run(main())
