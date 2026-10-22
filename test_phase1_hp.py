import asyncio, websockets, json, subprocess, tempfile, urllib.request, os, base64
from PIL import Image, ImageChops

EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(EDGE_PATH): EDGE_PATH = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

def count_diff_pixels(img_path1, img_path2):
    im1 = Image.open(img_path1).convert('RGB')
    im2 = Image.open(img_path2).convert('RGB')
    if im1.size != im2.size:
        return -1 # Different dimensions
    diff = ImageChops.difference(im1, im2)
    bbox = diff.getbbox()
    if not bbox:
        return 0
    # Hitung jumlah pixel yang berbeda
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
        '--remote-debugging-port=9477',
        f'--user-data-dir={tmp}',
        '--disable-extensions',
        '--disable-gpu',
        '--no-sandbox'
    ])
    await asyncio.sleep(1.8)
    try:
        req = urllib.request.urlopen('http://127.0.0.1:9477/json')
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

            total_tv_diff = 0

            for label, w, h in tv_tests:
                await call('Page.navigate', {'url': f'file:///{fp}'})
                await asyncio.sleep(0.5)
                await call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': False})
                await asyncio.sleep(0.3)

                # Check Start Screen
                test_start = f"baseline_tv/test_start_{label}.png"
                base_start = f"baseline_tv/start_{label}.png"
                await take_screenshot(test_start)
                diff_start = count_diff_pixels(base_start, test_start)
                print(f"Start Screen ({label}): {diff_start} piksel berbeda")
                assert diff_start == 0, f"ERROR: Pixel difference on Start {label} is {diff_start} (must be 0)!"

                # Check Board Screen
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
                test_board = f"baseline_tv/test_board_{label}.png"
                base_board = f"baseline_tv/board_{label}.png"
                await take_screenshot(test_board)
                diff_board = count_diff_pixels(base_board, test_board)
                print(f"Board Screen ({label}): {diff_board} piksel berbeda")
                assert diff_board == 0, f"ERROR: Pixel difference on Board {label} is {diff_board} (must be 0)!"

                # Check Result Screen
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
                test_result = f"baseline_tv/test_result_{label}.png"
                base_result = f"baseline_tv/result_{label}.png"
                await take_screenshot(test_result)
                diff_result = count_diff_pixels(base_result, test_result)
                print(f"Result Screen ({label}): {diff_result} piksel berbeda")
                assert diff_result == 0, f"ERROR: Pixel difference on Result {label} is {diff_result} (must be 0)!"

            print("-> VERIFIKASI TV 100% LOLOS: SELISIH PIKSEL = 0 PADA SEMUA LAYAR!")

            # =================================================================
            # 2. VERIFIKASI MODE HP: BEBAS SCROLL HALAMAN PADA 4 UKURAN UJI
            # =================================================================
            print("\n=======================================================")
            print("2. MEMERIKSA SCROLL HALAMAN PADA 4 UKURAN MOBILE (TARGET: 0 SCROLL)")
            print("=======================================================")

            mobile_viewports = [
                {"name": "iPhone SE Portrait", "width": 375, "height": 667},
                {"name": "iPhone 13/14 Portrait", "width": 390, "height": 844},
                {"name": "iPhone SE Landscape", "width": 667, "height": 375},
                {"name": "iPhone 13/14 Landscape", "width": 844, "height": 390}
            ]

            for vp in mobile_viewports:
                w, h = vp["width"], vp["height"]
                await call('Page.navigate', {'url': f'file:///{fp}'})
                await asyncio.sleep(0.5)
                await call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': True})
                await asyncio.sleep(0.3)

                scroll_data = await eval_js("""
                    (() => {
                        const app = document.getElementById('app-viewport');
                        const body = document.body;
                        const doc = document.documentElement;

                        // Periksa scroll di Layar Awal
                        const hasStartScroll = doc.scrollHeight > doc.clientHeight || body.scrollHeight > body.clientHeight;

                        // Pindah ke Layar Board
                        window.showScreen('screen-setup');
                        document.querySelector('.btn-count-choice[data-count="4"]').click();
                        const btnProceed = document.getElementById('btn-proceed-to-game');
                        if (btnProceed) btnProceed.click();

                        const hasBoardScroll = doc.scrollHeight > doc.clientHeight || body.scrollHeight > body.clientHeight;

                        // Pindah ke Layar Hasil
                        window.State.groups = [
                            { id: 'g1', nama: 'Tim Elang', warna: '#1E6B4C', skor: 15, correctTimes: [4.0, 4.2, 4.4], correctCount: 3 },
                            { id: 'g2', nama: 'Tim Harimau', warna: '#8B1E22', skor: 12, correctTimes: [5.0, 5.2, 5.4], correctCount: 3 }
                        ];
                        window.State.sessionCases = [{ id: 'k01', tingkat: 'dasar', kasus: 'Kasus 1' }];
                        window.State.currentCaseIndex = 0;
                        window.State.unsolvedCases = [];
                        window.renderResultScreen();
                        window.showScreen('screen-result');

                        const hasResultScroll = doc.scrollHeight > doc.clientHeight || body.scrollHeight > body.clientHeight;

                        const appStyle = window.getComputedStyle(app);

                        return {
                            hasStartScroll: hasStartScroll,
                            hasBoardScroll: hasBoardScroll,
                            hasResultScroll: hasResultScroll,
                            docScrollH: doc.scrollHeight,
                            docClientH: doc.clientHeight,
                            appPosition: appStyle.position,
                            appWidth: app.getBoundingClientRect().width,
                            appHeight: app.getBoundingClientRect().height,
                            windowW: window.innerWidth,
                            windowH: window.innerHeight
                        };
                    })()
                """)

                print(f"{vp['name']} ({w}x{h}):")
                print(f"  App Viewport: position={scroll_data['appPosition']}, size={scroll_data['appWidth']}x{scroll_data['appHeight']} (Window: {scroll_data['windowW']}x{scroll_data['windowH']})")
                print(f"  Page Scroll: Start={scroll_data['hasStartScroll']}, Board={scroll_data['hasBoardScroll']}, Result={scroll_data['hasResultScroll']}")

                assert scroll_data['appPosition'] == 'fixed', f"ERROR: app-viewport is not position fixed on {vp['name']}!"
                assert not scroll_data['hasStartScroll'], f"ERROR: Start screen has page scroll on {vp['name']}!"
                assert not scroll_data['hasBoardScroll'], f"ERROR: Board screen has page scroll on {vp['name']}!"
                assert not scroll_data['hasResultScroll'], f"ERROR: Result screen has page scroll on {vp['name']}!"

            print("-> VERIFIKASI MOBILE BEBAS SCROLL HALAMAN: 100% LOLOS!")

            # =================================================================
            # 3. VERIFIKASI RESIZE / ROTATE TIDAK MERESET STATE / TIMER
            # =================================================================
            print("\n=======================================================")
            print("3. MEMERIKSA RESIZE / ROTASI TIDAK MERESET TIMER / STATE")
            print("=======================================================")

            await call('Page.navigate', {'url': f'file:///{fp}'})
            await asyncio.sleep(0.5)
            await call('Emulation.setDeviceMetricsOverride', {'width': 390, 'height': 844, 'deviceScaleFactor': 1, 'mobile': True})
            await asyncio.sleep(0.3)

            # Mulai game dan jalankan timer beberapa detik
            await eval_js("""
                window.showScreen('screen-setup');
                document.querySelector('.btn-count-choice[data-count="4"]').click();
                const btnProceed = document.getElementById('btn-proceed-to-game');
                if (btnProceed) btnProceed.click();
            """)
            await asyncio.sleep(2.5) # Tunggu timer berjalan ~2-3 detik

            state_before = await eval_js("""
                ({
                    caseIndex: window.State.currentCaseIndex,
                    timer: window.State.timerSeconds,
                    isRunning: window.State.timerRunning,
                    activeGroup: window.State.activeGroupIndex
                })
            """)

            # Simulasikan rotasi ke Landscape 844x390
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

            print(f"State sebelum rotasi: Case={state_before['caseIndex']}, Timer={state_before['timer']}s, Running={state_before['isRunning']}")
            print(f"State setelah rotasi: Case={state_after['caseIndex']}, Timer={state_after['timer']}s, Running={state_after['isRunning']}")

            assert state_after['caseIndex'] == state_before['caseIndex'], "ERROR: Case index changed after rotation!"
            assert state_after['timer'] >= state_before['timer'], "ERROR: Timer reset or stopped after rotation!"
            assert state_after['isRunning'] == True, "ERROR: Timer stopped running after rotation!"
            print("-> VERIFIKASI ROTASI TIDAK MERESET TIMER/STATE: 100% LOLOS!")

            print("\n=======================================================")
            print("SEMUA PENGUJIAN FASE 1 LOLOS 100%!")
            print("=======================================================")

    finally:
        p.terminate()

if __name__ == '__main__':
    asyncio.run(main())
