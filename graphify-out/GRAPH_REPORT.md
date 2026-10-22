# Graph Report - Detektif Norma  (2026-10-23)

## Corpus Check
- 31 files · ~92,766 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .css 1)

## Summary
- 263 nodes · 622 edges · 29 communities (24 shown, 5 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 12 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `acb0050a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- asyncio
- PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)
- Detektif Norma
- test_explanation
- game.js
- run_podium_test
- test_scrolled_eval
- test_start_setup
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
- main
- main
- main
- run_test
- run_test
- test_correct
- run_test

## God Nodes (most connected - your core abstractions)
1. `playSound()` - 22 edges
2. `TAHAP PERBAIKAN TAMPILAN & UX (ITERASI v1.2)` - 15 edges
3. `Detektif Norma` - 13 edges
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
- `🏆 FASE 8: AUDIT MENYELURUH & RESOLUSI CACAT MOBILE LANDSCAPE (100% BEBAS CACAT)` --references--> `showCaseExplanation()`  [INFERRED]
  PROGRESS.md → game.js
- `FASE 1: FONDASI DAN DATA` --references--> `validasiDataNorma()`  [INFERRED]
  PROGRESS.md → data.js
- `Contoh Skema Kasus:` --references--> `validasiDataNorma()`  [INFERRED]
  README.md → data.js

## Import Cycles
- None detected.

## Communities (29 total, 5 thin omitted)

### Community 1 - "PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)"
Cohesion: 0.11
Nodes (17): KASUS_POOL, KELOMPOK_DEFAULT, NORMA_LIST, validasiDataNorma(), 📌 CATATAN PENTING & VERIFIKASI GURU, FASE 1: FONDASI DAN DATA, FASE 2: LAYAR AWAL, SETUP CEPAT, NAVIGASI, FASE 3: TATA LETAK PAPAN KASUS (+9 more)

### Community 2 - "Detektif Norma"
Cohesion: 0.11
Nodes (18): 1. Font Lokal, 1. Pilihan Mode Tampilan, 2. Batasan Teknis Perangkat Bergerak, 2. Gambar Latar Layar Awal (Opsional), 3. Foto Profil Pembuat, 4. Mengisi Kontak Pembuat, Alur Setup Kelompok & Pengingat Peran, Aset Gambar dan Font (Opsional) (+10 more)

### Community 3 - "test_explanation"
Cohesion: 0.67
Nodes (4): get_free_port(), test_explanation(), cmd(), eval_js()

### Community 4 - "game.js"
Cohesion: 0.09
Nodes (61): calculateAverageTime(), checkIfAllGroupsFailed(), checkPreviousSessionSetup(), closeModal(), composeSessionCases(), createGroupsAndProceed(), disableStamps(), enableStamps() (+53 more)

### Community 5 - "run_podium_test"
Cohesion: 0.67
Nodes (4): get_free_port(), run_podium_test(), cmd(), eval_js()

### Community 6 - "test_scrolled_eval"
Cohesion: 0.67
Nodes (4): get_free_port(), test_scrolled_eval(), cmd(), eval_js()

### Community 7 - "test_start_setup"
Cohesion: 0.67
Nodes (4): get_free_port(), test_start_setup(), cmd(), eval_js()

### Community 8 - "TAHAP PERBAIKAN TAMPILAN & UX (ITERASI v1.2)"
Cohesion: 0.08
Nodes (25): 1. FASE 1: TATA LETAK VERTIKAL 6 ZONA BEBAS OVERFLOW & BEBAS SCROLL, 2. FASE 2: STANDARISASI LENCANA (HANYA 2 LENCANA RESMI), 3. FASE 3: PERBAIKAN PODIUM, SKOR SERI, DAN TEKS WAKTU, 4. FASE 4: STRIP INFO & KASUS YANG PERLU DIBAHAS, 5. FASE 5: TOMBOL AKSI & HASIL PENGUJIAN MENYELURUH (CDP), FASE 1: FONDASI RESPONSIF HP, FASE 1: SET IKON SVG SATU GAYA (GANTI SEMUA EMOJI), FASE 2: PAPAN KASUS DI HP TEGAK (390×844, 375×667, 360×640, 430×932) (+17 more)

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

### Community 22 - "main"
Cohesion: 0.60
Nodes (5): count_diff_pixels(), main(), call(), eval_js(), take_screenshot()

### Community 23 - "main"
Cohesion: 0.60
Nodes (5): count_diff_pixels(), main(), call(), eval_js(), take_screenshot()

### Community 24 - "main"
Cohesion: 0.60
Nodes (5): count_diff_pixels(), main(), call(), eval_js(), take_screenshot()

### Community 27 - "test_correct"
Cohesion: 0.67
Nodes (4): get_free_port(), test_correct(), cmd(), eval_js()

### Community 28 - "run_test"
Cohesion: 0.67
Nodes (4): get_free_port(), run_test(), eval_js(), send_cmd()

## Knowledge Gaps
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Should `PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `Detektif Norma` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `game.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09474206349206349 - nodes in this community are weakly interconnected._
- **Should `TAHAP PERBAIKAN TAMPILAN & UX (ITERASI v1.2)` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._