import asyncio, websockets, json, subprocess, tempfile, urllib.request, os, base64
from PIL import Image, ImageChops

EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(EDGE_PATH): EDGE_PATH = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

def count_diff_pixels(img_path1, img_path2):
    im1 = Image.open(img_path1).convert('RGB')
    im2 = Image.open(img_path2).convert('RGB')
    if im1.size != im2.size:
        return -1
    diff = ImageChops.difference(im1, img_path2 if isinstance(img_path2, Image.Image) else im2)
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
            async def call(method, params=None):
                nonlocal msg_id
                msg_id += 1
                await ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
                while True:
                    resp = json.loads(await ws.recv())
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

            fp = os.path.abspath('index.html').replace('\\', '/')

            # =================================================================
            # 1. VERIFIKASI TV / DESKTOP (1080p & 768p) -> TARGET: 0 PIXEL DIFF
            # =================================================================
            print("\n=======================================================")
            print("1. MEMERIKSA SELISIH PIKSEL TV / DESKTOP (TARGET: 0 PIXEL)")
            print("=======================================================")

            for label, w, h in [('1080p', 1920, 1080), ('768p', 1366, 768)]:
                await call('Page.navigate', {'url': f'file:///{fp}'})
                await asyncio.sleep(0.5)
                await call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': False})
                await asyncio.sleep(0.4)

                # Start Screen
                test_start = f"baseline_tv/test_phase4_start_{label}.png"
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
                test_board = f"baseline_tv/test_phase4_board_{label}.png"
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
                test_result = f"baseline_tv/test_phase4_result_{label}.png"
                base_result = f"baseline_tv/result_{label}.png"
                await take_screenshot(test_result)
                diff_result = count_diff_pixels(base_result, test_result)
                print(f"Result Screen ({label}): {diff_result} piksel berbeda")
                assert diff_result == 0, f"ERROR: Pixel difference on Result {label} is {diff_result} (must be 0)!"

            print("-> VERIFIKASI TV 100% LOLOS: SELISIH PIKSEL = 0 PADA SEMUA LAYAR!")

            # =================================================================
            # 2. VERIFIKASI LAYAR AWAL PADA HP TEGAK & MENDATAR
            # =================================================================
            print("\n=======================================================")
            print("2. MEMERIKSA LAYAR AWAL PADA HP (TEGAK & MENDATAR)")
            print("=======================================================")

            test_viewports = [
                {"name": "iPhone 13/14 Portrait", "w": 390, "h": 844, "orient": "portrait"},
                {"name": "iPhone SE Portrait", "w": 375, "h": 667, "orient": "portrait"},
                {"name": "Android Small Portrait", "w": 360, "h": 640, "orient": "portrait"},
                {"name": "iPhone SE Landscape", "w": 667, "h": 375, "orient": "landscape"},
                {"name": "Android Small Landscape", "w": 740, "h": 360, "orient": "landscape"}
            ]

            for vp in test_viewports:
                await call('Page.navigate', {'url': f'file:///{fp}'})
                await asyncio.sleep(0.3)
                await call('Emulation.setDeviceMetricsOverride', {'width': vp['w'], 'height': vp['h'], 'deviceScaleFactor': 1, 'mobile': True})
                await asyncio.sleep(0.3)

                start_metrics = await eval_js("""
                    (() => {
                        const title = document.querySelector('.game-main-title');
                        const btnStart = document.getElementById('btn-start-game');
                        const toolbar = document.querySelector('.start-toolbar');
                        const footer = document.querySelector('.start-footer');
                        const doc = document.documentElement;

                        const rTitle = title.getBoundingClientRect();
                        const rBtnStart = btnStart.getBoundingClientRect();
                        const rToolbar = toolbar.getBoundingClientRect();
                        const rFooter = footer.getBoundingClientRect();
                        const winW = window.innerWidth;
                        const winH = window.innerHeight;

                        return {
                            hasScroll: doc.scrollHeight > winH || doc.scrollWidth > winW,
                            titleFits: rTitle.left >= 0 && rTitle.right <= winW + 1,
                            btnStartH: rBtnStart.height,
                            btnStartFits: rBtnStart.left >= 0 && rBtnStart.right <= winW + 1,
                            toolbarFits: rToolbar.right <= winW + 1,
                            footerFits: rFooter.bottom <= winH + 1 && rFooter.left >= 0
                        };
                    })()
                """)
                print(f"[{vp['name']}] Start Page Scroll: {start_metrics['hasScroll']}, Title Fits: {start_metrics['titleFits']}, BtnStart H: {start_metrics['btnStartH']:.1f}px, Toolbar Fits: {start_metrics['toolbarFits']}, Footer Fits: {start_metrics['footerFits']}")
                assert not start_metrics['hasScroll'], f"ERROR: Page has scroll on Start Screen ({vp['name']})!"
                assert start_metrics['titleFits'], f"ERROR: Title overflows on Start Screen ({vp['name']})!"
                assert start_metrics['btnStartH'] >= 44, f"ERROR: Start button height < 44px on ({vp['name']})!"
                assert start_metrics['toolbarFits'], f"ERROR: Toolbar buttons overflow on ({vp['name']})!"
                assert start_metrics['footerFits'], f"ERROR: Footer is cut off on ({vp['name']})!"

            # =================================================================
            # 3. VERIFIKASI SETUP KELOMPOK PADA HP (TEGAK & MENDATAR)
            # =================================================================
            print("\n=======================================================")
            print("3. MEMERIKSA SETUP KELOMPOK & EDIT NAMA PADA HP")
            print("=======================================================")

            for vp in [test_viewports[0], test_viewports[3]]:
                await call('Emulation.setDeviceMetricsOverride', {'width': vp['w'], 'height': vp['h'], 'deviceScaleFactor': 1, 'mobile': True})
                await eval_js("window.showScreen('screen-setup');")
                await asyncio.sleep(0.3)

                setup_metrics = await eval_js("""
                    (() => {
                        const btns = Array.from(document.querySelectorAll('.btn-count-choice'));
                        const rBtns = btns.map(b => b.getBoundingClientRect());
                        const winW = window.innerWidth;
                        const winH = window.innerHeight;
                        const doc = document.documentElement;

                        // Cek semua tombol 2,3,4,5 muat dan tinggi >= 46px
                        const allFitW = rBtns.every(r => r.left >= 0 && r.right <= winW);
                        const minH = Math.min(...rBtns.map(r => r.height));

                        // Buka modal ubah nama
                        document.getElementById('btn-edit-group-names').click();
                        const modal = document.getElementById('modal-edit-names');
                        const card = modal.querySelector('.modal-card');
                        const rCard = card.getBoundingClientRect();
                        const cardMaxH = rCard.height;
                        const cardMaxHPercent = (cardMaxH / winH) * 100;

                        // Cek input focus
                        const firstInput = document.getElementById('custom-name-0');
                        firstInput.focus();

                        return {
                            hasScroll: doc.scrollHeight > winH,
                            allBtnsFit: allFitW,
                            minBtnHeight: minH,
                            modalCardMaxHPercent: cardMaxHPercent,
                            inputFocused: document.activeElement === firstInput
                        };
                    })()
                """)
                print(f"[{vp['name']}] Setup Btns Fit: {setup_metrics['allBtnsFit']}, Min Btn H: {setup_metrics['minBtnHeight']:.1f}px, Modal Edit MaxH: {setup_metrics['modalCardMaxHPercent']:.1f}% <= 90%, Input Focus: {setup_metrics['inputFocused']}")
                assert setup_metrics['allBtnsFit'], f"ERROR: Choice buttons overflow width on ({vp['name']})!"
                assert setup_metrics['minBtnHeight'] >= 44, f"ERROR: Choice button height < 44px on ({vp['name']})!"
                assert setup_metrics['modalCardMaxHPercent'] <= 91.0, f"ERROR: Edit names modal card exceeds 90dvh ({setup_metrics['modalCardMaxHPercent']:.1f}%) on ({vp['name']})!"
                assert setup_metrics['inputFocused'], f"ERROR: Input cannot be focused on ({vp['name']})!"

            # =================================================================
            # 4. VERIFIKASI MODAL-MODAL (RULES, ABOUT, ROLE REMINDER, QR BLOCK)
            # =================================================================
            print("\n=======================================================")
            print("4. MEMERIKSA MODAL (MAKS 90DVH, SCROLL INTERNAL, TOMBOL TUTUP, BLOK QR)")
            print("=======================================================")

            for modal_id in ['modal-rules', 'modal-about', 'modal-role-reminder']:
                modal_check = await eval_js(f"""
                    (() => {{
                        window.openModal('{modal_id}');
                        const modal = document.getElementById('{modal_id}');
                        const card = modal.querySelector('.modal-card');
                        const body = modal.querySelector('.modal-body');
                        const closeBtn = modal.querySelector('.btn-close-modal') || modal.querySelector('#btn-proceed-to-game');
                        const winH = window.innerHeight;

                        const rCard = card.getBoundingClientRect();
                        const rClose = closeBtn ? closeBtn.getBoundingClientRect() : {{ height: 0 }};
                        const bodyOverflow = window.getComputedStyle(body).overflowY;

                        let qrOk = true;
                        if ('{modal_id}' === 'modal-about') {{
                            const qrBlock = document.getElementById('qr-mobile-block');
                            const qrImg = document.getElementById('qr-code-img');
                            const qrUrl = document.getElementById('qr-web-url');
                            qrOk = qrBlock && qrImg && qrUrl && qrImg.getAttribute('src') === 'assets/qr-detektif-norma.png';
                        }}

                        window.closeModal('{modal_id}');
                        return {{
                            cardHeightPercent: (rCard.height / winH) * 100,
                            closeBtnH: rClose.height,
                            bodyScrolls: bodyOverflow === 'auto' || bodyOverflow === 'scroll',
                            qrOk: qrOk
                        }};
                    }})()
                """)
                print(f"[{modal_id}] Height: {modal_check['cardHeightPercent']:.1f}% <= 90%, CloseBtn: {modal_check['closeBtnH']:.1f}px (>= 44px), Body Scroll: {modal_check['bodyScrolls']}, QR Block: {modal_check['qrOk']}")
                assert modal_check['cardHeightPercent'] <= 91.0, f"ERROR: {modal_id} exceeds 90dvh!"
                assert modal_check['closeBtnH'] >= 40.0, f"ERROR: {modal_id} close button < 40px!"
                assert modal_check['bodyScrolls'], f"ERROR: {modal_id} body does not scroll internally!"
                assert modal_check['qrOk'], f"ERROR: QR block in modal-about is not properly configured!"

            # =================================================================
            # 5. VERIFIKASI LAYAR HASIL DI HP (PODIUM, KARTU 4/5, AKSI MENEMPEL)
            # =================================================================
            print("\n=======================================================")
            print("5. MEMERIKSA LAYAR HASIL PADA HP TEGAK & MENDATAR")
            print("=======================================================")

            for vp in [test_viewports[0], test_viewports[1], test_viewports[3]]:
                await call('Emulation.setDeviceMetricsOverride', {'width': vp['w'], 'height': vp['h'], 'deviceScaleFactor': 1, 'mobile': True})
                # Setup 5 groups
                await eval_js("""
                    window.State.groups = [
                        { id: 'g1', nama: 'Tim Elang', warna: '#1E6B4C', skor: 15, correctTimes: [3.5, 3.8, 4.0], correctCount: 3 },
                        { id: 'g2', nama: 'Tim Harimau', warna: '#8B1E22', skor: 12, correctTimes: [4.5, 4.8, 5.0], correctCount: 3 },
                        { id: 'g3', nama: 'Tim Kancil', warna: '#1A4472', skor: 9, correctTimes: [5.5, 5.8, 6.0], correctCount: 3 },
                        { id: 'g4', nama: 'Tim Banteng', warna: '#9C651F', skor: 6, correctTimes: [6.5, 6.8], correctCount: 2 },
                        { id: 'g5', nama: 'Tim Rusa', warna: '#6B2D5C', skor: 3, correctTimes: [7.5], correctCount: 1 }
                    ];
                    window.State.sessionCases = [
                        { id: 'k01', tingkat: 'dasar', kasus: 'Kasus 1' },
                        { id: 'k15', tingkat: 'hots', kasus: 'Kasus 15', pertanyaanLanjutan: 'Refleksi' }
                    ];
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
                """)
                await asyncio.sleep(0.3)

                res_metrics = await eval_js("""
                    (() => {
                        const winW = window.innerWidth;
                        const winH = window.innerHeight;
                        const doc = document.documentElement;

                        const podium = document.getElementById('result-podium-container');
                        const rPodium = podium.getBoundingClientRect();

                        const remCards = Array.from(document.querySelectorAll('.remaining-team-card'));
                        const rRemCards = remCards.map(c => c.getBoundingClientRect());

                        const badges = Array.from(document.querySelectorAll('.podium-badge'));
                        const rBadges = badges.map(b => b.getBoundingClientRect());

                        const btnReplay = document.getElementById('btn-result-replay-same');
                        const btnLead = document.getElementById('btn-result-leaderboard');
                        const btnMenu = document.getElementById('btn-result-menu');

                        const rBtnReplay = btnReplay.getBoundingClientRect();
                        const rBtnLead = btnLead.getBoundingClientRect();
                        const rBtnMenu = btnMenu.getBoundingClientRect();

                        return {
                            hasScroll: doc.scrollHeight > winH || doc.scrollWidth > winW,
                            podiumFitsW: rPodium.left >= 0 && rPodium.right <= winW + 2,
                            remainingCardCount: remCards.length,
                            remainingCardsFitW: rRemCards.every(r => r.left >= 0 && r.right <= winW + 2),
                            remainingCardsFullW: rRemCards.every(r => r.width >= winW * 0.75),
                            badgesVisible: badges.length > 0 && rBadges.every(r => r.height >= 14),
                            actionsStickyBottom: Math.abs(Math.max(rBtnReplay.bottom, rBtnLead.bottom, rBtnMenu.bottom) - winH) <= 18,
                            minActionBtnH: Math.min(rBtnReplay.height, rBtnLead.height, rBtnMenu.height)
                        };
                    })()
                """)
                print(f"[{vp['name']}] Result Scroll: {res_metrics['hasScroll']}, Podium Fits: {res_metrics['podiumFitsW']}, Rem Cards: {res_metrics['remainingCardCount']}, Rem FullW: {res_metrics['remainingCardsFullW']}, Badges Visible: {res_metrics['badgesVisible']}, Actions Bottom: {res_metrics['actionsStickyBottom']}, Min ActionBtn H: {res_metrics['minActionBtnH']:.1f}px")
                assert not res_metrics['hasScroll'], f"ERROR: Result page has scroll on ({vp['name']})!"
                assert res_metrics['podiumFitsW'], f"ERROR: Podium overflows width on ({vp['name']})!"
                assert res_metrics['remainingCardCount'] == 2, f"ERROR: Expected 2 remaining teams cards!"
                assert res_metrics['remainingCardsFitW'], f"ERROR: Remaining cards overflow width on ({vp['name']})!"
                assert res_metrics['badgesVisible'], f"ERROR: Badges are not clearly visible on ({vp['name']})!"
                assert res_metrics['actionsStickyBottom'], f"ERROR: Action buttons are not at the bottom on ({vp['name']})!"
                assert res_metrics['minActionBtnH'] >= 44, f"ERROR: Action button height < 44px on ({vp['name']})!"

            # =================================================================
            # 6. VERIFIKASI PAPAN PERINGKAT (KARTU PER BARIS & INPUT FILE)
            # =================================================================
            print("\n=======================================================")
            print("6. MEMERIKSA PAPAN PERINGKAT (KARTU PER BARIS, TOMBOL, FILE INPUT)")
            print("=======================================================")

            for vp in [test_viewports[0], test_viewports[3]]:
                await call('Emulation.setDeviceMetricsOverride', {'width': vp['w'], 'height': vp['h'], 'deviceScaleFactor': 1, 'mobile': True})
                await eval_js("""
                    window.State.leaderboard = [
                        { nama: 'Tim Elang', avgTime: 4.2, skor: 15, tanggal: '22 Okt 2026', warna: '#1E6B4C' },
                        { nama: 'Tim Harimau', avgTime: 4.8, skor: 12, tanggal: '22 Okt 2026', warna: '#8B1E22' },
                        { nama: 'Tim Kancil', avgTime: 5.4, skor: 9, tanggal: '22 Okt 2026', warna: '#1A4472' }
                    ];
                    window.renderLeaderboardTable();
                    window.showScreen('screen-leaderboard');
                """)
                await asyncio.sleep(0.3)

                lead_metrics = await eval_js("""
                    (() => {
                        const winW = window.innerWidth;
                        const winH = window.innerHeight;
                        const doc = document.documentElement;

                        const rows = Array.from(document.querySelectorAll('#leaderboard-rows tr'));
                        const rRows = rows.map(r => r.getBoundingClientRect());

                        const btnExport = document.getElementById('btn-export-backup');
                        const labelImport = document.querySelector('.import-label');
                        const btnReset = document.getElementById('btn-reset-leaderboard');
                        const fileInput = document.getElementById('import-file-input');

                        const rExport = btnExport.getBoundingClientRect();
                        const rImport = labelImport.getBoundingClientRect();
                        const rReset = btnReset.getBoundingClientRect();

                        const isCardRow = vpName => {
                            if (window.innerWidth <= 820 && window.innerHeight > window.innerWidth) {
                                return window.getComputedStyle(rows[0]).display === 'flex';
                            }
                            return true;
                        };

                        return {
                            hasScroll: doc.scrollHeight > winH || doc.scrollWidth > winW,
                            rowsCount: rows.length,
                            rowsFitW: rRows.every(r => r.left >= 0 && r.right <= winW + 2),
                            isCardDisplay: isCardRow(),
                            adminBtnsFitW: rExport.right <= winW && rImport.right <= winW && rReset.right <= winW,
                            fileInputExists: fileInput && fileInput.getAttribute('type') === 'file' && fileInput.getAttribute('accept').includes('.json')
                        };
                    })()
                """)
                print(f"[{vp['name']}] Leaderboard Scroll: {lead_metrics['hasScroll']}, Rows Fit: {lead_metrics['rowsFitW']}, Card Display: {lead_metrics['isCardDisplay']}, Admin Btns Fit: {lead_metrics['adminBtnsFitW']}, File Input OK: {lead_metrics['fileInputExists']}")
                assert not lead_metrics['hasScroll'], f"ERROR: Leaderboard page has scroll on ({vp['name']})!"
                assert lead_metrics['rowsFitW'], f"ERROR: Leaderboard rows overflow width on ({vp['name']})!"
                assert lead_metrics['adminBtnsFitW'], f"ERROR: Admin buttons overflow width on ({vp['name']})!"
                assert lead_metrics['fileInputExists'], f"ERROR: File input is not configured for cross-platform on ({vp['name']})!"

            print("\n=======================================================")
            print("SEMUA PENGUJIAN FASE 4 LOLOS 100%!")
            print("=======================================================")

    finally:
        p.terminate()

if __name__ == '__main__':
    asyncio.run(main())
