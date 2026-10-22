import asyncio, json, os, subprocess, tempfile, time, websockets

EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
PORT = 9228

async def debug_rects():
    tmp_dir = tempfile.mkdtemp()
    proc = subprocess.Popen([
        EDGE_PATH, '--headless=new', f'--remote-debugging-port={PORT}',
        f'--user-data-dir={tmp_dir}', '--disable-gpu', '--no-sandbox', '--window-size=1920,1080'
    ])
    time.sleep(2)
    try:
        import urllib.request
        with urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json') as resp:
            ws_url = json.loads(resp.read().decode())[0]['webSocketDebuggerUrl']
        async with websockets.connect(ws_url) as ws:
            file_path = os.path.abspath('index.html').replace('\\', '/')
            await ws.send(json.dumps({'id': 1, 'method': 'Page.navigate', 'params': {'url': f'file:///{file_path}'}}))
            await ws.recv()
            await asyncio.sleep(1)
            
            expr = """
            (() => {
                document.getElementById('btn-start-game').click();
                document.querySelector('.btn-count-choice[data-count="3"]').click();
                document.getElementById('btn-proceed-to-game').click();
                document.querySelector('.team-card-btn').click();
                const st = window.__DETEKTIF_STATE__;
                const c = st.sessionCases[st.currentCaseIndex];
                document.querySelector(`.norma-stamp[data-norma="${c.jawabanId}"]`).click();
            })()
            """
            await ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': expr}}))
            await ws.recv()
            await asyncio.sleep(1)
            
            inspect_expr = """
            (() => {
                function rect(el) {
                    if (!el) return null;
                    const r = el.getBoundingClientRect();
                    return { id: el.id, class: el.className, x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height), right: Math.round(r.right), bottom: Math.round(r.bottom) };
                }
                return {
                    folder: rect(document.getElementById('case-folder')),
                    bottomRow: rect(document.querySelector('.folder-bottom-row')),
                    actionZone: rect(document.querySelector('.folder-action-zone')),
                    stampZone: rect(document.querySelector('.case-stamp-zone')),
                    stamp: rect(document.getElementById('stamp-terpecahkan')),
                    feedback: rect(document.getElementById('case-feedback-bar')),
                    reason: rect(document.getElementById('reason-panel'))
                };
            })()
            """
            await ws.send(json.dumps({'id': 3, 'method': 'Runtime.evaluate', 'params': {'expression': inspect_expr, 'returnByValue': True}}))
            res = json.loads(await ws.recv())
            print(json.dumps(res['result']['result']['value'], indent=2))
    finally:
        proc.terminate()
        try:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass

asyncio.run(debug_rects())
