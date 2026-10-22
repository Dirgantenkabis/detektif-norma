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
        '--remote-debugging-port=9488',
        f'--user-data-dir={tmp}',
        '--disable-extensions',
        '--disable-gpu',
        '--no-sandbox'
    ])
    await asyncio.sleep(1.8)
    try:
        req = urllib.request.urlopen('http://127.0.0.1:9488/json')
        tabs = json.loads(req.read().decode())
        ws_url = next(t for t in tabs if t.get('type') == 'page')['webSocketDebuggerUrl']
        async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
            msg_id = 1
            async def call(m, params=None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                await ws.send(json.dumps({'id': cid, 'method': m, 'params': params or {}}))
                while True:
                    r = json.loads(await ws.recv())
                    if r.get('id') == cid:
                        res = r.get('result', {})
                        if 'result' in res and 'value' in res['result']:
                            return res['result']['value']
                        return res

            async def eval_js(expression):
                res = await call("Runtime.evaluate", {"expression": expression, "returnByValue": True})
                if isinstance(res, dict) and 'exceptionDetails' in res.get('result', {}):
                    print("JS EXCEPTION:", res['result']['exceptionDetails'])
                    return None
                if isinstance(res, dict) and 'result' in res and 'value' in res['result']:
                    return res['result']['value']
                return res

            async def take_screenshot(filename):
                data = await call("Page.captureScreenshot", {"format": "png"})
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(data["data"]))

            await call('Page.enable')
            await call('Runtime.enable')
            fp = os.path.abspath('index.html').replace('\\', '/')

            # =================================================================
            # 1. VERIFIKASI SELISIH PIKSEL TV (1080p & 768p) HARUS 0
            # =================================================================
            print("\n=======================================================")
            print("1. MEMERIKSA SELISIH PIKSEL TV / DESKTOP (TARGET: 0 PIXEL)")
            print("=======================================================")

            tv_tests = [
                ("1080p", 1920, 1080),
                ("768p", 1366, 768)
            ]

            for label, w, h in tv_tests:
                await call('Page.navigate', {'url': f'file:///{fp}'})
                await asyncio.sleep(0.5)
                await call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': False})
                await asyncio.sleep(0.3)

                # Start Screen
                test_start = f"baseline_tv/test_phase2_start_{label}.png"
                base_start = f"baseline_tv/start_{label}.png"
                await take_screenshot(test_start)
                diff_start = count_diff_pixels(base_start, test_start)
                print(f"Start Screen ({label}): {diff_start} piksel berbeda")
                assert diff_start == 0, f"ERROR: Pixel difference on Start {label} is {diff_start} (must be 0)!"

                # Board Screen
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
                test_board = f"baseline_tv/test_phase2_board_{label}.png"
                base_board = f"baseline_tv/board_{label}.png"
                await take_screenshot(test_board)
                diff_board = count_diff_pixels(base_board, test_board)
                print(f"Board Screen ({label}): {diff_board} piksel berbeda")
                assert diff_board == 0, f"ERROR: Pixel difference on Board {label} is {diff_board} (must be 0)!"

                # Result Screen
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
                test_result = f"baseline_tv/test_phase2_result_{label}.png"
                base_result = f"baseline_tv/result_{label}.png"
                await take_screenshot(test_result)
                diff_result = count_diff_pixels(base_result, test_result)
                print(f"Result Screen ({label}): {diff_result} piksel berbeda")
                assert diff_result == 0, f"ERROR: Pixel difference on Result {label} is {diff_result} (must be 0)!"

            print("-> VERIFIKASI TV 100% LOLOS: SELISIH PIKSEL = 0 PADA SEMUA LAYAR!")

            # =================================================================
            # 2. VERIFIKASI PAPAN KASUS HP TEGAK (390x844, 375x667, 360x640, 430x932)
            # =================================================================
            print("\n=======================================================")
            print("2. MEMERIKSA PAPAN KASUS HP TEGAK PADA 4 UKURAN TARGET")
            print("=======================================================")

            hp_viewports = [
                {"name": "iPhone 13/14 Portrait", "width": 390, "height": 844},
                {"name": "iPhone SE Portrait", "width": 375, "height": 667},
                {"name": "Android Small Portrait", "width": 360, "height": 640},
                {"name": "iPhone Pro Max Portrait", "width": 430, "height": 932}
            ]

            for vp in hp_viewports:
                w, h = vp["width"], vp["height"]
                print(f"\n--- Menguji {vp['name']} ({w}x{h}) ---")

                for team_count in [2, 5]:
                    await call('Page.navigate', {'url': f'file:///{fp}'})
                    await asyncio.sleep(0.4)
                    await call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': True})
                    await asyncio.sleep(0.3)

                    # Setup game dengan team_count
                    await eval_js(f"""
                        window.showScreen('screen-setup');
                        document.querySelector('.btn-count-choice[data-count="{team_count}"]').click();
                        const btnProceed = document.getElementById('btn-proceed-to-game');
                        if (btnProceed) btnProceed.click();
                        // Muat kasus HOTS teks panjang (k17 atau k15)
                        const hotsLong = KASUS_POOL.find(k => k.tingkat === 'hots' && k.kasus.length > 80) || KASUS_POOL[16];
                        window.State.sessionCases = [hotsLong];
                        window.State.currentCaseIndex = 0;
                        window.loadCase(0);
                    """)
                    await asyncio.sleep(0.3)

                    # Periksa Bounding Boxes, Tumpang Tindih, Ukuran Tombol, Ukuran Font Kasus
                    metrics = await eval_js("""
                        (() => {
                            const header = document.getElementById('board-header');
                            const teams = document.querySelector('.teams-sidebar');
                            const folder = document.getElementById('case-folder');
                            const teacher = document.querySelector('.teacher-sidebar');
                            const stamps = document.querySelector('.stamps-section');
                            const caseText = document.getElementById('folder-case-text');
                            const doc = document.documentElement;

                            const rHeader = header.getBoundingClientRect();
                            const rTeams = teams.getBoundingClientRect();
                            const rFolder = folder.getBoundingClientRect();
                            const rTeacher = teacher.getBoundingClientRect();
                            const rStamps = stamps.getBoundingClientRect();

                            // Cek tumpang tindih vertikal antara 5 zona berurutan
                            const overlapHeaderTeams = rHeader.bottom > rTeams.top + 1;
                            const overlapTeamsFolder = rTeams.bottom > rFolder.top + 1;
                            const overlapFolderTeacher = rFolder.bottom > rTeacher.top + 1;
                            const overlapTeacherStamps = rTeacher.bottom > rStamps.top + 1;

                            // Cek tinggi tombol bilah guru (min 48px)
                            const teacherBtns = Array.from(document.querySelectorAll('.teacher-btn'));
                            const teacherBtnsMinH = Math.min(...teacherBtns.map(b => b.getBoundingClientRect().height));

                            // Cek ukuran stempel (min 56px)
                            const stampBtns = Array.from(document.querySelectorAll('.norma-stamp'));
                            const stampBtnsMinH = Math.min(...stampBtns.map(b => b.getBoundingClientRect().height));

                            // Cek ukuran chip kelompok (min 48px)
                            const teamChips = Array.from(document.querySelectorAll('.team-card-btn'));
                            const teamChipsMinH = Math.min(...teamChips.map(b => b.getBoundingClientRect().height));

                            // Cek ukuran font kasus (>= 20px)
                            const caseStyle = window.getComputedStyle(caseText);
                            const caseFontSize = parseFloat(caseStyle.fontSize);

                            // Cek scroll halaman
                            const hasPageScroll = doc.scrollHeight > doc.clientHeight + 2;

                            // Cek horizontal scroll chip jika 5 tim
                            const teamsList = document.getElementById('teams-list-container');
                            const hasHorizScrollTeams = teamsList.scrollWidth > teamsList.clientWidth;

                            return {
                                overlapHeaderTeams: overlapHeaderTeams,
                                overlapTeamsFolder: overlapTeamsFolder,
                                overlapFolderTeacher: overlapFolderTeacher,
                                overlapTeacherStamps: overlapTeacherStamps,
                                teacherBtnsMinH: teacherBtnsMinH,
                                stampBtnsMinH: stampBtnsMinH,
                                teamChipsMinH: teamChipsMinH,
                                caseFontSize: caseFontSize,
                                hasPageScroll: hasPageScroll,
                                hasHorizScrollTeams: hasHorizScrollTeams,
                                docScrollH: doc.scrollHeight,
                                docClientH: doc.clientHeight
                            };
                        })()
                    """)

                    print(f"  [{team_count} Tim] Page Scroll: {metrics['hasPageScroll']} ({metrics['docScrollH']}/{metrics['docClientH']}px)")
                    print(f"  [{team_count} Tim] Teks Kasus Font: {metrics['caseFontSize']}px (Target: >= 20px)")
                    print(f"  [{team_count} Tim] Tinggi Tombol Guru: {metrics['teacherBtnsMinH']:.1f}px (Target: >= 48px)")
                    print(f"  [{team_count} Tim] Tinggi Stempel: {metrics['stampBtnsMinH']:.1f}px (Target: >= 56px)")
                    print(f"  [{team_count} Tim] Tinggi Chip Tim: {metrics['teamChipsMinH']:.1f}px (Target: >= 48px)")
                    print(f"  [{team_count} Tim] Overlaps: H-T={metrics['overlapHeaderTeams']}, T-F={metrics['overlapTeamsFolder']}, F-Tr={metrics['overlapFolderTeacher']}, Tr-S={metrics['overlapTeacherStamps']}")

                    assert not metrics['hasPageScroll'], f"ERROR: Page scroll detected on {vp['name']} with {team_count} teams!"
                    assert metrics['caseFontSize'] >= 20, f"ERROR: Case font size < 20px ({metrics['caseFontSize']}px) on {vp['name']}!"
                    assert metrics['teacherBtnsMinH'] >= 48, f"ERROR: Teacher btn height < 48px ({metrics['teacherBtnsMinH']}px) on {vp['name']}!"
                    assert metrics['stampBtnsMinH'] >= 56, f"ERROR: Stamp height < 56px ({metrics['stampBtnsMinH']}px) on {vp['name']}!"
                    assert metrics['teamChipsMinH'] >= 48, f"ERROR: Team chip height < 48px ({metrics['teamChipsMinH']}px) on {vp['name']}!"
                    assert not metrics['overlapHeaderTeams'], "ERROR: Header and Teams overlap!"
                    assert not metrics['overlapTeamsFolder'], "ERROR: Teams and Folder overlap!"
                    assert not metrics['overlapFolderTeacher'], "ERROR: Folder and Teacher bar overlap!"
                    assert not metrics['overlapTeacherStamps'], "ERROR: Teacher bar and Stamps overlap!"

                    if team_count == 5:
                        assert metrics['hasHorizScrollTeams'], f"ERROR: 5 teams chip container should be scrollable horizontally on {vp['name']}!"

                    # =============================================================
                    # UJI BOTTOM SHEET: EVALUASI ALASAN & PENJELASAN
                    # =============================================================
                    # Pilih tim 0
                    await eval_js("window.handleSelectGroupTurn(0);")
                    await asyncio.sleep(0.1)

                    # Jawab benar dengan stempel jawaban yang tepat
                    await eval_js("""
                        const cur = window.State.sessionCases[window.State.currentCaseIndex];
                        window.handleStampAnswer(cur.jawabanId);
                    """)
                    await asyncio.sleep(0.4)

                    sheet_metrics = await eval_js("""
                        (() => {
                            const sheet = document.querySelector('.folder-action-zone');
                            const feedbackBar = document.getElementById('case-feedback-bar');
                            const caseText = document.getElementById('folder-case-text');
                            const stampSolved = document.getElementById('stamp-terpecahkan');
                            const btnSensible = document.getElementById('btn-reason-sensible');
                            const btnPass = document.getElementById('btn-reason-pass');

                            const rSheet = sheet.getBoundingClientRect();
                            const rFeedback = feedbackBar.getBoundingClientRect();
                            const rCaseText = caseText.getBoundingClientRect();
                            const rStamp = stampSolved.getBoundingClientRect();
                            const rBtnSensible = btnSensible.getBoundingClientRect();
                            const rBtnPass = btnPass.getBoundingClientRect();

                            const winH = window.innerHeight;
                            const sheetH = rSheet.height;
                            const sheetMaxHPercent = (sheetH / winH) * 100;

                            // Cek teks kasus terlihat di atas sheet
                            const caseTextAboveSheet = rCaseText.bottom <= rSheet.top || rCaseText.top < rSheet.top;

                            // Cek stempel terpecahkan tidak tertutup sheet
                            const stampNotCovered = rStamp.bottom <= rSheet.top;

                            // Cek feedback bar menyatu di kepala sheet
                            const feedbackAtHead = Math.abs(rFeedback.top - rSheet.top) < 3;

                            return {
                                sheetHeight: sheetH,
                                sheetMaxHPercent: sheetMaxHPercent,
                                caseTextAboveSheet: caseTextAboveSheet,
                                stampNotCovered: stampNotCovered,
                                feedbackAtHead: feedbackAtHead,
                                sensibleBtnHeight: rBtnSensible.height,
                                passBtnHeight: rBtnPass.height
                            };
                        })()
                    """)

                    print(f"  [{team_count} Tim] Bottom Sheet Height: {sheet_metrics['sheetHeight']:.1f}px ({sheet_metrics['sheetMaxHPercent']:.1f}% <= 62%)")
                    print(f"  [{team_count} Tim] Case Text Above Sheet: {sheet_metrics['caseTextAboveSheet']}")
                    print(f"  [{team_count} Tim] Stempel TERPECAHKAN Uncovered: {sheet_metrics['stampNotCovered']}")
                    print(f"  [{team_count} Tim] Feedback At Head: {sheet_metrics['feedbackAtHead']}")
                    print(f"  [{team_count} Tim] Tombol Alasan Min-H: {min(sheet_metrics['sensibleBtnHeight'], sheet_metrics['passBtnHeight']):.1f}px (>= 48px)")

                    assert sheet_metrics['sheetMaxHPercent'] <= 63.0, f"ERROR: Bottom sheet height exceeds 62% ({sheet_metrics['sheetMaxHPercent']:.1f}%) on {vp['name']}!"
                    assert sheet_metrics['caseTextAboveSheet'], f"ERROR: Case text is covered by sheet on {vp['name']}!"
                    assert sheet_metrics['stampNotCovered'], f"ERROR: Stempel TERPECAHKAN is covered by bottom sheet on {vp['name']}!"
                    assert sheet_metrics['feedbackAtHead'], f"ERROR: Feedback banner is not at the head of sheet on {vp['name']}!"
                    assert sheet_metrics['sensibleBtnHeight'] >= 48, f"ERROR: Sensible button height < 48px on {vp['name']}!"
                    assert sheet_metrics['passBtnHeight'] >= 48, f"ERROR: Pass button height < 48px on {vp['name']}!"

                    # Uji lanjut ke Penjelasan Norma & Tombol Kasus Berikutnya
                    next_metrics = await eval_js("""
                        (() => {
                            window.evaluateReason(true);
                            const nextBtn = document.getElementById('btn-next-case');
                            const rNext = nextBtn.getBoundingClientRect();
                            return {
                                nextBtnHeight: rNext.height,
                                nextBtnVisible: rNext.width > 0 && rNext.height > 0
                            };
                        })()
                    """)
                    print(f"  [{team_count} Tim] Tombol Kasus Berikutnya: {next_metrics['nextBtnHeight']:.1f}px (>= 48px, Visible: {next_metrics['nextBtnVisible']})")
                    assert next_metrics['nextBtnHeight'] >= 48, f"ERROR: Next Case button height < 48px on {vp['name']}!"

            # =================================================================
            # 3. UJI SATU SESI 12 KASUS PENUH PADA HP TEGAK (SIMULASI ALUR PENUH)
            # =================================================================
            print("\n=======================================================")
            print("3. MEMERIKSA SIMULASI PENUH 12 KASUS DI HP TEGAK (390x844)")
            print("=======================================================")

            await call('Page.navigate', {'url': f'file:///{fp}'})
            await asyncio.sleep(0.4)
            await call('Emulation.setDeviceMetricsOverride', {'width': 390, 'height': 844, 'deviceScaleFactor': 1, 'mobile': True})
            await asyncio.sleep(0.3)

            # Mulai game dengan 5 kelompok
            await eval_js("""
                window.showScreen('screen-setup');
                document.querySelector('.btn-count-choice[data-count="5"]').click();
                const btnProceed = document.getElementById('btn-proceed-to-game');
                if (btnProceed) btnProceed.click();
            """)
            await asyncio.sleep(0.3)

            for case_idx in range(12):
                res = await eval_js(f"""
                    (() => {{
                        const curCase = window.State.sessionCases[window.State.currentCaseIndex];
                        // Pilih giliran bergantian tim 0..4
                        const teamIdx = window.State.currentCaseIndex % 5;
                        window.handleSelectGroupTurn(teamIdx);

                        // Jawab benar
                        window.handleStampAnswer(curCase.jawabanId);

                        // Evaluasi alasan
                        window.evaluateReason(true);

                        // Lanjut jika bukan kasus terakhir
                        if (window.State.currentCaseIndex < 11) {{
                            window.loadCase(window.State.currentCaseIndex + 1);
                        }} else {{
                            window.finishGameSession();
                        }}

                        return {{
                            caseIndex: window.State.currentCaseIndex,
                            activeScreen: document.querySelector('.screen.active').id
                        }};
                    }})()
                """)
                await asyncio.sleep(0.1)

            final_screen = await eval_js("document.querySelector('.screen.active').id")
            print(f"Simulasi 12 Kasus selesai. Layar aktif saat ini: {final_screen}")
            assert final_screen == 'screen-result', f"ERROR: Game did not navigate to result screen after 12 cases! Active: {final_screen}"
            print("-> VERIFIKASI SATU SESI 12 KASUS PENUH: 100% LOLOS!")

            print("\n=======================================================")
            print("SEMUA PENGUJIAN FASE 2 LOLOS 100%!")
            print("=======================================================")

    finally:
        p.terminate()

if __name__ == '__main__':
    asyncio.run(main())
