/**
 * Detektif Norma - game.js
 * Logika Interaksi, Navigasi Layar, Audio Web API, dan Alur Permainan
 * Sesuai PRD v1.1
 */

(function () {
  "use strict";

  // ==========================================================================
  // STATE APLIKASI
  // ==========================================================================
  const State = {
    currentScreen: "screen-start",
    soundEnabled: true,
    audioCtx: null,

    // Kelompok aktif
    groupCount: 4,
    groups: [], // [{ id, nama, warna, warnaBorder, skor: 0, correctTimes: [], correctCount: 0 }]
    activeGroupIndex: null, // index tim yang sedang dapat giliran menjawab
    lockedGroupsForCase: new Set(), // Set index tim yang salah tebak di kasus aktif
    lockedNormasForCase: new Set(), // Set norma yang salah ditebak di kasus aktif (terkunci dengan ikon gembok)

    // Sesi permainan (12 kasus)
    sessionCases: [],
    lastSessionCaseIds: new Set(),
    currentCaseIndex: 0,
    currentClueIndex: 1, // 1, 2, atau 3
    isCaseAnswered: false,
    reasonEvaluated: false,
    isProcessingAnswer: false, // Guard klik cepat ganda
    unsolvedCases: [], // Kasus yang gagal dijawab untuk dibahas di akhir

    // Timer berpikir
    timerRunning: false,
    timerSeconds: 0,
    timerInterval: null,
    isPaused: false,

    // Rekor kecepatan (localStorage)
    leaderboard: [],

    // Penanda modal pengingat peran hanya muncul 1x per pembukaan halaman (hanya di memori)
    hasShownRoleReminder: false
  };

  // Ekspos state untuk pengujian dan otomasi
  if (typeof window !== "undefined") {
    window.State = State;
    window.evaluateReason = evaluateReason;
    window.renderLeaderboardTable = renderLeaderboardTable;
  }

  // Kunci penyimpanan lokal
  const STORAGE_KEYS = {
    GROUPS: "detektif_norma_last_groups",
    LEADERBOARD: "detektif_norma_leaderboard",
    SOUND: "detektif_norma_sound",
    CUSTOM_NAMES: "detektif_norma_custom_names"
  };

  // ==========================================================================
  // INISIALISASI SAAT HALAMAN SIAP
  // ==========================================================================
  document.addEventListener("DOMContentLoaded", () => {
    initAudio();
    initStorageData();
    initModals();
    initNavigationEvents();
    initSetupEvents();
    initBoardEvents();
    initResultEvents();
    initLeaderboardEvents();
    checkPreviousSessionSetup();

    // Pastikan validasi data dieksekusi
    if (typeof validasiDataNorma === "function") {
      validasiDataNorma();
    }
  });

  // ==========================================================================
  // SISTEM AUDIO (WEB AUDIO API OSCILLATOR TANPA FILE EXTERNAL)
  // ==========================================================================
  function initAudio() {
    try {
      const savedSound = localStorage.getItem(STORAGE_KEYS.SOUND);
      if (savedSound !== null) {
        State.soundEnabled = savedSound === "true";
      }
    } catch (e) {
      // Abaikan bila localStorage diblokir
    }
    updateSoundUI();
  }

  function getAudioContext() {
    if (!State.audioCtx) {
      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      if (AudioCtxClass) {
        State.audioCtx = new AudioCtxClass();
      }
    }
    if (State.audioCtx && State.audioCtx.state === "suspended") {
      State.audioCtx.resume();
    }
    return State.audioCtx;
  }

  function toggleSound() {
    State.soundEnabled = !State.soundEnabled;
    try {
      localStorage.setItem(STORAGE_KEYS.SOUND, String(State.soundEnabled));
    } catch (e) {}
    updateSoundUI();
    if (State.soundEnabled) {
      playSound("click");
    }
  }

  function updateSoundUI() {
    const textStart = document.getElementById("sound-text");
    const iconContainerStart = document.getElementById("sound-icon-container");
    const btnBoard = document.getElementById("btn-board-sound");

    const label = State.soundEnabled ? "Suara ON" : "Suara OFF";
    const iconId = State.soundEnabled ? "#icon-volume-on" : "#icon-volume-off";
    const svgHtml = `<svg class="ui-icon" aria-hidden="true"><use href="${iconId}"></use></svg>`;

    if (textStart) textStart.textContent = label;
    if (iconContainerStart) iconContainerStart.innerHTML = svgHtml;
    if (btnBoard) btnBoard.innerHTML = svgHtml;
  }

  // Timestamp suara terakhir untuk mencegah penumpukan audio
  const lastSoundTimes = {};

  function playSound(type) {
    if (!State.soundEnabled) return;
    const nowMs = Date.now();
    if (lastSoundTimes[type] && nowMs - lastSoundTimes[type] < 60) {
      return; // Cegah suara bertumpuk
    }
    lastSoundTimes[type] = nowMs;

    const ctx = getAudioContext();
    if (!ctx) return;

    const now = ctx.currentTime;

    try {
      if (type === "click") {
        // Nada klik lembut pendek
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(600, now);
        osc.frequency.exponentialRampToValueAtTime(300, now + 0.04);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.04);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.04);
      } else if (type === "stamp") {
        // Multi-layer Suara Stempel Tinta Fisik:
        // 1. Dentuman rendah: sine turun 140 Hz -> 45 Hz dalam 0.14 detik, gain turun cepat
        const oscSine = ctx.createOscillator();
        const gainSine = ctx.createGain();
        oscSine.type = "sine";
        oscSine.frequency.setValueAtTime(140, now);
        oscSine.frequency.exponentialRampToValueAtTime(45, now + 0.14);
        gainSine.gain.setValueAtTime(0.48, now);
        gainSine.gain.exponentialRampToValueAtTime(0.001, now + 0.14);
        oscSine.connect(gainSine);
        gainSine.connect(ctx.destination);
        oscSine.start(now);
        oscSine.stop(now + 0.14);

        // 2. Semburan noise pendek lewat lowpass 800 Hz (0.05 detik)
        try {
          const noiseLength = Math.floor(ctx.sampleRate * 0.05);
          const noiseBuffer = ctx.createBuffer(1, noiseLength, ctx.sampleRate);
          const noiseData = noiseBuffer.getChannelData(0);
          for (let i = 0; i < noiseLength; i++) {
            noiseData[i] = Math.random() * 2 - 1;
          }
          const noiseSrc = ctx.createBufferSource();
          noiseSrc.buffer = noiseBuffer;

          const filter = ctx.createBiquadFilter();
          filter.type = "lowpass";
          filter.frequency.setValueAtTime(800, now);

          const gainNoise = ctx.createGain();
          gainNoise.gain.setValueAtTime(0.32, now);
          gainNoise.gain.linearRampToValueAtTime(0.001, now + 0.05);

          noiseSrc.connect(filter);
          filter.connect(gainNoise);
          gainNoise.connect(ctx.destination);

          noiseSrc.start(now);
          noiseSrc.stop(now + 0.05);
        } catch (e) {
          // Fallback aman jika Web Audio buffer terbatas
        }

        // 3. Klik kecil sekitar 2 kHz (0.02 detik)
        const oscClick = ctx.createOscillator();
        const gainClick = ctx.createGain();
        oscClick.type = "sine";
        oscClick.frequency.setValueAtTime(2000, now);
        gainClick.gain.setValueAtTime(0.18, now);
        gainClick.gain.linearRampToValueAtTime(0.001, now + 0.02);
        oscClick.connect(gainClick);
        gainClick.connect(ctx.destination);
        oscClick.start(now);
        oscClick.stop(now + 0.02);
      } else if (type === "correct") {
        // Nada naik gembira (arpeggio dua nada: C5 -> G5)
        const notes = [523.25, 783.99];
        notes.forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = "sine";
          osc.frequency.setValueAtTime(freq, now + idx * 0.1);
          gain.gain.setValueAtTime(0.2, now + idx * 0.1);
          gain.gain.linearRampToValueAtTime(0.01, now + idx * 0.1 + 0.2);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + idx * 0.1);
          osc.stop(now + idx * 0.1 + 0.22);
        });
      } else if (type === "wrong") {
        // Nada turun lembut (bukan buzzer menjengkelkan, santun untuk anak)
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(320, now);
        osc.frequency.linearRampToValueAtTime(220, now + 0.2);
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.2);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.22);
      } else if (type === "finish") {
        // Nada selebrasi kemenangan
        const chord = [523.25, 659.25, 783.99, 1046.50];
        chord.forEach((freq, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = "triangle";
          osc.frequency.setValueAtTime(freq, now + i * 0.08);
          gain.gain.setValueAtTime(0.18, now + i * 0.08);
          gain.gain.linearRampToValueAtTime(0.01, now + i * 0.08 + 0.4);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + i * 0.08);
          osc.stop(now + i * 0.08 + 0.42);
        });
      }
    } catch (err) {
      // Mengabaikan error pemutaran suara
    }
  }

  // ==========================================================================
  // MANAJEMEN PENYIMPANAN DATA (DENGAN TRY/CATCH)
  // ==========================================================================
  function initStorageData() {
    try {
      const savedLeaderboard = localStorage.getItem(STORAGE_KEYS.LEADERBOARD);
      if (savedLeaderboard) {
        const parsed = JSON.parse(savedLeaderboard);
        if (Array.isArray(parsed)) {
          State.leaderboard = parsed;
        }
      }
    } catch (e) {
      console.warn("Penyimpanan lokal tidak tersedia, peringkat hanya sesi aktif.");
    }

    try {
      const savedNames = localStorage.getItem(STORAGE_KEYS.CUSTOM_NAMES);
      if (savedNames) {
        const parsedNames = JSON.parse(savedNames);
        if (Array.isArray(parsedNames)) {
          parsedNames.forEach((name, idx) => {
            if (KELOMPOK_DEFAULT[idx] && name && name.trim().length > 0) {
              KELOMPOK_DEFAULT[idx].nama = name.trim();
            }
          });
        }
      }
    } catch (e) {}

    updateSetupNamesPreview();
  }

  function updateSetupNamesPreview() {
    const el = document.getElementById("setup-names-list-text");
    if (el) {
      el.textContent = KELOMPOK_DEFAULT.map(k => k.nama).join(", ");
    }
  }

  function checkPreviousSessionSetup() {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.GROUPS);
      if (saved) {
        const data = JSON.parse(saved);
        if (data && Array.isArray(data.groups) && data.groups.length >= 2) {
          const btnResume = document.getElementById("btn-resume-previous");
          const labelTitle = document.getElementById("label-resume-title");
          const labelSub = document.getElementById("label-resume-sub");
          if (btnResume && labelTitle && labelSub) {
            btnResume.style.display = "inline-flex";
            const teamNames = data.groups.map(g => g.nama).join(", ");
            labelTitle.textContent = `Lanjutkan dengan ${data.groups.length} kelompok`;
            labelSub.textContent = teamNames;
          }
          return;
        }
      }
    } catch (e) {}

    const btnResume = document.getElementById("btn-resume-previous");
    if (btnResume) btnResume.style.display = "none";
  }

  // ==========================================================================
  // MANAJEMEN LAYAR & NAVIGASI (FADE PENDEK)
  // ==========================================================================
  function showScreen(screenId) {
    const screens = document.querySelectorAll(".screen");
    screens.forEach(s => {
      s.classList.remove("active");
      s.style.display = "none";
    });

    const target = document.getElementById(screenId);
    if (target) {
      target.style.display = "flex";
      // Trigger reflow untuk animasi fade
      void target.offsetWidth;
      target.classList.add("active");
      State.currentScreen = screenId;
    }
  }

  function navigateToMenu() {
    if (State.currentScreen === "screen-board") {
      openConfirmModal(
        "Keluar ke Menu Awal? Sesi saat ini akan dihentikan dan kemajuan tidak disimpan.",
        () => {
          stopTimer();
          showScreen("screen-start");
          checkPreviousSessionSetup();
        }
      );
    } else {
      showScreen("screen-start");
      checkPreviousSessionSetup();
    }
  }

  // ==========================================================================
  // MANAJEMEN MODAL (TOMBOL TUTUP BESAR, BACKDROP, ESCAPE KEY)
  // ==========================================================================
  let activeModal = null;

  function initModals() {
    // Tombol penutup modal
    document.querySelectorAll(".btn-close-modal").forEach(btn => {
      btn.addEventListener("click", () => {
        const modalId = btn.getAttribute("data-close");
        closeModal(modalId);
        playSound("click");
      });
    });

    // Klik di area backdrop gelap
    document.querySelectorAll(".modal-overlay").forEach(overlay => {
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) {
          closeModal(overlay.id);
          playSound("click");
          if (overlay.id === "modal-role-reminder") {
            startNewCaseSession();
          }
        }
      });
    });

    // Tombol keyboard Escape
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && activeModal) {
        const modalId = activeModal.id;
        closeModal(modalId);
        playSound("click");
        if (modalId === "modal-role-reminder") {
          startNewCaseSession();
        }
      }
    });
  }

  function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add("active");
      activeModal = modal;
    }
  }

  function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove("active");
      if (activeModal === modal) {
        activeModal = null;
      }
    }
  }

  function openConfirmModal(message, onConfirm) {
    const msgEl = document.getElementById("confirm-message");
    const btnYes = document.getElementById("btn-confirm-yes");
    const btnNo = document.getElementById("btn-confirm-no");

    if (msgEl) msgEl.textContent = message;

    const handleYes = () => {
      btnYes.removeEventListener("click", handleYes);
      btnNo.removeEventListener("click", handleNo);
      closeModal("modal-confirm");
      playSound("click");
      if (onConfirm) onConfirm();
    };

    const handleNo = () => {
      btnYes.removeEventListener("click", handleYes);
      btnNo.removeEventListener("click", handleNo);
      closeModal("modal-confirm");
      playSound("click");
    };

    btnYes.addEventListener("click", handleYes);
    btnNo.addEventListener("click", handleNo);

    openModal("modal-confirm");
  }

  // ==========================================================================
  // EVENT LISTENER: LAYAR AWAL & NAVIGASI
  // ==========================================================================
  function initNavigationEvents() {
    // Layar Penuh Toggle
    const handleFullscreen = () => {
      playSound("click");
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen().catch(() => {});
        }
      }
    };

    const fsBtnStart = document.getElementById("btn-fullscreen-toggle");
    const fsBtnBoard = document.getElementById("btn-board-fullscreen");
    if (fsBtnStart) fsBtnStart.addEventListener("click", handleFullscreen);
    if (fsBtnBoard) fsBtnBoard.addEventListener("click", handleFullscreen);

    // Suara Toggle
    const soundBtnStart = document.getElementById("btn-sound-toggle");
    const soundBtnBoard = document.getElementById("btn-board-sound");
    if (soundBtnStart) soundBtnStart.addEventListener("click", toggleSound);
    if (soundBtnBoard) soundBtnBoard.addEventListener("click", toggleSound);

    // Tombol Mulai
    const btnStart = document.getElementById("btn-start-game");
    if (btnStart) {
      btnStart.addEventListener("click", () => {
        playSound("click");
        showScreen("screen-setup");
      });
    }

    // Tombol Main Lagi dengan kelompok terakhir
    const btnResume = document.getElementById("btn-resume-previous");
    if (btnResume) {
      btnResume.addEventListener("click", () => {
        playSound("click");
        startWithPreviousGroups();
      });
    }

    // Modal Tentang & Cara Main & Peringkat dari Layar Awal
    const btnAbout = document.getElementById("btn-about");
    if (btnAbout) btnAbout.addEventListener("click", () => { playSound("click"); openModal("modal-about"); });

    const btnRules = document.getElementById("btn-how-to-play");
    if (btnRules) btnRules.addEventListener("click", () => { playSound("click"); openModal("modal-rules"); });

    const btnLead = document.getElementById("btn-view-leaderboard");
    if (btnLead) btnLead.addEventListener("click", () => {
      playSound("click");
      renderLeaderboardTable();
      showScreen("screen-leaderboard");
    });

    const btnBackStart = document.getElementById("btn-back-to-start");
    if (btnBackStart) btnBackStart.addEventListener("click", () => { playSound("click"); navigateToMenu(); });

    const btnBackLead = document.getElementById("btn-back-from-leaderboard");
    if (btnBackLead) btnBackLead.addEventListener("click", () => { playSound("click"); navigateToMenu(); });
  }

  // ==========================================================================
  // EVENT LISTENER: SETUP KELOMPOK CEPAT
  // ==========================================================================
  function initSetupEvents() {
    // Pemilihan jumlah kelompok (2, 3, 4, 5) - SATU KETUKAN LANGSUNG MULAI
    const countBtns = document.querySelectorAll(".btn-count-choice");
    countBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        playSound("click");
        const count = parseInt(btn.getAttribute("data-count"), 10);
        createGroupsAndProceed(count);
      });
    });

    // Ubah nama kelompok
    const btnEditNames = document.getElementById("btn-edit-group-names");
    if (btnEditNames) {
      btnEditNames.addEventListener("click", () => {
        playSound("click");
        renderEditNamesModal();
        openModal("modal-edit-names");
      });
    }

    const btnSaveNames = document.getElementById("btn-save-custom-names");
    if (btnSaveNames) {
      btnSaveNames.addEventListener("click", () => {
        playSound("click");
        saveCustomNames();
        closeModal("modal-edit-names");
      });
    }

    // Lanjut dari modal peran ke papan kasus
    const btnProceed = document.getElementById("btn-proceed-to-game");
    if (btnProceed) {
      btnProceed.addEventListener("click", () => {
        playSound("click");
        closeModal("modal-role-reminder");
        startNewCaseSession();
      });
    }
  }

  function createGroupsAndProceed(count) {
    State.groupCount = count;
    State.groups = [];

    for (let i = 0; i < count; i++) {
      const def = KELOMPOK_DEFAULT[i] || {
        id: `tim${i + 1}`,
        nama: `Tim ${i + 1}`,
        warna: "#2874A6",
        warnaBorder: "#1B4F72",
        warnaTeks: "#FFFFFF"
      };
      State.groups.push({
        id: def.id,
        nama: def.nama,
        warna: def.warna,
        warnaBorder: def.warnaBorder,
        warnaTeks: def.warnaTeks,
        skor: 0,
        correctTimes: [],
        correctCount: 0
      });
    }

    saveCurrentGroupsToStorage();

    // Muncul HANYA pada permainan pertama setelah halaman dibuka (disimpan di memori)
    if (!State.hasShownRoleReminder) {
      State.hasShownRoleReminder = true;
      openModal("modal-role-reminder");
    } else {
      startNewCaseSession();
    }
  }

  function saveCurrentGroupsToStorage() {
    try {
      localStorage.setItem(STORAGE_KEYS.GROUPS, JSON.stringify({
        count: State.groupCount,
        groups: State.groups.map(g => ({
          id: g.id,
          nama: g.nama,
          warna: g.warna,
          warnaBorder: g.warnaBorder,
          warnaTeks: g.warnaTeks
        }))
      }));
    } catch (e) {}
  }

  function startWithPreviousGroups() {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.GROUPS);
      if (saved) {
        const data = JSON.parse(saved);
        if (data && Array.isArray(data.groups) && data.groups.length >= 2) {
          State.groupCount = data.groups.length;
          State.groups = data.groups.map(g => ({
            id: g.id,
            nama: g.nama,
            warna: g.warna,
            warnaBorder: g.warnaBorder,
            warnaTeks: g.warnaTeks,
            skor: 0,
            correctTimes: [],
            correctCount: 0
          }));
          if (!State.hasShownRoleReminder) {
            State.hasShownRoleReminder = true;
            openModal("modal-role-reminder");
          } else {
            startNewCaseSession();
          }
          return;
        }
      }
    } catch (e) {}

    // Fallback bila data tidak valid
    createGroupsAndProceed(4);
  }

  function renderEditNamesModal() {
    const container = document.getElementById("edit-names-inputs-container");
    if (!container) return;
    container.innerHTML = "";

    // Tampilkan 5 baris nama kelompok default
    KELOMPOK_DEFAULT.forEach((team, idx) => {
      const row = document.createElement("div");
      row.className = "name-edit-row";
      row.innerHTML = `
        <span class="team-color-dot" style="background-color: ${team.warna};"></span>
        <label style="min-width: 90px; font-weight: 800;">Kelompok ${idx + 1}:</label>
        <input type="text" class="name-edit-input" id="custom-name-${idx}" value="${team.nama}" maxlength="20">
      `;
      container.appendChild(row);
    });
  }

  function saveCustomNames() {
    KELOMPOK_DEFAULT.forEach((team, idx) => {
      const input = document.getElementById(`custom-name-${idx}`);
      if (input && input.value.trim().length > 0) {
        team.nama = input.value.trim();
      }
    });

    try {
      localStorage.setItem(STORAGE_KEYS.CUSTOM_NAMES, JSON.stringify(KELOMPOK_DEFAULT.map(k => k.nama)));
    } catch (e) {}

    updateSetupNamesPreview();

    // Jika state groups sudah terbentuk, sinkronkan
    if (State.groups.length > 0) {
      State.groups.forEach((g, idx) => {
        if (KELOMPOK_DEFAULT[idx]) {
          g.nama = KELOMPOK_DEFAULT[idx].nama;
        }
      });
      saveCurrentGroupsToStorage();
    }
  }

  // ==========================================================================
  // LOGIKA PENGACAKAN SESI KASUS (FISHER-YATES SESUAI PRD 7)
  // 12 Kasus: 8 dasar (2 per norma) + 4 HOTS (1 per norma)
  // ==========================================================================
  function shuffleArray(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const temp = a[i];
      a[i] = a[j];
      a[j] = temp;
    }
    return a;
  }

  function composeSessionCases() {
    const norms = ["agama", "kesusilaan", "kesopanan", "hukum"];
    const chosenBasic = [];
    const chosenHots = [];

    norms.forEach(normId => {
      const basicForNorm = KASUS_POOL.filter(k => k.jawabanId === normId && k.tingkat === "dasar");
      const hotsForNorm = KASUS_POOL.filter(k => k.jawabanId === normId && k.tingkat === "hots");

      // Prioritaskan kasus yang belum muncul di sesi sebelumnya
      const unusedBasic = shuffleArray(basicForNorm.filter(k => !State.lastSessionCaseIds.has(k.id)));
      const usedBasic = shuffleArray(basicForNorm.filter(k => State.lastSessionCaseIds.has(k.id)));
      const combinedBasic = [...unusedBasic, ...usedBasic];

      const unusedHots = shuffleArray(hotsForNorm.filter(k => !State.lastSessionCaseIds.has(k.id)));
      const usedHots = shuffleArray(hotsForNorm.filter(k => State.lastSessionCaseIds.has(k.id)));
      const combinedHots = [...unusedHots, ...usedHots];

      // Ambil 2 dasar dan 1 hots per norma
      chosenBasic.push(combinedBasic[0], combinedBasic[1]);
      chosenHots.push(combinedHots[0]);
    });

    // Simpan daftar ID yang terpilih untuk sesi berikutnya
    const fullSession = shuffleArray([...chosenBasic, ...chosenHots]);
    State.lastSessionCaseIds = new Set(fullSession.map(k => k.id));
    return fullSession;
  }

  function startNewCaseSession() {
    // Reset skor dan catatan waktu setiap tim untuk sesi baru
    State.groups.forEach(g => {
      g.skor = 0;
      g.correctTimes = [];
      g.correctCount = 0;
    });

    State.sessionCases = composeSessionCases();
    State.currentCaseIndex = 0;
    State.unsolvedCases = [];

    showScreen("screen-board");
    loadCase(0);
  }

  // ==========================================================================
  // EVENT LISTENER: PAPAN KASUS (BOARD)
  // ==========================================================================
  function initBoardEvents() {
    // Tombol Menu di header papan kasus
    const btnMenu = document.getElementById("btn-board-menu");
    if (btnMenu) btnMenu.addEventListener("click", navigateToMenu);

    // Tombol Guru: Buka Petunjuk Berikutnya
    const btnUnlock = document.getElementById("btn-unlock-clue");
    if (btnUnlock) btnUnlock.addEventListener("click", handleUnlockNextClue);

    // Tombol Guru: Batalkan Giliran
    const btnCancel = document.getElementById("btn-cancel-turn");
    if (btnCancel) btnCancel.addEventListener("click", handleCancelTurn);

    // Tombol Guru: Jeda Game
    const btnPause = document.getElementById("btn-pause-game");
    if (btnPause) btnPause.addEventListener("click", handleTogglePause);

    // Tombol Guru: Selesai Sekarang
    const btnFinish = document.getElementById("btn-finish-now");
    if (btnFinish) btnFinish.addEventListener("click", handleFinishNow);

    // Tombol 4 Stempel Norma
    const stampBtns = document.querySelectorAll(".norma-stamp");
    stampBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const normaId = btn.getAttribute("data-norma");
        handleStampAnswer(normaId);
      });
    });

    // Tombol Evaluasi Alasan Guru (Tahan 1 detik untuk Masuk Akal)
    setupHoldReasonButton();

    const btnReasonPass = document.getElementById("btn-reason-pass");
    if (btnReasonPass) {
      btnReasonPass.addEventListener("click", () => {
        playSound("click");
        evaluateReason(false);
      });
    }

    // Tombol Lanjut ke Kasus Berikutnya
    const btnNext = document.getElementById("btn-next-case");
    if (btnNext) {
      btnNext.addEventListener("click", () => {
        playSound("click");
        goToNextCase();
      });
    }
  }

  // ==========================================================================
  // PEMUATAN KASUS KE PAPAN (STEP BY STEP)
  // ==========================================================================
  function loadCase(index) {
    if (index >= State.sessionCases.length) {
      finishGameSession();
      return;
    }

    const currentCase = State.sessionCases[index];
    State.currentCaseIndex = index;
    State.currentClueIndex = 1;
    State.isCaseAnswered = false;
    State.reasonEvaluated = false;
    State.isProcessingAnswer = false;
    State.activeGroupIndex = null;
    State.lockedGroupsForCase.clear();
    State.lockedNormasForCase.clear();

    // Reset status 4 stempel norma ke kondisi menunggu giliran
    document.querySelectorAll(".norma-stamp").forEach(b => {
      b.classList.remove("locked", "active", "stamping-down");
      b.classList.add("disabled");
      b.disabled = true;
    });

    // Sembunyikan elemen evaluasi dan stempel terpecahkan
    const stampSolved = document.getElementById("stamp-terpecahkan");
    if (stampSolved) stampSolved.classList.remove("show");

    const feedbackBar = document.getElementById("case-feedback-bar");
    if (feedbackBar) feedbackBar.style.display = "none";

    const reasonPanel = document.getElementById("reason-panel");
    if (reasonPanel) reasonPanel.style.display = "none";

    const explanationBox = document.getElementById("explanation-box");
    if (explanationBox) explanationBox.style.display = "none";

    const teacherEvalBox = document.getElementById("teacher-reason-actions");
    if (teacherEvalBox) teacherEvalBox.style.display = "none";

    const hotsBox = document.getElementById("hots-question-box");
    if (hotsBox) hotsBox.style.display = "none";

    const hotsGuide = document.getElementById("hots-question-guide");
    if (hotsGuide) {
      hotsGuide.textContent = "";
      hotsGuide.style.display = "none";
    }

    // Update Progres & Indikator Kasus
    const progressText = document.getElementById("case-progress-text");
    if (progressText) {
      progressText.textContent = `Kasus ${index + 1} dari ${State.sessionCases.length}`;
    }

    const hotsBadge = document.getElementById("hots-indicator");
    if (hotsBadge) {
      hotsBadge.style.display = currentCase.tingkat === "hots" ? "inline-block" : "none";
    }

    const caseBadgeNum = document.getElementById("folder-case-number");
    if (caseBadgeNum) {
      const numStr = (index + 1) < 10 ? `0${index + 1}` : `${index + 1}`;
      caseBadgeNum.textContent = `BERKAS KASUS #${numStr} (${currentCase.tingkat.toUpperCase()})`;
    }

    const caseTarget = document.getElementById("case-target-indicator");
    if (caseTarget) {
      caseTarget.textContent = "PILIH KELOMPOK DI SEBELAH KIRI";
      caseTarget.className = "case-target-badge";
    }

    // Teks Kasus
    const caseText = document.getElementById("folder-case-text");
    if (caseText) caseText.textContent = currentCase.kasus;

    // Pasang 3 Petunjuk (Petunjuk 1 Terbuka Otomatis Sesuai PRD 6.3)
    renderClues(currentCase, 1);

    // Render daftar tim di sidebar
    renderTeamsSidebar();

    // Matikan stempel sampai guru memilih kelompok
    disableStamps();

    // Update tombol guru
    updateTeacherControls();

    // Mulai timer berpikir kasus
    startTimer();
  }

  function renderClues(caseData, unlockedUpTo) {
    for (let i = 1; i <= 3; i++) {
      const slot = document.getElementById(`clue-slot-${i}`);
      if (!slot) continue;

      const clueParagraph = slot.querySelector(".clue-text");
      if (i <= unlockedUpTo) {
        slot.classList.remove("locked");
        slot.classList.add("unlocked");
        if (clueParagraph) clueParagraph.textContent = caseData.petunjuk[i - 1];
      } else {
        slot.classList.remove("unlocked");
        slot.classList.add("locked");
        if (clueParagraph) clueParagraph.textContent = "Terkunci...";
      }
    }
  }

  function renderTeamsSidebar(popGroupIndex = null) {
    const container = document.getElementById("teams-list-container");
    if (!container) return;
    container.innerHTML = "";

    State.groups.forEach((team, idx) => {
      const card = document.createElement("button");
      card.className = "team-card-btn";
      card.setAttribute("type", "button");

      const isActive = State.activeGroupIndex === idx;
      const isLocked = State.lockedGroupsForCase.has(idx);

      if (isActive) card.classList.add("active-turn");
      if (isLocked) card.classList.add("locked-out");

      const avgTime = calculateAverageTime(team.correctTimes);
      const timeStr = team.correctCount > 0 ? `Rata2: ${avgTime.toFixed(1)}s` : "Belum ada rekor";
      const isPopped = popGroupIndex === idx;

      card.innerHTML = `
        <div class="team-card-top">
          <div style="display: flex; align-items: center;">
            <span class="team-color-dot" style="background-color: ${team.warna};"></span>
            <span class="team-name-text">${team.nama}</span>
          </div>
          <span class="team-score-badge ${isPopped ? 'score-pop' : ''}">${team.skor} Poin</span>
        </div>
        <div class="team-time-stat">${timeStr} (${team.correctCount} benar)</div>
      `;

      card.addEventListener("click", () => {
        handleSelectGroupTurn(idx);
      });

      container.appendChild(card);
    });
  }

  function calculateAverageTime(timesArr) {
    if (!timesArr || timesArr.length === 0) return 0;
    const sum = timesArr.reduce((a, b) => a + b, 0);
    return sum / timesArr.length;
  }

  // ==========================================================================
  // LOGIKA PEMILIHAN KELOMPOK OLEH GURU
  // ==========================================================================
  function handleSelectGroupTurn(groupIndex) {
    // Tidak bisa memilih kelompok jika kasus sudah terjawab, atau kelompok tersebut terkunci untuk kasus ini
    if (State.isCaseAnswered) return;
    if (State.lockedGroupsForCase.has(groupIndex)) return;
    if (State.isPaused) return;

    playSound("click");
    State.activeGroupIndex = groupIndex;

    const chosenGroup = State.groups[groupIndex];
    const caseTarget = document.getElementById("case-target-indicator");
    if (caseTarget) {
      caseTarget.textContent = `GILIRAN MENJAWAB: ${chosenGroup.nama.toUpperCase()}`;
      caseTarget.className = "case-target-badge active-group";
      caseTarget.style.borderColor = chosenGroup.warna;
    }

    // Aktifkan stempel hanya untuk kelompok terpilih
    enableStamps();

    // Render ulang sidebar untuk highlight
    renderTeamsSidebar();

    // Aktifkan tombol Batalkan
    updateTeacherControls();
  }

  function handleCancelTurn() {
    if (State.activeGroupIndex === null || State.isCaseAnswered) return;
    playSound("click");
    State.activeGroupIndex = null;

    const caseTarget = document.getElementById("case-target-indicator");
    if (caseTarget) {
      caseTarget.textContent = "PILIH KELOMPOK DI SEBELAH KIRI";
      caseTarget.className = "case-target-badge";
      caseTarget.style.borderColor = "";
    }

    disableStamps();
    renderTeamsSidebar(State.activeGroupIndex);
    updateTeacherControls();
  }

  // ==========================================================================
  // KONTROL STEMPEL NORMA
  // ==========================================================================
  function enableStamps() {
    const stampBtns = document.querySelectorAll(".norma-stamp");
    stampBtns.forEach(btn => {
      const normaId = btn.getAttribute("data-norma");
      if (State.lockedNormasForCase && State.lockedNormasForCase.has(normaId)) {
        btn.disabled = true;
        btn.classList.add("locked");
        btn.classList.remove("active");
        btn.classList.add("disabled");
      } else {
        btn.disabled = false;
        btn.classList.remove("disabled");
        btn.classList.remove("locked");
        btn.classList.add("active");
      }
    });
  }

  function disableStamps() {
    const stampBtns = document.querySelectorAll(".norma-stamp");
    stampBtns.forEach(btn => {
      btn.disabled = true;
      btn.classList.remove("active");
      const normaId = btn.getAttribute("data-norma");
      if (State.lockedNormasForCase && State.lockedNormasForCase.has(normaId)) {
        btn.classList.add("locked");
      } else {
        btn.classList.remove("locked");
      }
      btn.classList.add("disabled");
    });
  }

  // ==========================================================================
  // JAWABAN KASUS (CEK HANYA DENGAN MEMBANDINGKAN jawabanId)
  // ==========================================================================
  function handleStampAnswer(chosenNormaId) {
    if (State.activeGroupIndex === null || State.isCaseAnswered || State.isPaused || State.isProcessingAnswer) return;
    State.isProcessingAnswer = true;

    // Hentikan timer berpikir kelompok untuk kasus ini
    pauseTimer();
    const thoughtTime = Math.min(State.timerSeconds, 180);

    const currentCase = State.sessionCases[State.currentCaseIndex];
    const answeringGroup = State.groups[State.activeGroupIndex];

    // Animasi fisik stempel turun ke bawah singkat saat ditekan
    const stampBtn = document.querySelector(`.norma-stamp[data-norma="${chosenNormaId}"]`);
    if (stampBtn) {
      stampBtn.classList.add("stamping-down");
    }

    // Mainkan efek suara ketukan
    playSound("click");

    setTimeout(() => {
      if (stampBtn) {
        stampBtn.classList.remove("stamping-down");
      }

      // Perbandingan ketat id norma
      const isCorrect = chosenNormaId === currentCase.jawabanId;

      if (isCorrect) {
        handleAnswerCorrect(answeringGroup, currentCase, thoughtTime);
      } else {
        // Norma salah ditandai terkunci untuk kasus ini
        if (!State.lockedNormasForCase) State.lockedNormasForCase = new Set();
        State.lockedNormasForCase.add(chosenNormaId);
        handleAnswerWrong(answeringGroup, currentCase);
      }
    }, 120);
  }

  function handleAnswerCorrect(group, caseItem, timeSpent) {
    State.isCaseAnswered = true;
    State.isProcessingAnswer = false;
    disableStamps();

    // Hitung poin tebakan berdasarkan petunjuk yang sedang terbuka:
    // Petunjuk 1 = 3 poin, Petunjuk 2 = 2 poin, Petunjuk 3 = 1 poin
    let points = 1;
    if (State.currentClueIndex === 1) points = 3;
    else if (State.currentClueIndex === 2) points = 2;

    group.skor += points;
    group.correctTimes.push(timeSpent);
    group.correctCount += 1;
    if (caseItem.tingkat === "hots") {
      group.hotsCount = (group.hotsCount || 0) + 1;
    }

    // Efek visual kilau emas dan getaran berkas saat stempel mendarat
    const folder = document.getElementById("case-folder");
    if (folder) {
      folder.classList.add("correct-glow");
      folder.classList.add("stamp-bounce");
      setTimeout(() => folder.classList.remove("correct-glow"), 650);
      setTimeout(() => folder.classList.remove("stamp-bounce"), 350);
    }

    // Tampilkan stempel TERPECAHKAN di zona stempel aman (kanan bawah)
    const stampSolved = document.getElementById("stamp-terpecahkan");
    if (stampSolved) stampSolved.classList.add("show");

    // Suara stempel fisik Web Audio dimainkan tepat saat stempel mendarat (140 ms)
    setTimeout(() => playSound("stamp"), 140);

    // Suara sukses ceria menyusul setelah stempel mantap mendarat
    setTimeout(() => playSound("correct"), 340);

    // Tampilkan Feedback Banner Ceria di atas panel aksi (In-Place seperti Pict 3)
    const feedbackBar = document.getElementById("case-feedback-bar");
    const feedbackText = document.getElementById("feedback-text");
    const feedbackIcon = document.getElementById("feedback-icon");
    if (feedbackBar && feedbackText) {
      feedbackBar.className = "feedback-banner success";
      if (feedbackIcon) feedbackIcon.innerHTML = '<svg class="ui-icon ui-icon-lg" aria-hidden="true"><use href="#icon-star"></use></svg>';
      feedbackText.textContent = `Tepat Sekali! ${group.nama} berhasil memecahkan kasus (+${points} Poin)!`;
      feedbackBar.style.display = "flex";
    }

    // Siapkan Panel Evaluasi Alasan In-Place (Fase 1: Alasan & Evaluasi Guru)
    const reasonPanel = document.getElementById("reason-panel");
    const hotsBox = document.getElementById("hots-question-box");
    const hotsLabel = document.getElementById("hots-prompt-label");
    const hotsQuestionText = document.getElementById("hots-question-text");
    const hotsGuide = document.getElementById("hots-question-guide");
    const teacherEvalBox = document.getElementById("teacher-reason-actions");
    const labelBtnSensible = document.getElementById("label-btn-sensible");
    const explanationBox = document.getElementById("explanation-box");

    const extra = caseItem.tingkat === "hots" ? 2 : 1;
    if (labelBtnSensible) {
      labelBtnSensible.textContent = `Alasan Masuk Akal (+${extra} Poin - Tahan 1 Detik)`;
    }

    const normaObj = NORMA_LIST.find(n => n.id === caseItem.jawabanId);
    const namaNorma = normaObj ? normaObj.nama : caseItem.jawabanId;

    if (caseItem.tingkat === "hots" && caseItem.pertanyaanLanjutan) {
      if (hotsBox && hotsQuestionText) {
        if (hotsLabel) hotsLabel.textContent = "Pertanyaan Lanjutan Kasus (HOTS):";
        hotsQuestionText.textContent = caseItem.pertanyaanLanjutan;
        if (hotsGuide && caseItem.alasan) {
          hotsGuide.textContent = `Panduan Guru: "${caseItem.alasan}"`;
          hotsGuide.style.display = "block";
        } else if (hotsGuide) {
          hotsGuide.style.display = "none";
        }
        hotsBox.className = "hots-prompt-box";
        hotsBox.style.display = "block";
      }
    } else {
      // Kasus Dasar: tampilkan panduan alasan lisan detektif agar tidak kosong
      if (hotsBox && hotsQuestionText) {
        if (hotsLabel) hotsLabel.textContent = "Tantangan Alasan Detektif (Lisan):";
        hotsQuestionText.textContent = `Mengapa perbuatan ini termasuk dalam ${namaNorma}?`;
        if (hotsGuide && caseItem.alasan) {
          hotsGuide.textContent = `Panduan Guru: "${caseItem.alasan}"`;
          hotsGuide.style.display = "block";
        } else if (hotsGuide) {
          hotsGuide.style.display = "none";
        }
        hotsBox.className = "hots-prompt-box basic-mode";
        hotsBox.style.display = "block";
      }
    }

    if (teacherEvalBox) teacherEvalBox.style.display = "block";
    if (explanationBox) explanationBox.style.display = "none";

    // Buka panel evaluasi alasan in-place setelah stempel selesai mendarat (250ms)
    setTimeout(() => {
      if (reasonPanel) reasonPanel.style.display = "flex";
    }, 250);

    renderTeamsSidebar(State.activeGroupIndex);
    updateTeacherControls();
  }

  function handleAnswerWrong(group, caseItem) {
    // Kunci kelompok ini untuk kasus ini (0 poin, tidak dicatat waktunya)
    State.lockedGroupsForCase.add(State.activeGroupIndex);
    State.activeGroupIndex = null;
    State.isProcessingAnswer = false;
    disableStamps();

    // Suara turun lembut
    setTimeout(() => playSound("wrong"), 100);

    // Animasi goyang lembut pada folder berkas
    const folder = document.getElementById("case-folder");
    if (folder) {
      folder.classList.add("shake-soft");
      setTimeout(() => folder.classList.remove("shake-soft"), 400);
    }

    // Tampilkan pesan ramah
    const feedbackBar = document.getElementById("case-feedback-bar");
    const feedbackText = document.getElementById("feedback-text");
    const feedbackIcon = document.getElementById("feedback-icon");
    if (feedbackBar && feedbackText) {
      feedbackBar.className = "feedback-banner soft-wrong";
      if (feedbackIcon) feedbackIcon.innerHTML = '<svg class="ui-icon ui-icon-lg" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>';
      feedbackText.textContent = `Coba lagi, ${group.nama}. Pikirkan sumber aturan dan alasan perilaku itu dilakukan.`;
      feedbackBar.style.display = "flex";
    }

    const caseTarget = document.getElementById("case-target-indicator");
    if (caseTarget) {
      caseTarget.textContent = "PILIH KELOMPOK LAIN DI SEBELAH KIRI";
      caseTarget.className = "case-target-badge";
      caseTarget.style.borderColor = "";
    }

    // Buka petunjuk berikutnya otomatis agar kelompok lain bisa menebak
    if (State.currentClueIndex < 3) {
      State.currentClueIndex++;
      renderClues(caseItem, State.currentClueIndex);
    }

    renderTeamsSidebar();
    updateTeacherControls();

    // Cek jika semua kelompok sudah terkunci atau petunjuk 3 sudah gagal
    checkIfAllGroupsFailed();

    // Lanjutkan timer jika masih ada kelompok yang bisa menebak
    if (!State.isCaseAnswered && State.lockedGroupsForCase.size < State.groups.length) {
      resumeTimer();
    }
  }

  function checkIfAllGroupsFailed() {
    if (State.isCaseAnswered) return;

    if (State.lockedGroupsForCase.size >= State.groups.length) {
      // Semua kelompok telah salah tebak pada kasus ini
      stopTimer();
      State.isCaseAnswered = true;
      disableStamps();

      const currentCase = State.sessionCases[State.currentCaseIndex];
      State.unsolvedCases.push(currentCase);

      const feedbackBar = document.getElementById("case-feedback-bar");
      const feedbackText = document.getElementById("feedback-text");
      const feedbackIcon = document.getElementById("feedback-icon");
      if (feedbackBar && feedbackText) {
        feedbackBar.className = "feedback-banner soft-wrong";
        if (feedbackIcon) feedbackIcon.innerHTML = '<svg class="ui-icon ui-icon-lg" aria-hidden="true"><use href="#icon-book"></use></svg>';
        const normaObj = NORMA_LIST.find(n => n.id === currentCase.jawabanId);
        const namaNorma = normaObj ? normaObj.nama : currentCase.jawabanId;
        feedbackText.textContent = `Waktu tebak selesai. Jawaban yang tepat adalah: ${namaNorma}.`;
        feedbackBar.style.display = "flex";
      }

      // Tampilkan penjelasan langsung
      showCaseExplanation(currentCase);
    }
  }

  // ==========================================================================
  // EVALUASI ALASAN OLEH GURU (TAHAN 1 DETIK)
  // ==========================================================================
  function setupHoldReasonButton() {
    const btnHold = document.getElementById("btn-reason-sensible");
    const bar = document.getElementById("hold-reason-bar");
    if (!btnHold || !bar) return;

    let holdTimer = null;
    let holdProgress = 0;
    const HOLD_DURATION = 1000; // 1 detik
    const INTERVAL_TICK = 50;

    const startHold = (e) => {
      if (State.reasonEvaluated) return;
      holdProgress = 0;
      bar.style.width = "0%";

      holdTimer = setInterval(() => {
        holdProgress += INTERVAL_TICK;
        const pct = Math.min(100, (holdProgress / HOLD_DURATION) * 100);
        bar.style.width = `${pct}%`;

        if (holdProgress >= HOLD_DURATION) {
          clearInterval(holdTimer);
          holdTimer = null;
          bar.style.width = "0%";
          playSound("correct");
          evaluateReason(true);
        }
      }, INTERVAL_TICK);
    };

    const cancelHold = () => {
      if (holdTimer) {
        clearInterval(holdTimer);
        holdTimer = null;
        bar.style.width = "0%";
      }
    };

    btnHold.addEventListener("pointerdown", startHold);
    btnHold.addEventListener("pointerup", cancelHold);
    btnHold.addEventListener("pointerleave", cancelHold);
    btnHold.addEventListener("pointercancel", cancelHold);
  }

  function evaluateReason(isSensible) {
    if (State.reasonEvaluated) return;
    State.reasonEvaluated = true;

    const currentCase = State.sessionCases[State.currentCaseIndex];
    const group = State.groups[State.activeGroupIndex];

    if (isSensible && group) {
      // Poin alasan: kasus dasar = +1 poin, kasus HOTS = +2 poin
      const extra = currentCase.tingkat === "hots" ? 2 : 1;
      group.skor += extra;
      group.reasonCount = (group.reasonCount || 0) + 1;
      renderTeamsSidebar(State.activeGroupIndex);
    }

    // Update teks feedback banner
    const feedbackBar = document.getElementById("case-feedback-bar");
    const feedbackText = document.getElementById("feedback-text");
    if (feedbackBar && feedbackText && group) {
      if (isSensible) {
        const extra = currentCase.tingkat === "hots" ? 2 : 1;
        feedbackText.textContent = `Hebat, ${group.nama}! Alasan lisan diterima (+${extra} Poin Alasan).`;
      } else {
        feedbackText.textContent = `Penyelidikan kasus selesai. Simak penjelasan norma di bawah ini:`;
      }
    }

    // Transisi ke Fase 2: sembunyikan pertanyaan HOTS & tombol evaluasi guru
    const hotsBox = document.getElementById("hots-question-box");
    if (hotsBox) hotsBox.style.display = "none";

    const hotsGuide = document.getElementById("hots-question-guide");
    if (hotsGuide) {
      hotsGuide.textContent = "";
      hotsGuide.style.display = "none";
    }

    const teacherEvalBox = document.getElementById("teacher-reason-actions");
    if (teacherEvalBox) teacherEvalBox.style.display = "none";

    showCaseExplanation(currentCase);
  }

  function showCaseExplanation(caseItem) {
    const reasonPanel = document.getElementById("reason-panel");
    const explanationBox = document.getElementById("explanation-box");
    const expText = document.getElementById("case-explanation-text");
    const hotsBox = document.getElementById("hots-question-box");
    const teacherEvalBox = document.getElementById("teacher-reason-actions");

    if (hotsBox) hotsBox.style.display = "none";
    if (teacherEvalBox) teacherEvalBox.style.display = "none";

    if (reasonPanel) {
      reasonPanel.style.display = "flex";
    }

    if (explanationBox) explanationBox.style.display = "block";

    if (expText) {
      const normaObj = NORMA_LIST.find(n => n.id === caseItem.jawabanId);
      const namaNorma = normaObj ? normaObj.nama : caseItem.jawabanId;
      expText.innerHTML = `<strong>Kategori: ${namaNorma}</strong><br>${caseItem.penjelasan}`;
    }
  }

  function goToNextCase() {
    loadCase(State.currentCaseIndex + 1);
  }

  // ==========================================================================
  // TOMBOL KENDALI GURU
  // ==========================================================================
  function handleUnlockNextClue() {
    if (State.currentClueIndex >= 3 || State.isCaseAnswered) return;
    playSound("click");
    State.currentClueIndex++;
    const currentCase = State.sessionCases[State.currentCaseIndex];
    renderClues(currentCase, State.currentClueIndex);
    updateTeacherControls();
  }

  function handleTogglePause() {
    playSound("click");
    const pauseIcon = document.getElementById("pause-icon");
    const pauseText = document.getElementById("pause-text");

    if (State.isPaused) {
      // Lanjutkan
      State.isPaused = false;
      resumeTimer();
      if (pauseIcon) pauseIcon.innerHTML = '<svg class="ui-icon ui-icon-inline" aria-hidden="true"><use href="#icon-pause"></use></svg>';
      if (pauseText) pauseText.textContent = "Jeda Game";
      if (State.activeGroupIndex !== null && !State.isCaseAnswered) {
        enableStamps();
      }
    } else {
      // Jeda
      State.isPaused = true;
      pauseTimer();
      if (pauseIcon) pauseIcon.innerHTML = '<svg class="ui-icon ui-icon-inline" aria-hidden="true"><use href="#icon-play"></use></svg>';
      if (pauseText) pauseText.textContent = "Lanjutkan Game";
      disableStamps();
    }
  }

  function handleFinishNow() {
    openConfirmModal(
      "Akhiri permainan sekarang? Hasil akan dihitung dari kasus yang sudah dimainkan.",
      () => {
        stopTimer();
        finishGameSession();
      }
    );
  }

  function updateTeacherControls() {
    const btnUnlock = document.getElementById("btn-unlock-clue");
    const btnCancel = document.getElementById("btn-cancel-turn");

    if (btnUnlock) {
      btnUnlock.disabled = State.currentClueIndex >= 3 || State.isCaseAnswered;
    }
    if (btnCancel) {
      btnCancel.disabled = State.activeGroupIndex === null || State.isCaseAnswered;
    }
  }

  // ==========================================================================
  // SISTEM PENGHITUNG WAKTU BERPIKIR (TIMER KASUS)
  // ==========================================================================
  function startTimer() {
    stopTimer();
    State.timerSeconds = 0;
    State.timerRunning = true;
    updateTimerDisplay();

    State.timerInterval = setInterval(() => {
      if (State.timerRunning && !State.isPaused) {
        State.timerSeconds++;
        updateTimerDisplay();
        if (State.timerSeconds >= 180) {
          // Batas 180 detik
          pauseTimer();
        }
      }
    }, 1000);
  }

  function pauseTimer() {
    State.timerRunning = false;
  }

  function resumeTimer() {
    if (State.timerSeconds < 180) {
      State.timerRunning = true;
    }
  }

  function stopTimer() {
    State.timerRunning = false;
    if (State.timerInterval) {
      clearInterval(State.timerInterval);
      State.timerInterval = null;
    }
  }

  function updateTimerDisplay() {
    const el = document.getElementById("timer-display");
    if (!el) return;
    const mins = Math.floor(State.timerSeconds / 60);
    const secs = State.timerSeconds % 60;
    const pad = (n) => (n < 10 ? `0${n}` : `${n}`);
    el.textContent = `${pad(mins)}:${pad(secs)}`;
  }

  // ==========================================================================
  // HASIL PERMAINAN & PERINGKAT KECEPATAN (FASE 6)
  // ==========================================================================
  function finishGameSession() {
    stopTimer();
    playSound("finish");

    // Simpan rekor kelompok ke daftar peringkat lokal jika memenuhi syarat (min 3 jawaban benar)
    saveEligibleGroupsToLeaderboard();

    // Render Layar Hasil
    renderResultScreen();
    showScreen("screen-result");

    // Mulai animasi confetti ringan
    launchConfetti();
  }

  function saveEligibleGroupsToLeaderboard() {
    const today = new Date().toLocaleDateString("id-ID", {
      day: "numeric",
      month: "short",
      year: "numeric"
    });

    let updated = false;

    State.groups.forEach(group => {
      if (group.correctCount >= 3) {
        const avg = calculateAverageTime(group.correctTimes);
        State.leaderboard.push({
          nama: group.nama,
          warna: group.warna,
          avgTime: avg,
          skor: group.skor,
          correctCount: group.correctCount,
          tanggal: today
        });
        updated = true;
      }
    });

    if (updated) {
      // Urutkan berdasarkan avgTime terkecil (makin cepat makin tinggi)
      State.leaderboard.sort((a, b) => a.avgTime - b.avgTime);
      // Batasi 10 teratas
      if (State.leaderboard.length > 10) {
        State.leaderboard = State.leaderboard.slice(0, 10);
      }
      try {
        localStorage.setItem(STORAGE_KEYS.LEADERBOARD, JSON.stringify(State.leaderboard));
      } catch (e) {}
    }
  }

  function formatAvgTime(avg) {
    if (!avg || isNaN(avg) || avg <= 0) return "0,0";
    return avg.toFixed(1).replace(".", ",");
  }

  function renderResultScreen() {
    // 1. Hitung avgTime untuk setiap kelompok
    State.groups.forEach(g => {
      g.avgTime = calculateAverageTime(g.correctTimes);
      g.badges = [];
      g.isTied = false;
    });

    // 2. Urutkan kelompok:
    //    Primer: skor tertinggi (b.skor - a.skor)
    //    Sekunder: jika skor sama, urutan tampil dari rata-rata waktu menjawab benar yang lebih cepat
    const sortedGroups = State.groups.slice().sort((a, b) => {
      if (b.skor !== a.skor) {
        return b.skor - a.skor;
      }
      const timeA = a.avgTime > 0 ? a.avgTime : 999999;
      const timeB = b.avgTime > 0 ? b.avgTime : 999999;
      return timeA - timeB;
    });

    // 3. Tentukan nomor peringkat & penanganan skor seri
    sortedGroups.forEach((g, idx) => {
      if (idx > 0) {
        const prev = sortedGroups[idx - 1];
        if (g.skor === prev.skor) {
          g.displayRank = prev.displayRank;
          g.isTied = true;
          prev.isTied = true;
        } else {
          g.displayRank = idx + 1;
        }
      } else {
        g.displayRank = 1;
      }
    });

    // 4. Hitung Lencana Resmi Sesuai FASE 2:
    //    HANYA 2 jenis lencana: "Skor Tertinggi" (emas) & "Tercepat" (teal/stopwatch)
    const maxScore = sortedGroups.length > 0 ? Math.max(...sortedGroups.map(g => g.skor)) : 0;
    if (maxScore > 0) {
      sortedGroups.forEach(g => {
        if (g.skor === maxScore) {
          g.badges.push({ id: "top-score", text: "Skor Tertinggi", icon: "#icon-trophy", type: "gold" });
        }
      });
    }

    // Lencana Tercepat: SATU kelompok tercepat DENGAN SYARAT minimal 3 jawaban benar
    const eligibleForFastest = sortedGroups.filter(g => g.correctCount >= 3 && g.avgTime > 0);
    if (eligibleForFastest.length > 0) {
      const minAvgTime = Math.min(...eligibleForFastest.map(g => g.avgTime));
      const fastestGroup = eligibleForFastest.find(g => Math.abs(g.avgTime - minAvgTime) < 0.001);
      if (fastestGroup) {
        fastestGroup.badges.push({ id: "fastest", text: "Tercepat", icon: "#icon-stopwatch", type: "teal" });
      }
    }

    // 5. Zona (b): Info Bar Ringkas (2 Item Saja: Kasus & Kecepatan Kelas)
    const totalCases = State.sessionCases.length || 12;
    const solvedCount = totalCases - State.unsolvedCases.length;
    const hlSolved = document.getElementById("hl-solved-count");
    if (hlSolved) hlSolved.textContent = `${solvedCount} dari ${totalCases} Kasus`;

    const allTimes = State.groups.flatMap(g => g.correctTimes);
    const classAvg = allTimes.length > 0 ? (allTimes.reduce((a, b) => a + b, 0) / allTimes.length) : 0;
    const hlSpeed = document.getElementById("hl-class-speed");
    if (hlSpeed) hlSpeed.textContent = `Rata-rata menjawab ${formatAvgTime(classAvg)} dtk`;

    let hasInsufficientAnswers = false;

    // 6. Zona (c): Susun Tampilan Podium Utama di Tengah
    const podiumContainer = document.getElementById("result-podium-container");
    const remainingContainer = document.getElementById("result-remaining-container");

    if (podiumContainer) {
      podiumContainer.innerHTML = "";

      const totalTeams = sortedGroups.length;
      let podiumTeams = [];

      if (totalTeams === 2) {
        // Untuk 2 kelompok: 2 balok (#1 di kiri/tengah, #2 di kanan)
        podiumTeams = [
          { group: sortedGroups[0], pedestal: "gold", posClass: "pos-center-2" },
          { group: sortedGroups[1], pedestal: "silver", posClass: "pos-side-2" }
        ];
      } else {
        // 3 atau lebih kelompok: podium 3 balok (#2 kiri, #1 tengah, #3 kanan)
        podiumTeams = [
          { group: sortedGroups[1], pedestal: "silver", posClass: "pos-left" },
          { group: sortedGroups[0], pedestal: "gold", posClass: "pos-center" },
          { group: sortedGroups[2], pedestal: "bronze", posClass: "pos-right" }
        ];
      }

      podiumTeams.forEach(item => {
        const g = item.group;
        if (!g) return;

        const col = document.createElement("div");
        col.className = `podium-col ${item.posClass}`;

        // Jika skor seri, tinggi balok dan warna mengikuti peringkat yang adil
        let pedestalType = item.pedestal;
        if (g.displayRank === 1) pedestalType = "gold";
        else if (g.displayRank === 2) pedestalType = "silver";
        else if (g.displayRank === 3) pedestalType = "bronze";

        // Lencana HTML (hanya jika ada)
        let badgesHtml = "";
        if (g.badges && g.badges.length > 0) {
          badgesHtml = `
            <div class="podium-badges">
              ${g.badges.map(b => `
                <span class="podium-badge badge-${b.type}">
                  <svg class="ui-icon ui-icon-inline" aria-hidden="true"><use href="${b.icon}"></use></svg>
                  <span>${b.text}</span>
                </span>
              `).join("")}
            </div>
          `;
        } else {
          badgesHtml = `<div class="podium-badges"></div>`;
        }

        // Teks waktu bersih: tampilkan waktu + bintang jika belum cukup 3 jawaban benar
        let timeInfoHtml = "";
        if (g.correctCount >= 3) {
          timeInfoHtml = `
            <div class="podium-time-info">
              <svg class="ui-icon ui-icon-inline" aria-hidden="true"><use href="#icon-stopwatch"></use></svg>
              <span>rata-rata ${formatAvgTime(g.avgTime)} dtk</span>
            </div>
          `;
        } else {
          hasInsufficientAnswers = true;
          timeInfoHtml = `
            <div class="podium-time-info">
              <svg class="ui-icon ui-icon-inline" aria-hidden="true"><use href="#icon-stopwatch"></use></svg>
              <span>rata-rata ${formatAvgTime(g.avgTime)} dtk<sup class="time-asterisk">*</sup></span>
            </div>
          `;
        }

        // Label Skor Sama pada balok peringkat jika seri
        const tieTagHtml = g.isTied ? `<span class="pedestal-tie-tag">Skor Sama</span>` : "";

        col.innerHTML = `
          <div class="podium-card" style="border-top: 6px solid ${g.warna};">
            ${badgesHtml}
            <div class="podium-team-header">
              <span class="team-color-dot" style="background-color: ${g.warna};"></span>
              <h3 class="podium-team-name">${g.nama}</h3>
            </div>
            <div class="podium-score" style="color: ${g.warna};">
              ${g.skor} <span class="podium-score-unit">Poin</span>
            </div>
            ${timeInfoHtml}
          </div>
          <div class="podium-pedestal pedestal-${pedestalType}">
            <div class="pedestal-rank-row">
              <div class="pedestal-rank-num">#${g.displayRank}</div>
              ${tieTagHtml}
            </div>
          </div>
        `;
        podiumContainer.appendChild(col);
      });

      // Pengungkapan Bertahap (Ceremonial Reveal)
      const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (!prefersReducedMotion) {
        podiumContainer.classList.add("ceremony-active");

        if (totalTeams === 2) {
          setTimeout(() => {
            const col2 = podiumContainer.querySelector(".pos-side-2");
            if (col2) {
              col2.classList.add("revealed");
              playSound("click");
            }
          }, 150);

          setTimeout(() => {
            const col1 = podiumContainer.querySelector(".pos-center-2");
            if (col1) {
              col1.classList.add("revealed");
              playSound("stamp");
              setTimeout(() => playSound("finish"), 200);
              launchConfetti();
            }
          }, 700);
        } else {
          // Langkah 1 (150ms): Juara 3
          setTimeout(() => {
            const col3 = podiumContainer.querySelector(".pos-right");
            if (col3) {
              col3.classList.add("revealed");
              playSound("click");
            }
          }, 150);

          // Langkah 2 (700ms): Juara 2
          setTimeout(() => {
            const col2 = podiumContainer.querySelector(".pos-left");
            if (col2) {
              col2.classList.add("revealed");
              playSound("click");
            }
          }, 700);

          // Langkah 3 (1300ms): Juara 1
          setTimeout(() => {
            const col1 = podiumContainer.querySelector(".pos-center");
            if (col1) {
              col1.classList.add("revealed");
              playSound("stamp");
              setTimeout(() => playSound("finish"), 200);
              launchConfetti();
            }
          }, 1300);
        }
      } else {
        podiumContainer.classList.remove("ceremony-active");
        podiumContainer.querySelectorAll(".podium-col").forEach(c => c.classList.add("revealed"));
        launchConfetti();
      }
    }

    // 7. Zona (d): Kelompok sisanya (Peringkat 4 dan 5 jika ada)
    if (remainingContainer) {
      remainingContainer.innerHTML = "";
      if (sortedGroups.length > 3) {
        remainingContainer.style.display = "flex";
        const remainingTeams = sortedGroups.slice(3);
        remainingTeams.forEach(g => {
          const card = document.createElement("div");
          card.className = "remaining-team-card";

          let badgesHtml = "";
          if (g.badges && g.badges.length > 0) {
            badgesHtml = g.badges.map(b => `
              <span class="podium-badge badge-${b.type}">
                <svg class="ui-icon ui-icon-inline" aria-hidden="true"><use href="${b.icon}"></use></svg>
                <span>${b.text}</span>
              </span>
            `).join("");
          }

          let timeText = "";
          if (g.correctCount >= 3) {
            timeText = `<svg class="ui-icon ui-icon-inline" aria-hidden="true"><use href="#icon-stopwatch"></use></svg> rata-rata ${formatAvgTime(g.avgTime)} dtk`;
          } else {
            hasInsufficientAnswers = true;
            timeText = `<svg class="ui-icon ui-icon-inline" aria-hidden="true"><use href="#icon-stopwatch"></use></svg> rata-rata ${formatAvgTime(g.avgTime)} dtk<sup class="time-asterisk">*</sup>`;
          }

          const tieTagHtml = g.isTied ? `<span class="pedestal-tie-tag">Skor Sama</span>` : "";

          card.innerHTML = `
            <div class="remaining-team-info">
              <div class="remaining-rank-wrap">
                <span class="remaining-rank">#${g.displayRank}</span>
                ${tieTagHtml}
              </div>
              <span class="team-color-dot" style="background-color: ${g.warna};"></span>
              <strong class="remaining-name">${g.nama}</strong>
              ${badgesHtml ? `<div class="remaining-badges">${badgesHtml}</div>` : ""}
            </div>
            <div class="remaining-stats">
              <span class="remaining-time">${timeText}</span>
              <span class="remaining-score" style="background-color: ${g.warna};">${g.skor} Poin</span>
            </div>
          `;
          remainingContainer.appendChild(card);
        });
      } else {
        remainingContainer.style.display = "none";
      }
    }

    // Tampilkan / sembunyikan catatan kaki tanda bintang
    const footnoteEl = document.getElementById("result-speed-footnote");
    if (footnoteEl) {
      footnoteEl.style.display = hasInsufficientAnswers ? "block" : "none";
    }

    // 8. Zona (e): Strip Bawah (Pertanyaan Refleksi HOTS Terakhir & Kasus Unsolved)
    const playedCases = State.sessionCases.slice(0, State.currentCaseIndex + 1);
    const lastHotsCase = playedCases.slice().reverse().find(k => k.tingkat === "hots" && k.pertanyaanLanjutan);
    const reflectionCard = document.getElementById("result-reflection-card");
    const hlReflection = document.getElementById("hl-reflection-question");
    if (reflectionCard && hlReflection) {
      if (lastHotsCase && lastHotsCase.pertanyaanLanjutan) {
        reflectionCard.style.display = "flex";
        hlReflection.textContent = `"${lastHotsCase.pertanyaanLanjutan}"`;
      } else {
        // Sembunyikan bila tidak ada kasus HOTS yang dimainkan
        reflectionCard.style.display = "none";
      }
    }

    const unsolvedBox = document.getElementById("result-unsolved-box");
    if (unsolvedBox) {
      unsolvedBox.innerHTML = "";
      if (State.unsolvedCases.length === 0) {
        unsolvedBox.innerHTML = `
          <div class="unsolved-compact-success">
            <svg class="ui-icon ui-icon-inline" aria-hidden="true"><use href="#icon-check"></use></svg>
            <span>Semua kasus terpecahkan dengan baik!</span>
          </div>
        `;
      } else {
        const toShow = State.unsolvedCases.slice(0, 3);
        const pillsHtml = toShow.map((item, idx) => {
          const normaObj = NORMA_LIST.find(n => n.id === item.jawabanId);
          const namaNorma = normaObj ? normaObj.nama : item.jawabanId;
          return `
            <div class="unsolved-compact-pill" title="${item.kasus}: ${item.penjelasan}">
              <strong>Kasus #${idx + 1}</strong>
              <span class="unsolved-norma-tag">${namaNorma}</span>
              <span class="unsolved-snippet">${item.kasus}</span>
            </div>
          `;
        }).join("");

        unsolvedBox.innerHTML = `
          <div class="unsolved-compact-content">
            <span class="unsolved-compact-label">
              <svg class="ui-icon ui-icon-inline" aria-hidden="true"><use href="#icon-document"></use></svg>
              <strong>Kasus yang perlu dibahas (${toShow.length}):</strong>
            </span>
            <div class="unsolved-compact-items">
              ${pillsHtml}
            </div>
          </div>
        `;
      }
    }
  }

  function initResultEvents() {
    const btnReplay = document.getElementById("btn-result-replay-same");
    if (btnReplay) {
      btnReplay.addEventListener("click", () => {
        playSound("click");
        startNewCaseSession();
      });
    }

    const btnLead = document.getElementById("btn-result-leaderboard");
    if (btnLead) {
      btnLead.addEventListener("click", () => {
        playSound("click");
        renderLeaderboardTable();
        showScreen("screen-leaderboard");
      });
    }

    const btnMenu = document.getElementById("btn-result-menu");
    if (btnMenu) {
      btnMenu.addEventListener("click", () => {
        playSound("click");
        navigateToMenu();
      });
    }
  }

  // ==========================================================================
  // PAPAN PERINGKAT KECEPATAN (REKOR KELAS)
  // ==========================================================================
  function renderLeaderboardTable() {
    const tbody = document.getElementById("leaderboard-rows");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (State.leaderboard.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align: center; color: var(--c-ink-muted); padding: 24px;">
            Belum ada rekor tersimpan. Mainkan 1 sesi dan jawab minimal 3 kasus dengan benar untuk mencatatkan rekor!
          </td>
        </tr>
      `;
      return;
    }

    State.leaderboard.forEach((entry, idx) => {
      const tr = document.createElement("tr");
      if (idx === 0) tr.classList.add("record-first");

      let rankBadge;
      if (idx === 0) {
        rankBadge = `<span class="rank-badge rank-1"><svg class="ui-icon ui-icon-inline" aria-hidden="true" style="color: #E89E19;"><use href="#icon-trophy"></use></svg> 1</span> <span class="record-badge-tag">Rekor Kelas</span>`;
      } else if (idx === 1) {
        rankBadge = `<span class="rank-badge rank-2">2</span>`;
      } else if (idx === 2) {
        rankBadge = `<span class="rank-badge rank-3">3</span>`;
      } else {
        rankBadge = `${idx + 1}`;
      }

      tr.innerHTML = `
        <td>${rankBadge}</td>
        <td>
          <span class="team-color-dot" style="background-color: ${entry.warna};"></span>
          ${entry.nama}
        </td>
        <td>${entry.avgTime.toFixed(1)} detik</td>
        <td>${entry.skor}</td>
        <td>${entry.tanggal || "-"}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  function initLeaderboardEvents() {
    // Ekspor Cadangan (.json)
    const btnExport = document.getElementById("btn-export-backup");
    if (btnExport) {
      btnExport.addEventListener("click", () => {
        playSound("click");
        exportLeaderboardJSON();
      });
    }

    // Impor Cadangan (.json)
    const importInput = document.getElementById("import-file-input");
    if (importInput) {
      importInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
          importLeaderboardJSON(file);
        }
      });
    }

    // Hapus Rekor (Tahan 2 Detik + Konfirmasi Sesuai PRD)
    setupHoldResetLeaderboard();
  }

  function exportLeaderboardJSON() {
    try {
      const dataStr = JSON.stringify(State.leaderboard, null, 2);
      const blob = new Blob([dataStr], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "peringkat-detektif-norma.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      alert("Gagal mengekspor data cadangan.");
    }
  }

  function importLeaderboardJSON(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const parsed = JSON.parse(e.target.result);
        if (Array.isArray(parsed)) {
          State.leaderboard = parsed;
          try {
            localStorage.setItem(STORAGE_KEYS.LEADERBOARD, JSON.stringify(parsed));
          } catch (err) {}
          renderLeaderboardTable();
          playSound("correct");
          alert("Data rekor peringkat berhasil diimpor!");
        } else {
          alert("Format file tidak valid.");
        }
      } catch (err) {
        alert("Gagal membaca file JSON.");
      }
    };
    reader.readAsText(file);
  }

  function setupHoldResetLeaderboard() {
    const btnReset = document.getElementById("btn-reset-leaderboard");
    const bar = document.getElementById("hold-reset-bar");
    if (!btnReset || !bar) return;

    let holdTimer = null;
    let holdProgress = 0;
    const HOLD_DURATION = 2000; // 2 detik
    const INTERVAL_TICK = 50;

    const startHold = () => {
      holdProgress = 0;
      bar.style.width = "0%";

      holdTimer = setInterval(() => {
        holdProgress += INTERVAL_TICK;
        const pct = Math.min(100, (holdProgress / HOLD_DURATION) * 100);
        bar.style.width = `${pct}%`;

        if (holdProgress >= HOLD_DURATION) {
          clearInterval(holdTimer);
          holdTimer = null;
          bar.style.width = "0%";
          openConfirmModal("Hapus semua catatan rekor kelas secara permanen?", () => {
            State.leaderboard = [];
            try {
              localStorage.removeItem(STORAGE_KEYS.LEADERBOARD);
            } catch (e) {}
            renderLeaderboardTable();
            playSound("click");
          });
        }
      }, INTERVAL_TICK);
    };

    const cancelHold = () => {
      if (holdTimer) {
        clearInterval(holdTimer);
        holdTimer = null;
        bar.style.width = "0%";
      }
    };

    btnReset.addEventListener("pointerdown", startHold);
    btnReset.addEventListener("pointerup", cancelHold);
    btnReset.addEventListener("pointerleave", cancelHold);
    btnReset.addEventListener("pointercancel", cancelHold);
  }

  // ==========================================================================
  // CONFETTI SEDERHANA CANVAS MANDIRI (TANPA LIBRARY)
  // ==========================================================================
  function launchConfetti() {
    const canvas = document.getElementById("confetti-canvas");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const width = (canvas.width = canvas.offsetWidth);
    const height = (canvas.height = canvas.offsetHeight);

    const pieces = [];
    const colors = ["#E89E19", "#A93226", "#2D6A4F", "#1D6A78", "#FBF6E9"];

    for (let i = 0; i < 60; i++) {
      pieces.push({
        x: Math.random() * width,
        y: -10 - Math.random() * height * 0.5,
        w: 8 + Math.random() * 8,
        h: 6 + Math.random() * 6,
        color: colors[Math.floor(Math.random() * colors.length)],
        vy: 2 + Math.random() * 3,
        vx: (Math.random() - 0.5) * 2,
        rot: Math.random() * 360,
        vrot: (Math.random() - 0.5) * 8
      });
    }

    let frameCount = 0;
    function renderFrame() {
      ctx.clearRect(0, 0, width, height);

      pieces.forEach(p => {
        p.y += p.vy;
        p.x += p.vx;
        p.rot += p.vrot;

        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate((p.rot * Math.PI) / 180);
        ctx.fillStyle = p.color;
        ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
        ctx.restore();
      });

      frameCount++;
      if (frameCount < 160) {
        requestAnimationFrame(renderFrame);
      } else {
        ctx.clearRect(0, 0, width, height);
      }
    }

    requestAnimationFrame(renderFrame);
  }

  // Debug reference untuk otomasi uji lingkungan
  window.__DETEKTIF_STATE__ = State;
  window.State = State;
  window.loadCase = loadCase;
  window.handleStampAnswer = handleStampAnswer;
  window.handleSelectGroupTurn = handleSelectGroupTurn;
  window.evaluateReason = evaluateReason;
  window.showCaseExplanation = showCaseExplanation;
  window.renderResultScreen = renderResultScreen;
  window.showScreen = showScreen;
  window.startNewCaseSession = startNewCaseSession;
  window.finishGameSession = finishGameSession;

})();
