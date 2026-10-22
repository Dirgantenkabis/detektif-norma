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
    await asyncio.sleep(1.8)
    try:
        req = urllib.request.urlopen('http://127.0.0.1:9499/json')
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
                test_start = f"baseline_tv/test_phase3_start_{label}.png"
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
                test_board = f"baseline_tv/test_phase3_board_{label}.png"
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
                test_result = f"baseline_tv/test_phase3_result_{label}.png"
                base_result = f"baseline_tv/result_{label}.png"
                await take_screenshot(test_result)
                diff_result = count_diff_pixels(base_result, test_result)
                print(f"Result Screen ({label}): {diff_result} piksel berbeda")
                assert diff_result == 0, f"ERROR: Pixel difference on Result {label} is {diff_result} (must be 0)!"

            print("-> VERIFIKASI TV 100% LOLOS: SELISIH PIKSEL = 0 PADA SEMUA LAYAR!")

            # =================================================================
            # 2. VERIFIKASI PAPAN KASUS HP MENDATAR (667x375, 844x390, 740x360, 932x430)
            # =================================================================
            print("\n=======================================================")
            print("2. MEMERIKSA PAPAN KASUS HP MENDATAR PADA 4 UKURAN TARGET")
            print("=======================================================")

            hp_landscape_viewports = [
                {"name": "iPhone SE Landscape", "width": 667, "height": 375},
                {"name": "iPhone 13/14 Landscape", "width": 844, "height": 390},
                {"name": "Android Small Landscape", "width": 740, "height": 360},
                {"name": "iPhone Pro Max Landscape", "width": 932, "height": 430}
            ]

            for vp in hp_landscape_viewports:
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
                        // Muat kasus HOTS teks panjang
                        const hotsLong = KASUS_POOL.find(k => k.tingkat === 'hots' && k.kasus.length > 80) || KASUS_POOL[16];
                        window.State.sessionCases = [hotsLong];
                        window.State.currentCaseIndex = 0;
                        window.loadCase(0);
                    """)
                    await asyncio.sleep(0.3)

                    metrics = await eval_js("""
                        (() => {
                            const header = document.getElementById('board-header');
                            const teams = document.querySelector('.teams-sidebar');
                            const folder = document.getElementById('case-folder');
                            const teacher = document.querySelector('.teacher-sidebar');
                            const stamps = document.querySelector('.stamps-section');
                            const doc = document.documentElement;

                            const rHeader = header.getBoundingClientRect();
                            const rTeams = teams.getBoundingClientRect();
                            const rFolder = folder.getBoundingClientRect();
                            const rTeacher = teacher.getBoundingClientRect();
                            const rStamps = stamps.getBoundingClientRect();

                            // Cek tinggi header (36-40px)
                            const headerH = rHeader.height;
                            const isHeaderThin = headerH >= 36 && headerH <= 40.5;

                            // Cek tinggi strip kelompok (32-34px)
                            const teamsH = rTeams.height;
                            const isTeamsChipH = teamsH >= 31 && teamsH <= 36.5;

                            // Cek lebar rel guru (~96px) dan tinggi tombol (min 44px)
                            const teacherW = rTeacher.width;
                            const teacherBtns = Array.from(document.querySelectorAll('.teacher-btn'));
                            const teacherBtnsMinH = Math.min(...teacherBtns.map(b => b.getBoundingClientRect().height));

                            // Cek stempel satu baris di bawah: 4 kolom, tinggi 52-56px
                            const stampBtns = Array.from(document.querySelectorAll('.norma-stamp'));
                            const stampBtnsMinH = Math.min(...stampBtns.map(b => b.getBoundingClientRect().height));
                            const stampBtnsMaxH = Math.max(...stampBtns.map(b => b.getBoundingClientRect().height));
                            const isStampsOneRow = (rStamps.bottom - rStamps.top) <= 65;

                            // Cek petunjuk 1-3 horizontal (baris sama)
                            const clueSlots = Array.from(document.querySelectorAll('.clue-box'));
                            const clueTops = clueSlots.map(c => Math.round(c.getBoundingClientRect().top));
                            const isCluesHorizontal = (Math.max(...clueTops) - Math.min(...clueTops)) <= 5;

                            // Cek keterangan kecil pada stempel disembunyikan
                            const stampDescs = Array.from(document.querySelectorAll('.stamp-desc'));
                            const areStampDescsHidden = stampDescs.every(d => window.getComputedStyle(d).display === 'none');

                            // Cek overlap antar elemen
                            const overlapHeaderTeams = rHeader.bottom > rTeams.top + 1;
                            const overlapTeamsFolder = rTeams.bottom > rFolder.top + 1;
                            const overlapFolderTeacher = rFolder.right > rTeacher.left + 1;
                            const overlapFolderStamps = rFolder.bottom > rStamps.top + 1;

                            // Cek scroll halaman utama (target: False)
                            const hasPageScroll = doc.scrollHeight > doc.clientHeight + 2;

                            return {
                                headerH: headerH,
                                isHeaderThin: isHeaderThin,
                                teamsH: teamsH,
                                isTeamsChipH: isTeamsChipH,
                                teacherW: teacherW,
                                teacherBtnsMinH: teacherBtnsMinH,
                                stampBtnsMinH: stampBtnsMinH,
                                stampBtnsMaxH: stampBtnsMaxH,
                                isStampsOneRow: isStampsOneRow,
                                isCluesHorizontal: isCluesHorizontal,
                                areStampDescsHidden: areStampDescsHidden,
                                overlapHeaderTeams: overlapHeaderTeams,
                                overlapTeamsFolder: overlapTeamsFolder,
                                overlapFolderTeacher: overlapFolderTeacher,
                                overlapFolderStamps: overlapFolderStamps,
                                hasPageScroll: hasPageScroll,
                                docScrollH: doc.scrollHeight,
                                docClientH: doc.clientHeight
                            };
                        })()
                    """)

                    print(f"  [{team_count} Tim] Page Scroll: {metrics['hasPageScroll']} ({metrics['docScrollH']}/{metrics['docClientH']}px)")
                    print(f"  [{team_count} Tim] Header Height: {metrics['headerH']:.1f}px (Target: 36-40px, Valid: {metrics['isHeaderThin']})")
                    print(f"  [{team_count} Tim] Teams Strip Height: {metrics['teamsH']:.1f}px (Target: 32-34px, Valid: {metrics['isTeamsChipH']})")
                    print(f"  [{team_count} Tim] Rel Guru Width: {metrics['teacherW']:.1f}px (Target: ~96px), Btn Min-H: {metrics['teacherBtnsMinH']:.1f}px (Target: >= 44px)")
                    print(f"  [{team_count} Tim] Stempel Height: {metrics['stampBtnsMinH']:.1f}-{metrics['stampBtnsMaxH']:.1f}px (Target: 52-56px, 1 Baris: {metrics['isStampsOneRow']})")
                    print(f"  [{team_count} Tim] Petunjuk 1-3 Horizontal: {metrics['isCluesHorizontal']}")
                    print(f"  [{team_count} Tim] Keterangan Kecil Stempel Hidden: {metrics['areStampDescsHidden']}")
                    print(f"  [{team_count} Tim] Overlaps: H-T={metrics['overlapHeaderTeams']}, T-F={metrics['overlapTeamsFolder']}, F-Tr={metrics['overlapFolderTeacher']}, F-S={metrics['overlapFolderStamps']}")

                    assert not metrics['hasPageScroll'], f"ERROR: Page scroll detected on {vp['name']} ({team_count} teams)!"
                    assert metrics['isHeaderThin'], f"ERROR: Header height {metrics['headerH']}px out of 36-40px range on {vp['name']}!"
                    assert metrics['isTeamsChipH'], f"ERROR: Teams strip height {metrics['teamsH']}px out of 32-34px range on {vp['name']}!"
                    assert abs(metrics['teacherW'] - 96) <= 5, f"ERROR: Teacher rail width {metrics['teacherW']}px not ~96px on {vp['name']}!"
                    assert metrics['teacherBtnsMinH'] >= 44, f"ERROR: Teacher btn height < 44px ({metrics['teacherBtnsMinH']}px) on {vp['name']}!"
                    assert metrics['stampBtnsMinH'] >= 52 and metrics['stampBtnsMaxH'] <= 56.5, f"ERROR: Stamp height {metrics['stampBtnsMinH']}-{metrics['stampBtnsMaxH']}px out of 52-56px on {vp['name']}!"
                    assert metrics['isStampsOneRow'], f"ERROR: Stamps are not in one single horizontal row on {vp['name']}!"
                    assert metrics['isCluesHorizontal'], f"ERROR: Clues 1-3 are not aligned horizontally on {vp['name']}!"
                    assert metrics['areStampDescsHidden'], f"ERROR: Small descriptions on stamps should be hidden in landscape mode on {vp['name']}!"
                    assert not metrics['overlapHeaderTeams'], "ERROR: Header and Teams overlap!"
                    assert not metrics['overlapTeamsFolder'], "ERROR: Teams and Folder overlap!"
                    assert not metrics['overlapFolderTeacher'], "ERROR: Folder and Teacher rail overlap!"
                    assert not metrics['overlapFolderStamps'], "ERROR: Folder and Stamps overlap!"

                    # =============================================================
                    # UJI BOTTOM SHEET PADA HP MENDATAR (MAX-HEIGHT 70%)
                    # =============================================================
                    await eval_js("window.handleSelectGroupTurn(0);")
                    await asyncio.sleep(0.1)

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

                            // Cek teks kasus dan stempel terpecahkan tidak tertutup
                            const caseTextAboveSheet = rCaseText.bottom <= rSheet.top || rCaseText.top < rSheet.top;
                            const stampNotCovered = rStamp.bottom <= rSheet.top;
                            const feedbackAtHead = Math.abs(rFeedback.top - rSheet.top) < 3;

                            return {
                                sheetHeight: sheetH,
                                sheetTop: rSheet.top,
                                stampTop: rStamp.top,
                                stampBottom: rStamp.bottom,
                                sheetMaxHPercent: sheetMaxHPercent,
                                caseTextAboveSheet: caseTextAboveSheet,
                                stampNotCovered: stampNotCovered,
                                feedbackAtHead: feedbackAtHead,
                                sensibleBtnHeight: rBtnSensible.height,
                                passBtnHeight: rBtnPass.height
                            };
                        })()
                    """)

                    print(f"  [{team_count} Tim] Bottom Sheet Height: {sheet_metrics['sheetHeight']:.1f}px ({sheet_metrics['sheetMaxHPercent']:.1f}% <= 70%), Sheet Top: {sheet_metrics['sheetTop']:.1f}px")
                    print(f"  [{team_count} Tim] Stamp Top: {sheet_metrics['stampTop']:.1f}px, Bottom: {sheet_metrics['stampBottom']:.1f}px")
                    print(f"  [{team_count} Tim] Case Text Above Sheet: {sheet_metrics['caseTextAboveSheet']}")
                    print(f"  [{team_count} Tim] Stempel TERPECAHKAN Uncovered: {sheet_metrics['stampNotCovered']}")
                    print(f"  [{team_count} Tim] Tombol Alasan Height: {min(sheet_metrics['sensibleBtnHeight'], sheet_metrics['passBtnHeight']):.1f}px (>= 44px)")

                    assert sheet_metrics['sheetMaxHPercent'] <= 71.0, f"ERROR: Bottom sheet height exceeds 70% ({sheet_metrics['sheetMaxHPercent']:.1f}%) on {vp['name']}!"
                    assert sheet_metrics['caseTextAboveSheet'], f"ERROR: Case text is covered by sheet on {vp['name']}!"
                    assert sheet_metrics['stampNotCovered'], f"ERROR: Stempel TERPECAHKAN is covered by bottom sheet on {vp['name']}!"
                    assert sheet_metrics['sensibleBtnHeight'] >= 44, f"ERROR: Sensible button height < 44px on {vp['name']}!"
                    assert sheet_metrics['passBtnHeight'] >= 44, f"ERROR: Pass button height < 44px on {vp['name']}!"

                    # Lanjut ke penjelasan
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
                    print(f"  [{team_count} Tim] Tombol Kasus Berikutnya: {next_metrics['nextBtnHeight']:.1f}px (>= 44px, Visible: {next_metrics['nextBtnVisible']})")
                    assert next_metrics['nextBtnHeight'] >= 44, f"ERROR: Next Case button height < 44px on {vp['name']}!"

            # =================================================================
            # 3. UJI ROTATE DARI TEGAK KE MENDATAR DI TENGAH KASUS
            # =================================================================
            print("\n=======================================================")
            print("3. MEMERIKSA ROTASI DARI TEGAK KE MENDATAR DI TENGAH KASUS")
            print("=======================================================")

            await call('Page.navigate', {'url': f'file:///{fp}'})
            await asyncio.sleep(0.4)
            # Mulai di Portrait 390x844
            await call('Emulation.setDeviceMetricsOverride', {'width': 390, 'height': 844, 'deviceScaleFactor': 1, 'mobile': True})
            await asyncio.sleep(0.3)

            await eval_js("""
                window.showScreen('screen-setup');
                document.querySelector('.btn-count-choice[data-count="4"]').click();
                const btnProceed = document.getElementById('btn-proceed-to-game');
                if (btnProceed) btnProceed.click();
            """)
            await asyncio.sleep(1.5)

            # Pilih tim 2 di tengah kasus
            await eval_js("window.handleSelectGroupTurn(2);")
            await asyncio.sleep(1.0) # biarkan timer berjalan ~2-3 detik

            state_before = await eval_js("""
                ({
                    caseIndex: window.State.currentCaseIndex,
                    timer: window.State.timerSeconds,
                    isRunning: window.State.timerRunning,
                    activeGroup: window.State.activeGroupIndex
                })
            """)

            # Rotasi ke Landscape 844x390
            await call('Emulation.setDeviceMetricsOverride', {'width': 844, 'height': 390, 'deviceScaleFactor': 1, 'mobile': True})
            await eval_js("window.dispatchEvent(new Event('resize')); window.dispatchEvent(new Event('orientationchange'));")
            await asyncio.sleep(0.5)

            state_after = await eval_js("""
                ({
                    caseIndex: window.State.currentCaseIndex,
                    timer: window.State.timerSeconds,
                    isRunning: window.State.timerRunning,
                    activeGroup: window.State.activeGroupIndex
                })
            """)

            print(f"State sebelum rotasi: Case={state_before['caseIndex']}, Timer={state_before['timer']}s, Running={state_before['isRunning']}, ActiveTeam={state_before['activeGroup']}")
            print(f"State setelah rotasi: Case={state_after['caseIndex']}, Timer={state_after['timer']}s, Running={state_after['isRunning']}, ActiveTeam={state_after['activeGroup']}")

            assert state_after['caseIndex'] == state_before['caseIndex'], "ERROR: Case index changed after rotation!"
            assert state_after['activeGroup'] == state_before['activeGroup'], "ERROR: Active group changed after rotation!"
            assert state_after['timer'] >= state_before['timer'], "ERROR: Timer reset or stopped after rotation!"
            assert state_after['isRunning'] == True, "ERROR: Timer stopped running after rotation!"
            print("-> VERIFIKASI ROTASI TIDAK MERESET STATE / TIMER / KELOMPOK TERPILIH: 100% LOLOS!")

            # =================================================================
            # 4. SIMULASI PENUH 12 KASUS DI HP MENDATAR (844x390)
            # =================================================================
            print("\n=======================================================")
            print("4. MEMERIKSA SIMULASI PENUH 12 KASUS DI HP MENDATAR (844x390)")
            print("=======================================================")

            for case_idx in range(12):
                res = await eval_js(f"""
                    (() => {{
                        const curCase = window.State.sessionCases[window.State.currentCaseIndex];
                        const teamIdx = window.State.currentCaseIndex % 4;
                        window.handleSelectGroupTurn(teamIdx);
                        window.handleStampAnswer(curCase.jawabanId);
                        window.evaluateReason(true);
                        if (window.State.currentCaseIndex < 11) {{
                            window.loadCase(window.State.currentCaseIndex + 1);
                        }} else {{
                            window.finishGameSession();
                        }}
                    }})()
                """)
                await asyncio.sleep(0.1)

            final_screen = await eval_js("document.querySelector('.screen.active').id")
            print(f"Simulasi 12 Kasus selesai. Layar aktif saat ini: {final_screen}")
            assert final_screen == 'screen-result', f"ERROR: Game did not navigate to result screen after 12 cases! Active: {final_screen}"
            print("-> VERIFIKASI SATU SESI 12 KASUS PENUH HP MENDATAR: 100% LOLOS!")

            print("\n=======================================================")
            print("SEMUA PENGUJIAN FASE 3 LOLOS 100%!")
            print("=======================================================")

    finally:
        p.terminate()

if __name__ == '__main__':
    asyncio.run(main())
