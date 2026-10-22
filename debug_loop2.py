import asyncio
import json
import os
import subprocess
import tempfile
import urllib.request
import websockets

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE_PATH):
    EDGE_PATH = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

async def test_loop():
    tmp_dir = tempfile.mkdtemp()
    proc = subprocess.Popen([
        EDGE_PATH,
        "--headless=new",
        "--remote-debugging-port=9444",
        f"--user-data-dir={tmp_dir}",
        "--disable-extensions",
        "--disable-gpu",
        "--no-sandbox"
    ])
    await asyncio.sleep(2.0)

    try:
        req = urllib.request.urlopen("http://127.0.0.1:9444/json")
        tabs = json.loads(req.read().decode())
        page_tab = next(t for t in tabs if t.get("type") == "page")
        ws_url = page_tab["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
            msg_id = 1
            async def send_cmd(method, params=None):
                nonlocal msg_id
                cid = msg_id
                msg_id += 1
                await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
                while True:
                    resp = json.loads(await ws.recv())
                    if resp.get("id") == cid:
                        r = resp.get("result", {})
                        if "result" in r and "value" in r["result"]:
                            return r["result"]["value"]
                        return r

            async def eval_js(expression):
                return await send_cmd("Runtime.evaluate", {"expression": expression, "returnByValue": True})

            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")
            await send_cmd("DOM.enable")

            file_path = os.path.abspath("index.html").replace("\\", "/")
            await send_cmd("Page.navigate", {"url": f"file:///{file_path}"})
            await asyncio.sleep(1.0)

            # Start game with 4 teams
            await eval_js("""
                window.showScreen('screen-setup');
                document.querySelector('.btn-count-choice[data-count=\"4\"]').click();
            """)
            await asyncio.sleep(0.3)
            # Dismiss modal
            await eval_js("const b = document.getElementById('btn-proceed-to-game'); if (b) b.click();")
            await asyncio.sleep(0.4)

            # Selesaikan kasus 1
            print("Case 1:")
            await eval_js("document.querySelectorAll('.team-card-btn')[0].click();")
            ans1 = await eval_js("State.sessionCases[0].jawabanId")
            await eval_js(f"document.querySelector('.norma-stamp[data-norma=\"{ans1}\"]').click();")
            await asyncio.sleep(0.3)
            await eval_js("evaluateReason(true);")
            await asyncio.sleep(0.2)
            await eval_js("document.getElementById('btn-next-case').click();")
            await asyncio.sleep(0.4)

            print("After Case 1 next, checking state:")
            s1 = await eval_js("({ idx: State.currentCaseIndex, isAnswered: State.isCaseAnswered, activeGroup: State.activeGroupIndex, locked: Array.from(State.lockedGroupsForCase) })")
            print(s1)

            # Sekarang di kasus 2:
            print("\nCase 2:")
            team_cards_len = await eval_js("document.querySelectorAll('.team-card-btn').length")
            print(f"team_cards_len: {team_cards_len}")
            click_res = await eval_js("""
                (() => {
                    const cards = document.querySelectorAll('.team-card-btn');
                    if (cards.length > 0) {
                        cards[0].click();
                        return { clicked: true, activeGroup: State.activeGroupIndex };
                    }
                    return { clicked: false };
                })()
            """)
            print("Team card 0 click result:", click_res)

            ans2 = await eval_js("State.sessionCases[State.currentCaseIndex].jawabanId")
            stamp_info = await eval_js(f"""
                (() => {{
                    const s = document.querySelector('.norma-stamp[data-norma=\"{ans2}\"]');
                    return {{
                        found: !!s,
                        disabled: s.disabled,
                        classes: s.className
                    }};
                }})()
            """)
            print("Stamp info for ans2:", stamp_info)

            # Click stamp
            await eval_js(f"document.querySelector('.norma-stamp[data-norma=\"{ans2}\"]').click();")
            await asyncio.sleep(0.4)
            s2_after_stamp = await eval_js("({ idx: State.currentCaseIndex, isAnswered: State.isCaseAnswered, processing: State.isProcessingAnswer })")
            print("After stamp click:", s2_after_stamp)
    finally:
        proc.terminate()
        try: proc.wait(timeout=2)
        except: proc.kill()

asyncio.run(test_loop())
