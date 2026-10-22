import asyncio, json, os, subprocess, tempfile, time, websockets

EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
PORT = 9230

async def inspect():
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
            
            # Click sequence with proper pauses
            await ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.getElementById("btn-start-game").click()'}}))
            await ws.recv()
            await asyncio.sleep(0.4)
            
            await ws.send(json.dumps({'id': 3, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.querySelector(".btn-count-choice[data-count=\\"3\\"]").click()'}}))
            await ws.recv()
            await asyncio.sleep(0.4)
            
            await ws.send(json.dumps({'id': 4, 'method': 'Runtime.evaluate', 'params': {'expression': 'document.getElementById("btn-proceed-to-game").click()'}}))
            await ws.recv()
            await asyncio.sleep(0.8)
            
            expr = """
            (() => {
                const folder = document.getElementById('case-folder');
                const center = document.querySelector('.board-center-case');
                const main = document.querySelector('.board-main-area');
                const stampZone = document.querySelector('.case-stamp-zone');
                const bottomRow = document.querySelector('.folder-bottom-row');
                const actionZone = document.querySelector('.folder-action-zone');
                
                function b(el) {
                    if (!el) return null;
                    const r = el.getBoundingClientRect();
                    return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height), right: Math.round(r.right), bottom: Math.round(r.bottom) };
                }
                
                return {
                    main: b(main),
                    center: b(center),
                    folder: b(folder),
                    bottomRow: b(bottomRow),
                    actionZone: b(actionZone),
                    stampZone: b(stampZone)
                };
            })()
            """
            await ws.send(json.dumps({'id': 5, 'method': 'Runtime.evaluate', 'params': {'expression': expr, 'returnByValue': True}}))
            res = json.loads(await ws.recv())
            print(json.dumps(res['result']['result']['value'], indent=2))
    finally:
        proc.terminate()
        try:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass

asyncio.run(inspect())
