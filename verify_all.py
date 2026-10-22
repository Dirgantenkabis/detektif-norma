import asyncio, websockets, json, subprocess, tempfile, urllib.request, os, base64

EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(EDGE_PATH): EDGE_PATH = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

async def main():
    tmp = tempfile.mkdtemp()
    p = subprocess.Popen([
        EDGE_PATH,
        '--headless=new',
        '--remote-debugging-port=9411',
        f'--user-data-dir={tmp}',
        '--disable-extensions',
        '--disable-gpu',
        '--no-sandbox'
    ])
    await asyncio.sleep(2.0)
    try:
        req = urllib.request.urlopen('http://127.0.0.1:9411/json')
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

            # Uji kedua tipe kasus: Dasar (k07) & HOTS (k12) di 1080p & 768p
            cases_to_test = [
                ("k07", "DASAR (Rina Dompet)", "kesusilaan"),
                ("k12", "HOTS (Kiki Difitnah)", "kesusilaan")
            ]

            for case_id, case_label, ans in cases_to_test:
                for w, h in [(1920, 1080), (1366, 768)]:
                    print(f"\n=======================================================")
                    print(f"VERIFYING {case_label} AT {w}x{h}")
                    print(f"=======================================================")
                    await call('Page.navigate', {'url': f'file:///{fp}'})
                    await asyncio.sleep(0.8)
                    await call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': False})
                    await asyncio.sleep(0.3)

                    # Setup game 4 kelompok
                    await eval_js("""
                        window.showScreen('screen-setup');
                        document.querySelector('.btn-count-choice[data-count="4"]').click();
                    """)
                    await asyncio.sleep(0.3)
                    await eval_js("""
                        const modal = document.getElementById('modal-role-reminder');
                        if (modal && modal.classList.contains('active')) {
                            document.getElementById('btn-proceed-to-game').click();
                        }
                    """)
                    await asyncio.sleep(0.3)

                    # Pasang kasus target
                    await eval_js(f"""
                        window.showScreen('screen-board');
                        const targetCase = KASUS_POOL.find(k => k.id === '{case_id}');
                        State.sessionCases[0] = targetCase;
                        window.loadCase(0);
                        window.handleSelectGroupTurn(0);
                    """)
                    await asyncio.sleep(0.3)

                    # Jawab benar
                    await eval_js(f"window.handleStampAnswer('{ans}');")
                    await asyncio.sleep(0.6)

                    # Audit Phase 1
                    p1 = await eval_js("""
                        (() => {
                            const getR = id => {
                                const el = document.getElementById(id);
                                if (!el) return null;
                                const r = el.getBoundingClientRect();
                                return { id, top: Math.round(r.top), bottom: Math.round(r.bottom), height: Math.round(r.height), display: window.getComputedStyle(el).display, visibility: window.getComputedStyle(el).visibility };
                            };
                            const clue1 = getR('clue-slot-1');
                            const clue2 = getR('clue-slot-2');
                            const clue3 = getR('clue-slot-3');
                            const feedback = getR('case-feedback-bar');
                            const hotsBox = getR('hots-question-box');
                            const teacherEval = getR('teacher-reason-actions');
                            const explanation = getR('explanation-box');
                            const stamp = getR('stamp-terpecahkan');

                            const maxClueBottom = Math.max(clue1.bottom, clue2.bottom, clue3.bottom);
                            const minBottomRowTop = feedback.top;

                            return {
                                hasScrollY: document.documentElement.scrollHeight > document.documentElement.clientHeight,
                                hasScrollX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                                clearance: minBottomRowTop - maxClueBottom,
                                feedbackVisible: feedback.display === 'flex',
                                promptBoxVisible: hotsBox.display === 'block',
                                promptLabel: document.getElementById('hots-prompt-label').textContent,
                                promptText: document.getElementById('hots-question-text').textContent,
                                teacherVisible: teacherEval.display === 'block',
                                explanationHidden: explanation.display === 'none',
                                stampVisible: stamp.visibility === 'visible'
                            };
                        })()
                    """)
                    print("PHASE 1 AUDIT:", json.dumps(p1, indent=2))
                    assert p1['hasScrollY'] == False, "0 vertical scroll"
                    assert p1['hasScrollX'] == False, "0 horizontal scroll"
                    assert p1['clearance'] > 15, "0 collision with clues"
                    assert p1['feedbackVisible'] == True, "Feedback banner visible"
                    assert p1['promptBoxVisible'] == True, "Question/prompt box MUST be visible!"
                    assert len(p1['promptText']) > 5, "Question text must not be empty"
                    assert p1['teacherVisible'] == True, "Teacher eval buttons visible"
                    assert p1['explanationHidden'] == True, "Explanation box hidden in Phase 1"
                    assert p1['stampVisible'] == True, "TERPECAHKAN stamp visible"

                    # Audit Phase 2
                    await eval_js("window.evaluateReason(true);")
                    await asyncio.sleep(0.4)

                    p2 = await eval_js("""
                        (() => {
                            const hotsBox = document.getElementById('hots-question-box');
                            const teacherEval = document.getElementById('teacher-reason-actions');
                            const explanation = document.getElementById('explanation-box');
                            const nextBtn = document.getElementById('btn-next-case');
                            const stamp = document.getElementById('stamp-terpecahkan');
                            const feedback = document.getElementById('case-feedback-bar');
                            const clue1 = document.getElementById('clue-slot-1');
                            const clue2 = document.getElementById('clue-slot-2');
                            const clue3 = document.getElementById('clue-slot-3');
                            const maxClueBottom = Math.max(clue1.getBoundingClientRect().bottom, clue2.getBoundingClientRect().bottom, clue3.getBoundingClientRect().bottom);
                            const minBottomRowTop = feedback.getBoundingClientRect().top;

                            return {
                                hasScrollY: document.documentElement.scrollHeight > document.documentElement.clientHeight,
                                hasScrollX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                                clearance: Math.round(minBottomRowTop - maxClueBottom),
                                promptHidden: window.getComputedStyle(hotsBox).display === 'none',
                                teacherHidden: window.getComputedStyle(teacherEval).display === 'none',
                                expVisible: window.getComputedStyle(explanation).display === 'block',
                                nextBtnVisible: window.getComputedStyle(nextBtn).display !== 'none',
                                stampVisible: window.getComputedStyle(stamp).visibility === 'visible'
                            };
                        })()
                    """)
                    print("PHASE 2 AUDIT:", json.dumps(p2, indent=2))
                    assert p2['hasScrollY'] == False, "0 vertical scroll in Phase 2"
                    assert p2['hasScrollX'] == False, "0 horizontal scroll in Phase 2"
                    assert p2['clearance'] > 15, "0 collision in Phase 2"
                    assert p2['promptHidden'] == True, "Prompt box hidden in Phase 2"
                    assert p2['teacherHidden'] == True, "Teacher eval buttons hidden in Phase 2"
                    assert p2['expVisible'] == True, "Explanation visible in Phase 2"
                    assert p2['nextBtnVisible'] == True, "Next button visible in Phase 2"
                    assert p2['stampVisible'] == True, "Stamp visible in Phase 2"
                    print(f"PASSED {case_label} at {w}x{h}!")

    finally:
        p.kill()

if __name__ == '__main__':
    asyncio.run(main())
