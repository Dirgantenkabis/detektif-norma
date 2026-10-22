import asyncio, websockets, json, subprocess, tempfile, urllib.request, os, base64

EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(EDGE_PATH): EDGE_PATH = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

async def main():
    tmp = tempfile.mkdtemp()
    p = subprocess.Popen([
        EDGE_PATH,
        '--headless=new',
        '--remote-debugging-port=9422',
        f'--user-data-dir={tmp}',
        '--disable-extensions',
        '--disable-gpu',
        '--no-sandbox'
    ])
    await asyncio.sleep(2.0)
    try:
        req = urllib.request.urlopen('http://127.0.0.1:9422/json')
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
                return await call("Runtime.evaluate", {"expression": expression, "returnByValue": True})

            async def take_screenshot(filename):
                data = await call("Page.captureScreenshot", {"format": "png"})
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(data["data"]))
                print(f"Captured: {filename}")

            await call('Page.enable')
            await call('Runtime.enable')
            fp = os.path.abspath('index.html').replace('\\', '/')

            scenarios = [
                {
                    "name": "Scenario 1: 5 Teams, 0 Unsolved, HOTS present, 1080p",
                    "width": 1920, "height": 1080,
                    "setup_code": """
                        window.State.groups = [
                            { id: 'g1', nama: 'Tim Elang Perkasa', warna: '#1E6B4C', skor: 18, correctTimes: [4.2, 5.1, 4.8, 6.0], correctCount: 4, hotsCount: 2, reasonCount: 2 },
                            { id: 'g2', nama: 'Tim Harimau Cerdas', warna: '#8B1E22', skor: 15, correctTimes: [3.2, 3.5, 3.1], correctCount: 3, hotsCount: 1, reasonCount: 1 },
                            { id: 'g3', nama: 'Tim Kancil Gesit', warna: '#1A4472', skor: 12, correctTimes: [5.0, 4.5], correctCount: 2, hotsCount: 0, reasonCount: 1 },
                            { id: 'g4', nama: 'Tim Banteng Tangguh', warna: '#9C651F', skor: 9, correctTimes: [6.5, 7.0, 5.5], correctCount: 3, hotsCount: 1, reasonCount: 0 },
                            { id: 'g5', nama: 'Tim Rusa Bijaksana', warna: '#5B2C6F', skor: 6, correctTimes: [8.0], correctCount: 1, hotsCount: 0, reasonCount: 0 }
                        ];
                        window.State.sessionCases = [
                            { id: 'k01', tingkat: 'dasar', kasus: 'Kasus dasar 1' },
                            { id: 'k12', tingkat: 'hots', kasus: 'Kasus hots 12', pertanyaanLanjutan: 'Mengapa memfitnah teman merusak kepercayaan dalam berteman?' }
                        ];
                        window.State.currentCaseIndex = 1;
                        window.State.unsolvedCases = [];
                        window.renderResultScreen();
                        window.showScreen('screen-result');
                    """
                },
                {
                    "name": "Scenario 2: 4 Teams, Tie at #1 (Skor Sama), 2 Unsolved, 1080p",
                    "width": 1920, "height": 1080,
                    "setup_code": """
                        window.State.groups = [
                            { id: 'g1', nama: 'Tim Elang', warna: '#1E6B4C', skor: 15, correctTimes: [4.0, 4.2, 4.4], correctCount: 3 },
                            { id: 'g2', nama: 'Tim Harimau', warna: '#8B1E22', skor: 15, correctTimes: [5.0, 5.2, 5.4], correctCount: 3 },
                            { id: 'g3', nama: 'Tim Kancil', warna: '#1A4472', skor: 10, correctTimes: [6.0, 6.2, 6.4], correctCount: 3 },
                            { id: 'g4', nama: 'Tim Banteng', warna: '#9C651F', skor: 7, correctTimes: [7.0, 7.2], correctCount: 2 }
                        ];
                        window.State.sessionCases = [
                            { id: 'k01', tingkat: 'dasar', kasus: 'Kasus 1' },
                            { id: 'k15', tingkat: 'hots', kasus: 'Kasus 15', pertanyaanLanjutan: 'Bagaimana seharusnya kita bersikap jika melihat ketidakadilan di lingkungan sekitar?' }
                        ];
                        window.State.currentCaseIndex = 1;
                        window.State.unsolvedCases = [
                            { id: 'u01', kasus: 'Menyerobot antrean di kantin sekolah saat istirahat', jawabanId: 'kesopanan', penjelasan: 'Antre adalah tata krama' },
                            { id: 'u02', kasus: 'Mengambil pensil teman tanpa izin saat kelas sepi', jawabanId: 'kesusilaan', penjelasan: 'Hati nurani melarang mengambil hak orang' }
                        ];
                        window.renderResultScreen();
                        window.showScreen('screen-result');
                    """
                },
                {
                    "name": "Scenario 3: 3 Teams, Tie at #2, All < 3 answers, 1080p",
                    "width": 1920, "height": 1080,
                    "setup_code": """
                        window.State.groups = [
                            { id: 'g1', nama: 'Tim Garuda', warna: '#1E6B4C', skor: 9, correctTimes: [4.5, 5.0], correctCount: 2 },
                            { id: 'g2', nama: 'Tim Rajawali', warna: '#8B1E22', skor: 6, correctTimes: [6.0], correctCount: 1 },
                            { id: 'g3', nama: 'Tim Merak', warna: '#1A4472', skor: 6, correctTimes: [7.0], correctCount: 1 }
                        ];
                        window.State.sessionCases = [
                            { id: 'k01', tingkat: 'dasar', kasus: 'Kasus 1' }
                        ];
                        window.State.currentCaseIndex = 0;
                        window.State.unsolvedCases = [];
                        window.renderResultScreen();
                        window.showScreen('screen-result');
                    """
                },
                {
                    "name": "Scenario 4: 2 Teams, 0 HOTS, 768p (1366x768)",
                    "width": 1366, "height": 768,
                    "setup_code": """
                        window.State.groups = [
                            { id: 'g1', nama: 'Tim Alpha', warna: '#1E6B4C', skor: 12, correctTimes: [4.0, 4.5, 4.2], correctCount: 3 },
                            { id: 'g2', nama: 'Tim Beta', warna: '#8B1E22', skor: 8, correctTimes: [5.0, 5.5, 5.2], correctCount: 3 }
                        ];
                        window.State.sessionCases = [
                            { id: 'k01', tingkat: 'dasar', kasus: 'Kasus 1' },
                            { id: 'k02', tingkat: 'dasar', kasus: 'Kasus 2' }
                        ];
                        window.State.currentCaseIndex = 1;
                        window.State.unsolvedCases = [];
                        window.renderResultScreen();
                        window.showScreen('screen-result');
                    """
                },
                {
                    "name": "Scenario 5: 5 Teams, 4 Unsolved (>3 cases), 768p (1366x768)",
                    "width": 1366, "height": 768,
                    "setup_code": """
                        window.State.groups = [
                            { id: 'g1', nama: 'Tim Elang', warna: '#1E6B4C', skor: 15, correctTimes: [3.8, 4.2, 4.0], correctCount: 3 },
                            { id: 'g2', nama: 'Tim Harimau', warna: '#8B1E22', skor: 12, correctTimes: [4.5, 4.8, 4.2], correctCount: 3 },
                            { id: 'g3', nama: 'Tim Kancil', warna: '#1A4472', skor: 9, correctTimes: [5.0, 5.2, 5.1], correctCount: 3 },
                            { id: 'g4', nama: 'Tim Banteng', warna: '#9C651F', skor: 6, correctTimes: [6.0, 6.2, 6.1], correctCount: 3 },
                            { id: 'g5', nama: 'Tim Rusa', warna: '#5B2C6F', skor: 3, correctTimes: [7.0], correctCount: 1 }
                        ];
                        window.State.sessionCases = [
                            { id: 'k01', tingkat: 'dasar', kasus: 'Kasus 1' },
                            { id: 'k12', tingkat: 'hots', kasus: 'Kasus 12', pertanyaanLanjutan: 'Mengapa norma hukum memiliki sanksi yang paling tegas dibandingkan norma lainnya?' }
                        ];
                        window.State.currentCaseIndex = 1;
                        window.State.unsolvedCases = [
                            { id: 'u01', kasus: 'Kasus gagal 1', jawabanId: 'agama', penjelasan: 'P1' },
                            { id: 'u02', kasus: 'Kasus gagal 2', jawabanId: 'kesusilaan', penjelasan: 'P2' },
                            { id: 'u03', kasus: 'Kasus gagal 3', jawabanId: 'kesopanan', penjelasan: 'P3' },
                            { id: 'u04', kasus: 'Kasus gagal 4', jawabanId: 'hukum', penjelasan: 'P4' }
                        ];
                        window.renderResultScreen();
                        window.showScreen('screen-result');
                    """
                }
            ]

            for s in scenarios:
                print(f"\n=======================================================")
                print(f"RUNNING {s['name']}")
                print(f"=======================================================")
                await call('Page.navigate', {'url': f'file:///{fp}'})
                await asyncio.sleep(0.5)
                await call('Emulation.setDeviceMetricsOverride', {
                    'width': s['width'], 'height': s['height'],
                    'deviceScaleFactor': 1, 'mobile': False
                })
                await asyncio.sleep(0.3)

                await eval_js(s['setup_code'])
                await asyncio.sleep(0.8)

                # Inspeksi DOM & CSS
                metrics = await eval_js("""
                    (() => {
                        const board = document.querySelector('.result-board');
                        const screen = document.getElementById('screen-result');
                        const app = document.getElementById('app-viewport');
                        const btnReplay = document.getElementById('btn-result-replay-same');
                        const btnLead = document.getElementById('btn-result-leaderboard');
                        const btnMenu = document.getElementById('btn-result-menu');
                        const podium = document.getElementById('result-podium-container');
                        const remaining = document.getElementById('result-remaining-container');
                        const reflection = document.getElementById('result-reflection-card');
                        const unsolved = document.getElementById('result-unsolved-box');
                        const footnote = document.getElementById('result-speed-footnote');

                        const podiumCols = Array.from(document.querySelectorAll('.podium-col')).map(col => {
                            const nameEl = col.querySelector('.podium-team-name');
                            const scoreEl = col.querySelector('.podium-score');
                            const timeEl = col.querySelector('.podium-time-info');
                            const pedestalEl = col.querySelector('.podium-pedestal');
                            const rankEl = col.querySelector('.pedestal-rank-num');
                            const tieTag = col.querySelector('.pedestal-tie-tag');
                            const badges = Array.from(col.querySelectorAll('.podium-badge')).map(b => b.textContent.trim());

                            return {
                                name: nameEl ? nameEl.textContent.trim() : null,
                                nameFontSize: nameEl ? window.getComputedStyle(nameEl).fontSize : null,
                                score: scoreEl ? scoreEl.textContent.trim() : null,
                                scoreFontSize: scoreEl ? window.getComputedStyle(scoreEl).fontSize : null,
                                time: timeEl ? timeEl.textContent.trim() : null,
                                timeFontSize: timeEl ? window.getComputedStyle(timeEl).fontSize : null,
                                rank: rankEl ? rankEl.textContent.trim() : null,
                                hasTieTag: !!tieTag,
                                badges: badges,
                                pedestalHeight: pedestalEl ? pedestalEl.getBoundingClientRect().height : null
                            };
                        });

                        const remainingCols = Array.from(document.querySelectorAll('.remaining-team-card')).map(card => {
                            const nameEl = card.querySelector('.remaining-name');
                            const rankEl = card.querySelector('.remaining-rank');
                            const scoreEl = card.querySelector('.remaining-score');
                            const timeEl = card.querySelector('.remaining-time');
                            const tieTag = card.querySelector('.pedestal-tie-tag');
                            const badges = Array.from(card.querySelectorAll('.podium-badge')).map(b => b.textContent.trim());

                            // Check bounding box: is score inside card?
                            const cardRect = card.getBoundingClientRect();
                            const scoreRect = scoreEl ? scoreEl.getBoundingClientRect() : null;
                            const scoreInside = scoreRect ? (scoreRect.right <= cardRect.right + 2 && scoreRect.left >= cardRect.left) : true;

                            return {
                                name: nameEl ? nameEl.textContent.trim() : null,
                                rank: rankEl ? rankEl.textContent.trim() : null,
                                score: scoreEl ? scoreEl.textContent.trim() : null,
                                time: timeEl ? timeEl.textContent.trim() : null,
                                hasTieTag: !!tieTag,
                                badges: badges,
                                scoreInside: scoreInside
                            };
                        });

                        const allBadgesInDOM = Array.from(document.querySelectorAll('.podium-badge')).map(b => b.textContent.trim());

                        // Check reflection card
                        const reflectionVisible = reflection ? window.getComputedStyle(reflection).display !== 'none' : false;
                        const reflectionText = reflection ? document.getElementById('hl-reflection-question').textContent : null;

                        // Check unsolved pills count
                        const unsolvedPills = Array.from(document.querySelectorAll('.unsolved-compact-pill')).length;
                        const hasSuccessMessage = document.querySelector('.unsolved-compact-success') !== null;

                        return {
                            appScrollHeight: app.scrollHeight,
                            appClientHeight: app.clientHeight,
                            screenScrollHeight: screen.scrollHeight,
                            screenClientHeight: screen.clientHeight,
                            hasScrollbar: screen.scrollHeight > screen.clientHeight || app.scrollHeight > app.clientHeight,
                            btnReplayHeight: btnReplay ? btnReplay.getBoundingClientRect().height : null,
                            btnReplayFontSize: btnReplay ? window.getComputedStyle(btnReplay).fontSize : null,
                            btnLeadHeight: btnLead ? btnLead.getBoundingClientRect().height : null,
                            btnMenuHeight: btnMenu ? btnMenu.getBoundingClientRect().height : null,
                            podiumCols: podiumCols,
                            remainingCols: remainingCols,
                            allBadges: allBadgesInDOM,
                            footnoteVisible: footnote ? window.getComputedStyle(footnote).display !== 'none' : false,
                            reflectionVisible: reflectionVisible,
                            reflectionText: reflectionText,
                            unsolvedPills: unsolvedPills,
                            hasSuccessMessage: hasSuccessMessage
                        };
                    })()
                """)

                print(f"Scroll check: hasScrollbar={metrics['hasScrollbar']} (screen: {metrics['screenScrollHeight']}/{metrics['screenClientHeight']}, app: {metrics['appScrollHeight']}/{metrics['appClientHeight']})")
                print(f"Button heights: Replay={metrics['btnReplayHeight']}px (font: {metrics['btnReplayFontSize']}), Lead={metrics['btnLeadHeight']}px, Menu={metrics['btnMenuHeight']}px")
                print(f"Podium columns: {len(metrics['podiumCols'])}")
                for c in metrics['podiumCols']:
                    print(f"  Col {c['rank']}: {c['name']} (font: {c['nameFontSize']}), score: {c['score']} (font: {c['scoreFontSize']}), time: {c['time']} (font: {c['timeFontSize']}), badges: {c['badges']}, tie: {c['hasTieTag']}, pedestalH: {c['pedestalHeight']:.1f}px")
                if metrics['remainingCols']:
                    print(f"Remaining cards: {len(metrics['remainingCols'])}")
                    for r in metrics['remainingCols']:
                        print(f"  Row {r['rank']}: {r['name']}, score: {r['score']}, time: {r['time']}, tie: {r['hasTieTag']}, scoreInside: {r['scoreInside']}")

                print(f"All badges in DOM: {set(metrics['allBadges'])}")
                print(f"Footnote visible: {metrics['footnoteVisible']}")
                print(f"Reflection card visible: {metrics['reflectionVisible']} (text: {metrics['reflectionText']})")
                print(f"Unsolved pills: {metrics['unsolvedPills']}, success message: {metrics['hasSuccessMessage']}")

                # Assertions
                assert not metrics['hasScrollbar'], f"ERROR: Screen has scrollbar! {metrics['screenScrollHeight']} > {metrics['screenClientHeight']}"
                if s['height'] == 1080:
                    assert metrics['btnReplayHeight'] >= 79.0, f"ERROR: Button replay height < 80px in 1080p: {metrics['btnReplayHeight']}"
                else:
                    assert metrics['btnReplayHeight'] >= 59.0, f"ERROR: Button replay height < 60px in 768p: {metrics['btnReplayHeight']}"

                # Verify badges: ONLY "Skor Tertinggi" and "Tercepat" are allowed
                allowed_badges = {"Skor Tertinggi", "Tercepat"}
                for b in metrics['allBadges']:
                    assert b in allowed_badges, f"ERROR: Disallowed badge found: {b}!"

                # Verify remaining card scoreInside
                for r in metrics['remainingCols']:
                    assert r['scoreInside'], f"ERROR: Score badge overflowed card: {r}"

            print("\n=======================================================")
            print("ALL 5 SCENARIOS PASSED 100% WITH ZERO ERRORS!")
            print("=======================================================")

    finally:
        p.terminate()

if __name__ == '__main__':
    asyncio.run(main())
