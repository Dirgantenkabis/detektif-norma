# Graph Report - Detektif Norma  (2026-10-22)

## Corpus Check
- 22 files · ~400,448 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .css 1)

## Summary
- 206 nodes · 471 edges · 22 communities (20 shown, 2 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `61ab3b22`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- asyncio
- PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)
- Detektif Norma
- game.js
- handleAnswerWrong
- startNewCaseSession
- playSound
- finishGameSession
- TAHAP PERBAIKAN TAMPILAN & UX (ITERASI v1.2)
- audit_codebase.py
- main
- run_verification
- run_test
- run_test
- run_test
- run_master_audit
- test_loop
- main
- main
- main
- main

## God Nodes (most connected - your core abstractions)
1. `playSound()` - 22 edges
2. `TAHAP PERBAIKAN TAMPILAN & UX (ITERASI v1.2)` - 12 edges
3. `Detektif Norma` - 12 edges
4. `initBoardEvents()` - 11 edges
5. `startNewCaseSession()` - 10 edges
6. `PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)` - 10 edges
7. `navigateToMenu()` - 9 edges
8. `loadCase()` - 9 edges
9. `handleAnswerWrong()` - 9 edges
10. `finishGameSession()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `FASE 2: LAYAR AWAL, SETUP CEPAT, NAVIGASI` --references--> `navigateToMenu()`  [INFERRED]
  PROGRESS.md → game.js
- `FASE 5: SETUP KELOMPOK DAN MODAL PENGINGAT` --references--> `startNewCaseSession()`  [INFERRED]
  PROGRESS.md → game.js
- `Contoh Skema Kasus:` --references--> `validasiDataNorma()`  [INFERRED]
  README.md → data.js
- `FASE 1: FONDASI DAN DATA` --references--> `validasiDataNorma()`  [INFERRED]
  PROGRESS.md → data.js

## Import Cycles
- None detected.

## Communities (22 total, 2 thin omitted)

### Community 0 - "asyncio"
Cohesion: 0.26
Nodes (6): debug_rects(), inspect(), get_free_port(), run_test(), get_free_port(), run_test()

### Community 1 - "PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)"
Cohesion: 0.12
Nodes (14): KASUS_POOL, KELOMPOK_DEFAULT, NORMA_LIST, validasiDataNorma(), 📌 CATATAN PENTING & VERIFIKASI GURU, FASE 1: FONDASI DAN DATA, FASE 2: LAYAR AWAL, SETUP CEPAT, NAVIGASI, FASE 3: TATA LETAK PAPAN KASUS (+6 more)

### Community 2 - "Detektif Norma"
Cohesion: 0.11
Nodes (18): 1. Font Lokal, 2. Gambar Latar Layar Awal (Opsional), 3. Foto Profil Pembuat, 4. Mengisi Kontak Pembuat, Alur Setup Kelompok & Pengingat Peran, Aset Gambar dan Font (Opsional), Aturan Komposisi Data Kasus:, ⚡ Cara Kerja Papan Peringkat Kecepatan & Batasannya (+10 more)

### Community 3 - "game.js"
Cohesion: 0.23
Nodes (12): composeSessionCases(), initAudio(), initStorageData(), pauseTimer(), saveCurrentGroupsToStorage(), saveCustomNames(), shuffleArray(), startTimer() (+4 more)

### Community 4 - "handleAnswerWrong"
Cohesion: 0.18
Nodes (22): calculateAverageTime(), checkIfAllGroupsFailed(), disableStamps(), enableStamps(), evaluateReason(), goToNextCase(), handleAnswerCorrect(), handleAnswerWrong() (+14 more)

### Community 5 - "startNewCaseSession"
Cohesion: 0.32
Nodes (12): checkPreviousSessionSetup(), createGroupsAndProceed(), initNavigationEvents(), initResultEvents(), initSetupEvents(), navigateToMenu(), openModal(), renderEditNamesModal() (+4 more)

### Community 6 - "playSound"
Cohesion: 0.33
Nodes (9): closeModal(), exportLeaderboardJSON(), getAudioContext(), importLeaderboardJSON(), initLeaderboardEvents(), initModals(), openConfirmModal(), playSound() (+1 more)

### Community 7 - "finishGameSession"
Cohesion: 0.38
Nodes (6): finishGameSession(), formatAvgTime(), handleFinishNow(), launchConfetti(), renderResultScreen(), stopTimer()

### Community 8 - "TAHAP PERBAIKAN TAMPILAN & UX (ITERASI v1.2)"
Cohesion: 0.11
Nodes (19): 1. FASE 1: TATA LETAK VERTIKAL 6 ZONA BEBAS OVERFLOW & BEBAS SCROLL, 2. FASE 2: STANDARISASI LENCANA (HANYA 2 LENCANA RESMI), 3. FASE 3: PERBAIKAN PODIUM, SKOR SERI, DAN TEKS WAKTU, 4. FASE 4: STRIP INFO & KASUS YANG PERLU DIBAHAS, 5. FASE 5: TOMBOL AKSI & HASIL PENGUJIAN MENYELURUH (CDP), FASE 1: FONDASI RESPONSIF HP, FASE 1: SET IKON SVG SATU GAYA (GANTI SEMUA EMOJI), FASE 2: PAPAN KASUS DI HP TEGAK (390×844, 375×667, 360×640, 430×932) (+11 more)

### Community 10 - "main"
Cohesion: 0.60
Nodes (5): count_diff_pixels(), main(), call(), eval_js(), take_screenshot()

### Community 11 - "run_verification"
Cohesion: 0.60
Nodes (5): get_free_port(), run_verification(), eval_js(), send_cmd(), take_screenshot()

### Community 12 - "run_test"
Cohesion: 0.67
Nodes (4): get_free_port(), run_test(), eval_js(), send_cmd()

### Community 13 - "run_test"
Cohesion: 0.67
Nodes (4): get_free_port(), run_test(), eval_js(), send_cmd()

### Community 14 - "run_test"
Cohesion: 0.67
Nodes (4): get_free_port(), run_test(), eval_js(), send_cmd()

### Community 15 - "run_master_audit"
Cohesion: 0.67
Nodes (4): get_free_port(), run_master_audit(), eval_js(), send_cmd()

### Community 16 - "test_loop"
Cohesion: 1.00
Nodes (3): test_loop(), eval_js(), send_cmd()

### Community 18 - "main"
Cohesion: 0.83
Nodes (4): main(), call(), eval_js(), take_screenshot()

### Community 19 - "main"
Cohesion: 0.83
Nodes (4): main(), call(), eval_js(), take_screenshot()

### Community 20 - "main"
Cohesion: 0.83
Nodes (4): main(), call(), eval_js(), take_screenshot()

### Community 21 - "main"
Cohesion: 0.60
Nodes (5): count_diff_pixels(), main(), call(), eval_js(), take_screenshot()

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `validasiDataNorma()` connect `PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)` to `Detektif Norma`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Should `PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Should `Detektif Norma` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `TAHAP PERBAIKAN TAMPILAN & UX (ITERASI v1.2)` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._