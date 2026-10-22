# Graph Report - Detektif Norma  (2026-10-21)

## Corpus Check
- 16 files · ~140,490 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: .css 1)

## Summary
- 165 nodes · 383 edges · 18 communities (16 shown, 2 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- asyncio
- PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)
- Detektif Norma
- startNewCaseSession
- handleAnswerWrong
- game.js
- playSound
- finishGameSession
- initBoardEvents
- audit_codebase.py
- stopTimer
- run_verification
- run_test
- run_test
- run_test
- run_master_audit
- test_loop

## God Nodes (most connected - your core abstractions)
1. `playSound()` - 22 edges
2. `initBoardEvents()` - 11 edges
3. `startNewCaseSession()` - 10 edges
4. `PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)` - 10 edges
5. `TAHAP PERBAIKAN TAMPILAN & UX (ITERASI v1.2)` - 10 edges
6. `Detektif Norma` - 10 edges
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

## Communities (18 total, 2 thin omitted)

### Community 0 - "asyncio"
Cohesion: 0.30
Nodes (6): debug_rects(), inspect(), get_free_port(), run_test(), get_free_port(), run_test()

### Community 1 - "PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)"
Cohesion: 0.08
Nodes (24): KASUS_POOL, KELOMPOK_DEFAULT, NORMA_LIST, validasiDataNorma(), 📌 CATATAN PENTING & VERIFIKASI GURU, FASE 1: FONDASI DAN DATA, FASE 1: SET IKON SVG SATU GAYA (GANTI SEMUA EMOJI), FASE 2: LAYAR AWAL, SETUP CEPAT, NAVIGASI (+16 more)

### Community 2 - "Detektif Norma"
Cohesion: 0.12
Nodes (16): 1. Font Lokal, 2. Gambar Latar Layar Awal (Opsional), 3. Foto Profil Pembuat, 4. Mengisi Kontak Pembuat, Alur Setup Kelompok & Pengingat Peran, Aset Gambar dan Font (Opsional), Aturan Komposisi Data Kasus:, ⚡ Cara Kerja Papan Peringkat Kecepatan & Batasannya (+8 more)

### Community 3 - "startNewCaseSession"
Cohesion: 0.24
Nodes (12): composeSessionCases(), createGroupsAndProceed(), initSetupEvents(), initStorageData(), openModal(), renderEditNamesModal(), saveCurrentGroupsToStorage(), saveCustomNames() (+4 more)

### Community 4 - "handleAnswerWrong"
Cohesion: 0.30
Nodes (12): disableStamps(), goToNextCase(), handleAnswerCorrect(), handleAnswerWrong(), handleCancelTurn(), handleSelectGroupTurn(), handleUnlockNextClue(), loadCase() (+4 more)

### Community 5 - "game.js"
Cohesion: 0.44
Nodes (9): checkPreviousSessionSetup(), initAudio(), initNavigationEvents(), initResultEvents(), navigateToMenu(), renderLeaderboardTable(), showScreen(), toggleSound() (+1 more)

### Community 6 - "playSound"
Cohesion: 0.29
Nodes (10): closeModal(), exportLeaderboardJSON(), getAudioContext(), handleFinishNow(), importLeaderboardJSON(), initLeaderboardEvents(), initModals(), openConfirmModal() (+2 more)

### Community 7 - "finishGameSession"
Cohesion: 0.38
Nodes (6): calculateAverageTime(), finishGameSession(), formatAvgTime(), launchConfetti(), renderResultScreen(), saveEligibleGroupsToLeaderboard()

### Community 8 - "initBoardEvents"
Cohesion: 0.38
Nodes (7): enableStamps(), evaluateReason(), handleStampAnswer(), handleTogglePause(), initBoardEvents(), pauseTimer(), setupHoldReasonButton()

### Community 10 - "stopTimer"
Cohesion: 0.40
Nodes (5): checkIfAllGroupsFailed(), showCaseExplanation(), startTimer(), stopTimer(), updateTimerDisplay()

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

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `navigateToMenu()` connect `game.js` to `initBoardEvents`, `PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)`, `stopTimer`, `playSound`?**
  _High betweenness centrality (0.151) - this node is a cross-community bridge._
- **Should `PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._
- **Why does `FASE 2: LAYAR AWAL, SETUP CEPAT, NAVIGASI` connect `PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)` to `game.js`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Should `Detektif Norma` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._