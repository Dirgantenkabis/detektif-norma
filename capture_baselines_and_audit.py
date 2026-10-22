import asyncio, websockets, json, subprocess, tempfile, urllib.request, os, base64

EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(EDGE_PATH): EDGE_PATH = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

async def main():
    tmp = tempfile.mkdtemp()
    p = subprocess.Popen([
        EDGE_PATH,
        '--headless=new',
        '--remote-debugging-port=9455',
        f'--user-data-dir={tmp}',
        '--disable-extensions',
        '--disable-gpu',
        '--no-sandbox'
    ])
    await asyncio.sleep(1.8)
    try:
        req = urllib.request.urlopen('http://127.0.0.1:9455/json')
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
                print(f"Captured: {filename}")

            await call('Page.enable')
            await call('Runtime.enable')
            fp = os.path.abspath('index.html').replace('\\', '/')

            # =================================================================
            # 1. CAPTURE TV BASELINES (1920x1080 and 1366x768)
            # =================================================================
            tv_resolutions = [
                (1920, 1080, "1080p"),
                (1366, 768, "768p")
            ]

            for w, h, label in tv_resolutions:
                await call('Page.navigate', {'url': f'file:///{fp}'})
                await asyncio.sleep(0.5)
                await call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': False})
                await asyncio.sleep(0.3)

                # Baseline Start Screen
                await take_screenshot(f"baseline_tv/start_{label}.png")

                # Baseline Board Screen (kasus 1)
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
                await take_screenshot(f"baseline_tv/board_{label}.png")

                # Baseline Result Screen
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
                await take_screenshot(f"baseline_tv/result_{label}.png")

            print("\nTV Baselines captured successfully.")

            # =================================================================
            # 2. AUDIT MOBILE VIEWPORTS BEFORE ANY CODE CHANGES
            # =================================================================
            mobile_viewports = [
                {"name": "iPhone SE Portrait", "width": 375, "height": 667, "mode": "hp-tegak"},
                {"name": "iPhone 13/14 Portrait", "width": 390, "height": 844, "mode": "hp-tegak"},
                {"name": "iPhone SE Landscape", "width": 667, "height": 375, "mode": "hp-mendatar"},
                {"name": "iPhone 13/14 Landscape", "width": 844, "height": 390, "mode": "hp-mendatar"}
            ]

            audit_results = {}

            for vp in mobile_viewports:
                w, h = vp["width"], vp["height"]
                print(f"\n=======================================================")
                print(f"AUDITING {vp['name']} ({w}x{h})")
                print(f"=======================================================")

                await call('Page.navigate', {'url': f'file:///{fp}'})
                await asyncio.sleep(0.5)
                await call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': True})
                await asyncio.sleep(0.3)

                # Check on Board Screen with HOTS case
                audit_data = await eval_js("""
                    (() => {
                        const app = document.getElementById('app-viewport');
                        const body = document.body;
                        const appRect = app.getBoundingClientRect();

                        // Jalankan game ke kasus HOTS k12
                        window.showScreen('screen-setup');
                        document.querySelector('.btn-count-choice[data-count="4"]').click();
                        const btnProceed = document.getElementById('btn-proceed-to-game');
                        if (btnProceed) btnProceed.click();

                        // Force load HOTS case k12
                        const hotsCase = (typeof KASUS_POOL !== 'undefined' ? KASUS_POOL : window.State.sessionCases).find(k => k.id === 'k12');
                        if (hotsCase) {
                            window.State.sessionCases[0] = JSON.parse(JSON.stringify(hotsCase));
                            window.loadCase(0);
                        }

                        // Jawab benar untuk trigger alasan lisan HOTS
                        const teamCard = document.querySelector('.team-card[data-index="0"]');
                        if (teamCard) teamCard.click();
                        // Klik stempel kesusilaan
                        const stamp = document.querySelector('.norma-stamp[data-norma="kesusilaan"]');
                        if (stamp) stamp.click();

                        // Kumpulkan elemen interaktif (tombol, input, stempel)
                        const interactiveElements = Array.from(document.querySelectorAll('button, .norma-stamp, .team-card, a')).filter(el => {
                            const rect = el.getBoundingClientRect();
                            return rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).display !== 'none';
                        });

                        const smallTouchTargets = interactiveElements.map(el => {
                            const r = el.getBoundingClientRect();
                            return {
                                tag: el.tagName,
                                id: el.id || el.className,
                                text: el.textContent.trim().slice(0, 25),
                                width: Math.round(r.width),
                                height: Math.round(r.height),
                                top: Math.round(r.top),
                                left: Math.round(r.left)
                            };
                        }).filter(item => item.width < 44 || item.height < 44);

                        // Kumpulkan teks teks dengan font-size < 14px
                        const allTextNodes = Array.from(document.querySelectorAll('p, span, h1, h2, h3, h4, div, strong, button')).filter(el => {
                            if (el.children.length > 0 && Array.from(el.children).some(c => c.textContent.trim() === el.textContent.trim())) return false;
                            const text = el.textContent.trim();
                            if (!text) return false;
                            const rect = el.getBoundingClientRect();
                            return rect.width > 0 && rect.height > 0;
                        });

                        const smallFonts = allTextNodes.map(el => {
                            const fs = parseFloat(window.getComputedStyle(el).fontSize);
                            return {
                                text: el.textContent.trim().slice(0, 30),
                                fontSize: fs,
                                id: el.id || el.className
                            };
                        }).filter(item => item.fontSize < 14);

                        // Cek collision antara reason panel dengan clues / clue box
                        const cluesBox = document.querySelector('.case-clues-section') || document.querySelector('.clues-container') || document.querySelector('.case-clue-slots');
                        const hotsBox = document.getElementById('hots-question-box');
                        const reasonActions = document.getElementById('teacher-reason-actions');
                        const cluesRect = cluesBox ? cluesBox.getBoundingClientRect() : null;
                        const hotsRect = hotsBox ? hotsBox.getBoundingClientRect() : null;
                        const reasonRect = reasonActions ? reasonActions.getBoundingClientRect() : null;

                        let collisionDetected = false;
                        if (cluesRect && hotsRect && window.getComputedStyle(hotsBox).display !== 'none') {
                            collisionDetected = (cluesRect.bottom > hotsRect.top);
                        }

                        // Cek viewport ratio squeeze
                        const viewportSqueeze = {
                            windowWidth: window.innerWidth,
                            windowHeight: window.innerHeight,
                            appWidth: Math.round(appRect.width),
                            appHeight: Math.round(appRect.height),
                            isLetterboxed: (appRect.width < window.innerWidth - 2 || appRect.height < window.innerHeight - 2),
                            bodyScrollHeight: document.body.scrollHeight,
                            windowHeight: window.innerHeight
                        };

                        return {
                            smallTouchTargetsCount: smallTouchTargets.length,
                            smallTouchTargetsSample: smallTouchTargets.slice(0, 8),
                            smallFontsCount: smallFonts.length,
                            smallFontsSample: smallFonts.slice(0, 8),
                            cluesBottom: cluesRect ? cluesRect.bottom : null,
                            hotsTop: hotsRect ? hotsRect.top : null,
                            collisionDetected: collisionDetected,
                            viewportSqueeze: viewportSqueeze
                        };
                    })()
                """)

                print("RAW EVAL RESULT:", type(audit_data), audit_data)
                audit_results[vp["name"]] = audit_data
                print(f"Touch targets < 44px: {audit_data.get('smallTouchTargetsCount')}")
                for s in audit_data['smallTouchTargetsSample'][:5]:
                    print(f"  - {s['id']} ({s['text']}): {s['width']}x{s['height']}px")
                print(f"Font size < 14px: {audit_data['smallFontsCount']}")
                for f in audit_data['smallFontsSample'][:5]:
                    print(f"  - {f['id']} ({f['text']}): {f['fontSize']}px")
                print(f"Collision clue/hots: {audit_data['collisionDetected']} (cluesBottom: {audit_data['cluesBottom']}, hotsTop: {audit_data['hotsTop']})")
                print(f"Viewport squeeze: App is {audit_data['viewportSqueeze']['appWidth']}x{audit_data['viewportSqueeze']['appHeight']} in window {audit_data['viewportSqueeze']['windowWidth']}x{audit_data['viewportSqueeze']['windowHeight']} (Letterboxed: {audit_data['viewportSqueeze']['isLetterboxed']})")

            # Save full audit json for reference
            with open("baseline_tv/audit_results.json", "w") as f:
                json.dump(audit_results, f, indent=2)

    finally:
        p.terminate()

if __name__ == '__main__':
    asyncio.run(main())
