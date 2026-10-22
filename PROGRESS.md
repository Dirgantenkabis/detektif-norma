# PROGRESS PENGERJAAN: DETEKTIF NORMA (v1.1)

Proyek: Game Pembelajaran Interaktif PPKn Kelas 5 SD  
Platform: Web Statis Murni (HTML/CSS/JS), Tanpa Framework/Library/CDN, Offline-Ready, Layar Sentuh TV / Pointer Events.

---

## 📌 CATATAN PENTING & VERIFIKASI GURU
> **PERHATIAN GURU KELAS 5:**  
> Seluruh 24 kasus (16 dasar + 8 HOTS) di `data.js` telah disusun berdasarkan capaian pembelajaran norma PPKn Kelas 5 (Agama, Kesusilaan, Kesopanan, Hukum) dengan bahasa lugas dan tanpa ambiguitas. Sebelum dipakai secara resmi dalam pembelajaran di kelas, mohon guru membaca ulang daftar kasus untuk memastikan kesesuaian kultur dan konteks lokal siswa.

---

## FASE 1: FONDASI DAN DATA
- **Status:** SELESAI ✅
- **Apa yang dibuat:**
  1. Sistem desain terpadu di `:root` (`style.css`): palet warna kantor detektif (dinding hijau botol, papan gabus, kertas krem berklip, 4 warna stempel norma yang tegas dan bukan neon), outline tebal bersatu, bayangan arah seragam, dan variabel tipografi responsif.
  2. Komponen tombol seragam (`.btn-primary-big`, `.btn-secondary`, `.btn-action`, `.btn-danger`, `.btn-sm`, `.btn-icon`) dengan warna dasar yang langsung terlihat jelas dalam kondisi normal (tanpa menunggu hover/focus), serta efek fisik turun saat ditekan (`:active` / `.pressed`).
  3. Komponen modal berkas detektif lengkap dengan penutup ✕ besar (min. 64px), klik backdrop, dan escape keyboard.
  4. Berkas `data.js` berisi:
     - 4 Norma lengkap (`NORMA_LIST`): Agama, Kesusilaan, Kesopanan, Hukum dengan deskripsi singkat dan warna stempel.
     - 5 Kelompok bawaan (`KELOMPOK_DEFAULT`): Tim Elang, Tim Harimau, Tim Kancil, Tim Banteng, Tim Rusa.
     - 24 Kasus lengkap (`KASUS_POOL`): 16 dasar (4 per norma) dan 8 HOTS (2 per norma) dengan 3 tingkat petunjuk bertahap, pertanyaan lanjutan terarah untuk HOTS, alasan, dan penjelasan.
     - Fungsi validasi data otomatis `validasiDataNorma()` yang memverifikasi skema, keunikan ID, jumlah petunjuk, serta keseimbangan norma.
- **Apa yang diuji:**
  - Menjalankan uji mandiri validasi `validasiDataNorma()`: 100% lolos (24 kasus valid, 0 error, 0 warning).
  - Pengecekan ambiguitas teks kasus: seluruh kalimat kasus di bawah 20 kata, nama tokoh netral, konteks sekolah/rumah/lingkungan aman dan ramah anak.
  - Verifikasi warna tombol: semua tombol memiliki latar belakang solid dan border kontras dalam keadaan idle (tanpa hover).
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Pada draf awal, kasus HOTS k23 hampir menyerupai norma kesusilaan murni karena unsur kejujuran.
  - *Perbaikan:* Ditajamkan pada aspek perizinan resmi mendirikan bangunan dan suap sebagai tindak pidana korupsi terhadap negara agar tegas berlabuh pada norma hukum.
- **Keputusan:**
  - Menggunakan CSS variable `--fs-case: clamp(22px, 3.7vh, 38px)` agar di layar 1080p ukuran teks kasus berada di rentang 40px sesuai PRD.
  - Mengutamakan fallback font sistem bulat tebal (`ui-rounded`, `Nunito`, `Trebuchet MS`, `sans-serif`) yang secara bawaan sangat ramah untuk anak-anak sekolah dasar jika folder `assets/fonts/` belum diisi file fisik font.

---

## FASE 2: LAYAR AWAL, SETUP CEPAT, NAVIGASI
- **Status:** SELESAI ✅
- **Apa yang dibuat:**
  1. Layar awal (`screen-start`): Judul "DETEKTIF NORMA" besar dengan ornamen kaca pembesar SVG mandiri, tombol besar "MULAI PETUALANGAN BARU", tombol toolbar (Suara ON/OFF, Layar Penuh, Cara Main, Peringkat, Tentang), tombol kondisional "Main Lagi dengan Kelompok Terakhir", dan footer kredit resmi Bu Fina & Mas Dirga.
  2. Setup kelompok kilat 1 ketukan (`screen-setup`): Pertanyaan tunggal "Berapa kelompok yang bertugas hari ini?" dengan 4 tombol besar (2, 3, 4, 5). Begitu diketuk, kelompok langsung terbuat otomatis dari `KELOMPOK_DEFAULT`, tersimpan ke `localStorage`, dan memunculkan kartu pengingat peran.
  3. Modal kartu pengingat peran (`modal-role-reminder`): Aturan utama "Tidak boleh mengejek jawaban kelompok lain!" dan 4 peran detektif (Pembaca Kartu, Pengarah Tim, Pencatat, Penyaji Alasan) dengan tombol "Siap Menyelidiki Kasus! 🚀".
  4. Modal Tentang (`modal-about`): Avatar ramah (gambar `assets/profil.png` dengan fallback SVG mandiri), teks sapaan Mas Dirga, pembatas, Kontak: [ISI KONTAK], materi Bu Fina, catatan ilustrasi AI, dan tombol tutup ✕ besar (tinggi > 64px).
  5. Modal Cara Main (`modal-rules`): Panduan 5 langkah satu kasus dan fungsi tombol kendali guru.
  6. Navigasi sentral `navigateToMenu()` dengan konfirmasi jika meninggalkan sesi aktif.
- **Apa yang diuji:**
  - Navigasi 2 ketukan dari layar awal ke papan kasus (Mulai ➔ Pilih jumlah ➔ Board).
  - Navigasi 1 ketukan tombol resume "Main Lagi dengan Kelompok Terakhir" yang otomatis memuat nama tim sebelumnya.
  - Buka-tutup modal Tentang dan Cara Main dengan 3 cara: tombol ✕, klik area gelap (backdrop), dan tombol Escape keyboard.
  - Tampilan visual di 1920x1080 dan 1366x768 via headless Edge browser: 100% responsif 16:9, bebas scrollbar.
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Pada integrasi CSS awal, aturan `.screen { display: none; }` dan `.modal-overlay { display: none; }` sempat terpotong saat penulisan stylesheet sehingga elemen sempat bertumpuk di DOM.
  - *Perbaikan:* Menambahkan deklarasi eksplisit `.screen` dan `.modal-overlay` dengan selektor prioritas tinggi (`display: flex !important;` pada kelas `.active`), diverifikasi lewat tangkapan layar otomatis CDP.
- **Keputusan:**
  - Kartu pengingat peran ditampilkan setelah pemilihan jumlah kelompok dengan tombol konfirmasi langsung agar siswa dan guru dapat menyepakati pembagian peran dan aturan dilarang mengejek sebelum berkas pertama dibuka.

---

## FASE 3: TATA LETAK PAPAN KASUS
- **Status:** SELESAI ✅
- **Apa yang dibuat:**
  1. Header papan satu baris (`#board-header`): Tombol Menu di kiri, badge progres "Kasus X dari 12" dan indikator "🔥 Kasus Tantangan" di tengah, timer waktu berpikir ⏱️, toggle suara, serta tombol layar penuh di kanan. Tidak ada elemen yang tumpang tindih atau bertumpuk.
  2. Berkas kasus detektif (`#case-folder`): Bahan kertas krem bertekstur arsip dengan klip logam fisik, nomor kasus berkas, target giliran aktif, teks kasus besar (setara 40px di 1080p), dan 3 slot petunjuk bertahap (Petunjuk 1 langsung terbuka, Petunjuk 2 & 3 terkunci).
  3. Bawah tengah: 4 stempel karet norma (Agama, Kesusilaan, Kesopanan, Hukum) dengan warna pembeda berkarakter, ikon visual, dan deskripsi singkat. Stempel nonaktif (ramah terbaca namun terkunci) sampai guru memilih kelompok.
  4. Sisi kiri (`teams-sidebar`): Papan kelompok dengan nama, dot warna tim, skor dinamis, dan catatan waktu. Kelompok yang dipilih mendapatkan highlight tebal emas `active-turn`.
  5. Sisi kanan (`teacher-sidebar`): Panel guru terpisah dengan tombol besar mudah dibedakan: Buka Petunjuk Berikutnya, Batalkan Giliran, Jeda Game, dan Selesai Sekarang.
- **Apa yang diuji:**
  - Pengujian tata letak responsif untuk 2, 3, 4, dan 5 kelompok di dua resolusi target: 1920x1080 dan 1366x768.
  - Verifikasi DOM layout otomatis (CDP): semua kartu kelompok terisi rapi, stempel aktif tepat saat kelompok dipilih.
  - Uji tombol Batalkan Giliran: mengembalikan status pemilihan kelompok ke posisi netral tanpa dampak pada skor.
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Pada daftar 5 kelompok di resolusi 1366x768, sempat muncul baris scrollbar horizontal tipis di bawah sidebar kiri.
  - *Perbaikan:* Menambahkan `overflow-x: hidden;` dan `scrollbar-width: none;` pada `.board-sidebar` dan `.teams-vertical-list`.
- **Keputusan:**
  - Mengatur stempel dalam keadaan nonaktif dengan `opacity: 0.65` dan `grayscale(25%)` agar teks dan warna dasarnya tetap terbaca jelas oleh anak-anak saat berdiskusi, namun tetap memperlihatkan status nonaktif yang tegas sampai guru mengetuk giliran kelompok.

---

## FASE 4: LOGIKA KASUS, SKOR, WAKTU
- **Status:** SELESAI ✅
- **Apa yang dibuat:**
  1. Komposisi sesi 12 kasus (8 dasar + 4 HOTS, 2 dasar per norma & 1 HOTS per norma) diacak Fisher-Yates dengan mekanisme `lastSessionCaseIds` yang memprioritaskan kasus yang belum muncul di sesi sebelumnya.
  2. Alur 1 kasus interaktif:
     - Petunjuk 1 terbuka langsung dan timer berpikir mulai menghitung (maksimal 180 detik).
     - Guru memilih kelompok di papan skor sebelum stempel norma dapat ditekan.
     - Tombol Batalkan mengembalikan status tanpa dampak skor jika guru keliru mengetuk nama kelompok.
     - Perbandingan jawaban murni mencocokkan `jawabanId` kasus dengan norma stempel yang ditekan.
  3. Logika evaluasi jawaban:
     - Jawaban Benar: stempel "TERPECAHKAN" muncul dengan rotasi dinamis, pesan apresiatif, penambahan poin tebakan (3/2/1 sesuai petunjuk terbuka), pencatatan waktu berpikir kelompok terpilih, dan pembukaan panel alasan lisan.
     - Jawaban Salah: feedback santun ("Coba lagi. Pikirkan sumber aturan..."), kelompok terkunci untuk kasus itu (0 poin, tanpa catatan waktu), dan petunjuk berikutnya terbuka otomatis untuk memberi kesempatan kelompok lain.
  4. Panel alasan guru: pertanyaan lanjutan pemandu tampil pada kasus HOTS. Tombol "Alasan Masuk Akal" dengan indikator progress tahan 1 detik memberi poin ekstra (+1 untuk dasar, +2 untuk HOTS).
  5. Kasus gagal / semua kelompok terkunci otomatis dimasukkan ke daftar `unsolvedCases` untuk dibahas di akhir sesi.
  6. Tombol kendali guru: Jeda menghentikan timer sementara waktu, dan Selesai Sekarang mengakhiri sesi seketika dengan menghitung perolehan dari kasus yang telah dimainkan.
  7. Pencegahan klik cepat / spam click (`isProcessingAnswer` guard) agar tidak terjadi skor ganda atau error race condition.
- **Apa yang diuji:**
  - Uji otomasi menyeluruh `test_phase4.py`: stempel terkunci sebelum pilih kelompok, pembatalan giliran, penguncian kelompok setelah salah dan pembukaan petunjuk berikutnya otomatis, perhitungan poin petunjuk 1 (+3) dan petunjuk 2 (+2), poin alasan masuk akal (+1/+2), tombol Jeda/Lanjut, dan tombol Selesai Sekarang.
  - Simulasi 12 kasus penuh secara berurutan (`test_full_12.py`) dari kasus 1 sampai kasus 12: 100% transisi lancar ke layar hasil dengan perolehan skor akurat.
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Pada klik stempel bertubi-tubi dalam tempo milidetik, ada potensi event ganda terpanggil sebelum state diperbarui.
  - *Perbaikan:* Menambahkan guard flag `State.isProcessingAnswer` yang memblokir panggilan stempel berikutnya sampai logika selesai.
- **Keputusan:**
  - Timer berpikir hanya mencatat jawaban benar; tebakan salah tidak dicatat agar anak tidak terdorong untuk menebak asal demi kecepatan.

---

## FASE 5: EFEK DAN SUARA
- **Status:** SELESAI ✅
- **Apa yang dibuat:**
  1. Generator suara mandiri Web Audio API (OscillatorNode, tanpa file audio luar):
     - `click`: nada klik lembut frekuensi 600Hz ➔ 300Hz.
     - `stamp`: efek suara "duk" stempel fisik mantap 140Hz ➔ 45Hz.
     - `correct`: dua nada naik ceria (C5 ➔ G5, 523Hz ➔ 784Hz).
     - `wrong`: nada turun lembut (320Hz ➔ 220Hz, bukan buzzer keras, santun untuk kelas).
     - `finish`: akor arpeggio selebrasi 4 nada harmonis.
     - Proteksi debounce audio (`lastSoundTimes`) mencegah tumpang tindih saat klik cepat.
  2. Pasangan efek visual untuk setiap kejadian:
     - Stempel jatuh: animasi cap stempel "TERPECAHKAN" membesar dan miring -12 derajat.
     - Tebakan salah: berkas kertas bergoyang pelan (`shake-soft`) dengan aksen garis tepi oranye lembut (bukan merah menyala agresif).
     - Tebakan benar: kilau emas lembut pada berkas folder (`correct-glow`).
     - Perolehan skor: animasi pop angka membesar sejenak pada badge skor kelompok (`score-pop`).
     - Partikel confetti ringan (Canvas API mandiri, 60 partikel palet detektif, otomatis berhenti setelah 160 frame).
  3. Dukungan penuh `prefers-reduced-motion: reduce` untuk aksesibilitas siswa dengan sensitivitas visual.
- **Apa yang diuji:**
  - Pengujian audio dan toggle suara (`test_phase5.py`): aktivasi/deaktivasi audio tidak menghentikan visual feedback.
  - Verifikasi DOM kelas animasi: `shake-soft`, `correct-glow`, `stamp-terpecahkan`, dan `score-pop` terpicu tepat waktu.
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Pada klik beruntun, suara oscillator sempat berpotensi menumpuk.
  - *Perbaikan:* Menerapkan filter throttle waktu 60ms antar-suara berjenis sama.
- **Keputusan:**
  - Menghindari pemakaian nada buzzer elektrik atau warna merah membara pada tebakan salah agar anak-anak tidak merasa tertekan dan tetap berani mengemukakan pendapat.

---

## FASE 6: HASIL DAN PERINGKAT KECEPATAN
- **Status:** SELESAI ✅
- **Apa yang dibuat:**
  1. Layar Hasil Permainan (`screen-result`):
     - Papan perolehan skor akhir semua kelompok dengan visualisasi dot warna kelompok, badge poin kontras, dan penanganan skor seri alami (#1, #2, #2...).
     - Rata-rata waktu berpikir per jawaban benar untuk masing-masing kelompok.
     - Pesan apresiatif tanpa diskriminasi: "Semua detektif hebat dan belajar banyak hari ini! 🎉" (tidak memakai kata "kalah").
     - Bagian "Kasus Yang Perlu Dibahas Bersama" (maksimal 3 kasus yang gagal dipecahkan beserta jawaban benar & penjelasan materinya).
     - Tombol aksi: "Main Lagi (Kelompok Sama)" paling mencolok, tombol "Papan Peringkat Kecepatan", dan "Menu Utama".
  2. Papan Peringkat Kecepatan (`screen-leaderboard`):
     - Peringkat dihitung dari rata-rata waktu berpikir pada jawaban benar (makin kecil makin tinggi / cepat).
     - Syarat kualifikasi: minimal 3 jawaban benar dalam satu sesi permainan.
     - Posisi 1 mendapatkan badge khusus `Rekor Kelas`.
     - Tampil maksimal 10 entri terbaik dari seluruh sesi yang tersimpan di `localStorage`.
     - Data yang disimpan hanya nama kelompok, tanpa identitas nama siswa individu (sesuai privasi kelas PRD).
  3. Fitur Utilitas Guru:
     - Ekspor Cadangan: mengunduh file `peringkat-detektif-norma.json`.
     - Impor Cadangan: membaca dan memvalidasi file JSON dari penyimpanan guru.
     - Hapus Rekor: pengamanan ganda (tombol tahan 2 detik dengan visual progress bar + modal konfirmasi).
  4. Manajemen Sesi Tanpa Reload:
     - Tiga sesi permainan berurutan dapat dijalankan berturut-turut tanpa me-reload browser; status lama (skor, catatan waktu, kasus terbuka, timer) selalu di-reset bersih.
- **Apa yang diuji:**
  - Uji otomasi menyeluruh `test_phase6.py`:
    - Pencatatan skor akhir dan kasus unsolved.
    - Kualifikasi kelompok masuk leaderboard hanya jika jawaban benar >= 3.
    - Persistensi data `localStorage` yang tetap utuh setelah `Page.reload`.
    - Uji 3 sesi berurutan tanpa reload: skor terbukti kembali 0 pada awal tiap sesi baru.
    - Uji reset leaderboard: tabel kembali ke status default "Belum ada rekor tersimpan".
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Pada tampilan hasil sesi 4 kelompok awal di resolusi 768p, badge poin sempat terdorong ke samping kartu karena flex gap.
  - *Perbaikan:* Menyederhanakan label menjadi `#1 Tim Elang`, mengatur `white-space: nowrap;`, serta membatasi ukuran teks statistik waktu agar badge skor selalu tampak rapi di dalam kartu.
- **Keputusan:**
  - Format tanggal rekor menggunakan format lokal Indonesia `id-ID` (contoh: "21 Okt 2026") agar mudah dipahami oleh guru dan siswa SD.

---

## FASE 7: PENGUJIAN, PERBAIKAN, README
- **Status:** SELESAI ✅
- **Apa yang dibuat & diuji:**
  1. Audit Kepatuhan PRD & Larangan:
     - Pencarian kata `"maskot"` dan `"mascot"` pada seluruh file (`.js`, `.css`, `.html`): **0 hasil (bersih 100%)**.
     - Audit warna tombol kondisi normal: seluruh 38 tombol dan stempel norma memiliki warna latar dan garis tepi solid pada kondisi idle (tidak bergantung pada hover, aman untuk layar sentuh TV kelas).
     - Tidak ada dependensi framework, library luar, font internet, atau pemanggilan CDN (semua path relatif, 100% offline-ready).
  2. Pengujian Teknis Komprehensif (`test_phase7_full_audit.py`):
     - Validasi data 24 kasus otomatis: 100% lolos (16 dasar + 8 HOTS, seimbang 4 norma).
     - Emulasi sentuhan Pointer Events: seluruh klik tombol dan modal berfungsi responsif pada input sentuh.
     - Fallback aset: ketiadaan file gambar `assets/profil.png` otomatis menampilkan ilustrasi vektor SVG mandiri tanpa memicu error visual.
     - Aksesibilitas: dukungan media `prefers-reduced-motion: reduce` teruji meredam animasi tanpa mengganggu interaksi gameplay.
     - Resolusi responsif 16:9: teruji bebas overflow dan bebas scrollbar di 1920×1080 dan 1366×768.
  3. Dokumentasi `README.md`:
     - Petunjuk menjalankan game secara offline langsung dari `index.html`.
     - Panduan menambah/mengubah kasus di `data.js` beserta contoh skema lengkap dan syarat HOTS.
     - Panduan aset font lokal (`assets/fonts/Nunito-Bold.ttf`, `Fredoka-Bold.ttf`) dan gambar avatar (`assets/profil.png`), serta letak penggantian teks `[ISI KONTAK]`.
     - Penjelasan cara kerja dan batasan teknis peringkat lokal `localStorage`.
     - Petunjuk ekspor dan impor cadangan rekor `peringkat-detektif-norma.json`.
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Label peringkat pada baris tim hasil sesi sempat memicu pemotongan horizontal pada resolusi 768p.
  - *Perbaikan:* Tata letak kartu disederhanakan dengan perataan teks flexbox dan format `#1 Tim Elang` sehingga badge skor dan catatan waktu selalu tampil proporsional.
- **Keputusan:**
  - Menghapus skrip-skrip uji sementara jika diperlukan atau mempertahankannya sebagai rangkaian pengujian otomatis end-to-end yang dapat dijalankan ulang sewaktu-waktu.

---

## 🏁 KESIMPULAN AKHIR PROYEK
Seluruh 7 Fase pengerjaan game **"Detektif Norma"** telah tuntas 100% dan memenuhi seluruh kriteria penerimaan PRD v1.1:
1. Mulai ke kasus pertama maksimal 2 ketukan (atau 1 ketukan via "Main lagi dengan kelompok yang sama").
2. Sesi 12 kasus tuntas tanpa error untuk 2, 3, 4, dan 5 kelompok.
3. Stempel terkunci sebelum guru memilih kelompok; pembatalan giliran bekerja akurat.
4. Perhitungan skor sesuai tabel PRD; kelompok salah terkunci khusus kasus tersebut; poin tidak pernah berkurang.
5. Waktu berpikir akurat tanpa menghitung waktu Jeda dan panel alasan.
6. Papan peringkat kecepatan beroperasi dengan syarat minimal 3 jawaban benar; Rekor Kelas tampil; persistensi localStorage dan alat ekspor/impor cadangan JSON berfungsi penuh.
7. Semua tombol berlatar warna jelas pada kondisi normal tanpa hover; header satu baris rapi bebas tumpang tindih.
8. Berjalan 100% offline tanpa gambar di `assets/`.
9. Tiga sesi berurutan berjalan mulus tanpa reload tanpa meninggalkan status lama.
10. Teruji di monitor 1920×1080 dan 1366×768, mouse, dan emulasi sentuhan.
11. 24 kasus tersusun rapi menurut kurikulum PPKn Kelas 5 SD dan ditandai untuk dicek guru sebelum pemakaian kelas resmi.

---

# TAHAP PERBAIKAN TAMPILAN & UX (ITERASI v1.2)

## FASE 1: SET IKON SVG SATU GAYA (GANTI SEMUA EMOJI)
- **Status:** SELESAI ✅
- **Apa yang dibuat/diubah:**
  1. Membuat sprite SVG inline mandiri (`#svg-sprite`) di `index.html` berisi 36 definisi `<symbol>` seragam (grid 24x24px, garis tebal 2.5 - 3px, `stroke-linecap="round"`, `stroke-linejoin="round"`, pewarnaan murni `currentColor`, tanpa gradasi).
  2. Menyediakan seluruh ikon yang disyaratkan: kaca pembesar, berkas/dokumen, stopwatch, suara hidup/mati, layar penuh, menu/pintu, kelompok, buku panduan, piala, info, jeda, lanjutkan, batalkan, bendera selesai, bintang, lampu petunjuk, pensil/ubah, megafon, gembok, centang, panah kanan, serta empat ikon norma: tempat ibadah (Agama), hati (Kesusilaan), dua tangan berjabat (Kesopanan), timbangan (Hukum).
  3. Mengganti 100% emoji di seluruh berkas proyek (`index.html`, `style.css`, `game.js`, `data.js`) dengan SVG `<use href="#icon-...">` atau teks murni.
  4. Menambahkan utility class CSS untuk ikon: `.ui-icon`, `.ui-icon-inline`, `.ui-icon-lg`, `.ui-icon-xl`.
- **Apa yang diuji:**
  - Audit regex mendalam pada seluruh kode sumber (`.html`, `.js`, `.css`): **0 emoji tersisa (Total Emojis Found: 0)**.
  - Semua ikon teruji mewarisi warna teks (`currentColor`) secara konsisten pada tombol normal maupun aktif.
  - Seluruh alur permainan tetap berfungsi normal.
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Label dinamis di JavaScript (seperti tombol suara, tombol jeda/lanjut, pesan umpan balik tebakan, dan ikon baris tim) sebelumnya menyisipkan karakter unicode emoji langsung.
  - *Perbaikan:* Diperbarui dengan fungsi helper render ikon SVG aman dan string teks murni.
- **Keputusan:**
  - Menempatkan sprite SVG tepat di awal tag `<body>` agar langsung tersedia secara instan sebelum elemen DOM lain dirender.

---

## FASE 2: STEMPEL "TERPECAHKAN" + SUARA + RUANG BERKAS
- **Status:** SELESAI ✅
- **Apa yang dibuat/diubah:**
  1. Merancang ulang stempel fisik "TERPECAHKAN" mirip stempel tinta asli (SVG/CSS):
     - Bingkai ganda dengan sudut membulat (`.stamp-outer-frame` dan `.stamp-inner-frame`).
     - Teks tebal "TERPECAHKAN" dengan dua ikon bintang SVG mandiri di sisi kiri dan kanan.
     - Teks subjudul kecil "KASUS DETEKTIF" di bagian atas stempel.
     - Warna merah tinta bata dari variabel CSS `--c-stamp-ink: #A93226;`, opasitas 0.88, `mix-blend-mode: multiply;`, rotasi dinamis -10 derajat.
     - Tekstur tinta tidak rata menggunakan filter SVG `<filter id="filter-stamp-ink">` berbasis `<feTurbulence>` dan `<feColorMatrix>` sebagai alpha mask bertekstur pudar alami.
  2. Alokasi zona khusus bebas bentrok:
     - Mengatur tata letak bawah berkas (`.folder-bottom-row`) menjadi dua kolom seimbang: panel umpan balik & evaluasi alasan guru di sisi kiri (`.folder-action-zone`), dan zona stempel tetap (`.case-stamp-zone`) di sisi kanan bawah.
     - Stempel diposisikan di zona khusus sehingga terbukti tidak pernah menutupi teks kasus, petunjuk, maupun panel alasan guru, serta tata letak berkas tidak melompat saat stempel muncul.
  3. Animasi stempel fisik mantap (durasi 350 ms <= 400 ms):
     - Efek jatuh dari skala 1.8 ke skala 1.0 dengan kurva pegas hentakan (`cubic-bezier(0.2, 0.9, 0.3, 1.15)`).
     - Berkas folder bergetar singkat (`stamp-bounce`).
     - Cincin tinta tipis memudar melingkar (`.stamp-ink-ripple`).
     - Dukungan penuh `prefers-reduced-motion: reduce` beralih ke fade sederhana tanpa animasi guncangan.
  4. Sintesis audio multi-layer Web Audio API tanpa file audio eksternal:
     - Lapisan 1: Dentuman rendah sweep sine 140 Hz ➔ 45 Hz dalam 0.14 detik dengan decay gain cepat.
     - Lapisan 2: Semburan noise pendek melalui biquad lowpass filter 800 Hz selama 0.05 detik.
     - Lapisan 3: Klik tajam 2 kHz selama 0.02 detik.
     - Dimainkan tepat saat stempel mendarat (delay 140 ms), tersinkronisasi dengan toggle suara dan proteksi anti-spam click.
  5. Perapian tipografi dan ruang layar kasus:
     - Teks kasus diperbesar menjadi `clamp(24px, 4.2vh, 42px)` (mencapai 42px pada 1080p, melampaui standar minimal 40px).
     - Teks petunjuk diperbesar menjadi `clamp(14px, 2.1vh, 18px)` dengan font-weight 800.
     - Teks panduan bawah "Tekan salah satu stempel norma setelah kelompok diberi giliran:" diperbesar menjadi `clamp(17px, 2.7vh, 29px)` (mencapai 29px pada 1080p, melampaui syarat minimal 28px).
     - Timer header diperkecil menjadi `clamp(12px, 1.6vh, 15px)` sehingga tetap terbaca jelas tanpa mencuri fokus.
- **Apa yang diuji:**
  - Pengujian otomasi visual CDP Edge (`test_phase2.py`):
    - Uji overlap geometris pada 1920×1080: `overlapsCaseText: false`, `overlapsClues: false`, `overlapsReasonPanel: false`, `overlapsFeedback: false`.
    - Uji overlap geometris pada 1366×768: `overlapsCaseText: false`, `overlapsClues: false`, `overlapsReasonPanel: false`, `overlapsFeedback: false`.
    - Verifikasi reset stempel saat berpindah ke kasus berikutnya: kelas `.show` terhapus bersih dan stempel kembali tersembunyi.
    - Uji audio Web Audio: audio stempel terpicu tepat waktu dan berhenti total saat tombol Suara OFF.
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Pada draf tata letak awal di resolusi 768p, tombol alasan guru pada kasus HOTS sempat menyentuh margin stempel sebesar 10px karena flex gap default terlalu rapat.
  - *Perbaikan:* Menetapkan `gap: clamp(20px, 2.8vw, 40px)` pada `.folder-bottom-row` dan mengubah `margin-top: auto` menjadi `margin-top: clamp(6px, 1vh, 12px)` sehingga seluruh elemen berada pada alur vertikal yang proporsional dan bebas overlap di kedua resolusi.
- **Keputusan:**
  - Menghilangkan scrollbar pada kontainer berkas (`overflow-x: hidden`, `scrollbar-width: none`) agar visual berkas kertas tetap bersih seperti dokumen fisik asli.

---

## FASE 3: KARTU STEMPEL NORMA
- **Status:** SELESAI ✅
- **Apa yang dibuat/diubah:**
  1. Merancang ulang 4 stempel norma menjadi stempel karet fisik:
     - Gagang kayu bertekstur di bagian atas (`.stamp-wood-handle` dengan lekuk pegangan `.stamp-handle-ridge`).
     - Bantalan karet berwarna di bagian bawah (`.stamp-pad-body`) dengan bayangan bawah tegas (`box-shadow: 0 5px 0 var(--c-outline)`).
     - Area sentuh besar dengan tinggi teruji minimal 80px di kedua resolusi (`clamp(80px, 11vh, 102px)`: 104px di 1080p, 86px di 768p).
     - Pewarnaan terpadu sesuai standar PRD: Agama hijau tua (`#1E6B4C`), Kesusilaan merah marun (`#8B1E22`), Kesopanan biru tua (`#1A4472`), Hukum cokelat emas (`#9C651F`), tanpa neon dan tanpa gradasi ungu-biru.
  2. Komponen konten stempel:
     - Ikon SVG tajam satu gaya dari Fase 1 (`#icon-norma-agama`, `#icon-norma-kesusilaan`, `#icon-norma-kesopanan`, `#icon-norma-hukum`).
     - Nama norma besar, tebal, dan kontras (`font-weight: 900`, `letter-spacing: 1px`).
     - Keterangan kecil ringkas PPKn Kelas 5 tetap dipertahankan.
  3. Tiga kondisi visual yang jelas dan terbaca dari jauh:
     - **(a) Menunggu giliran (waiting):** warna terang dan segar (`opacity: 0.92`), kursor tidak aktif, posisi rata di meja, terlihat siap digunakan dan tidak kusam/mati.
     - **(b) Aktif (setelah guru memilih kelompok):** stempel terangkat naik 6px (`transform: translateY(-6px)`), outline/border kuning emas cerah (`#F1C40F`), denyut animasi melayang pelan (`stampActiveGently`), dan kursor pointer.
     - **(c) Terkunci (setelah tebakan salah):** warna memudar (`opacity: 0.42`, `filter: grayscale(50%)`), posisi turun ke meja, memunculkan lencana ikon gembok SVG (`.stamp-lock-icon`), dan kursor `not-allowed`. Stempel norma yang salah terkunci khusus kasus tersebut sehingga kelompok berikutnya terpandu memilih opsi tersisa.
  4. Interaksi tekan fisik:
     - Saat ditekan, stempel turun ke bawah singkat (`.stamping-down`, `translateY(4px)`) diiringi suara klik Web Audio sebelum evaluasi jawaban dieksekusi.
- **Apa yang diuji:**
  - Pengujian otomasi visual CDP Edge (`test_phase3.py`):
    - Verifikasi Kondisi (A): 4 stempel berstatus disabled, opasitas 0.92, gagang kayu dan bantalan karet terverifikasi utuh, tinggi 104px (>= 80px).
    - Verifikasi Kondisi (B): saat kelompok diketuk, ke-4 stempel beralih ke kelas `.active`, border kuning `rgb(241, 196, 15)`, animasi denyut aktif.
    - Verifikasi Kondisi (C): saat tebakan salah, stempel yang salah otomatis terkunci (`.locked`, gembok tampak, grayscale 0.5), dan ketika kelompok kedua dipilih, norma yang telah tereliminasi tetap terkunci sementara 3 norma lainnya aktif.
    - Verifikasi responsivitas 768p: seluruh 4 stempel mempertahankan tinggi 86px (memenuhi syarat min. 80px).
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Pada status idle lama, stempel memiliki opasitas rendah dan grayscale sehingga terkesan rusak atau nonaktif.
  - *Perbaikan:* Ditingkatkan ke opasitas 0.92 dengan warna solid asli agar murid dapat membaca dan berdiskusi dengan nyaman sebelum giliran kelompok dipanggil.
- **Keputusan:**
  - Menandai stempel norma yang keliru ditebak dengan status terkunci per kasus agar siswa terdorong memikirkan alternatif norma lain yang lebih tepat.

---

## FASE 4: LAYAR HASIL (PODIUM + LENCANA)
- **Status:** SELESAI ✅
- **Apa yang dibuat/diubah:**
  1. Merancang ulang tata letak layar hasil (`screen-result`) menjadi panggung podium terpadu:
     - Judul besar "HASIL PENYELIDIKAN KELAS" dengan subjudul apresiatif tanpa kata "kalah".
     - Podium fisik besar di tengah (`#result-podium-container`) dengan 3 balok fisik bertingkat untuk 3 besar (Juara 1 emas di tengah, Juara 2 perak di kiri, Juara 3 perunggu di kanan). Khusus untuk 2 kelompok, podium otomatis beralih menjadi 2 balok proporsional.
     - Setiap kartu podium menampilkan: nama kelompok dan dot warna, skor raksasa terbaca dari bangku belakang, informasi waktu berpikir, dan lencana prestasi.
     - Balok podium memiliki nomor peringkat fisik timbul tebal (`#1`, `#2`, `#3`) dengan bayangan dan outline 3D yang tegas.
  2. Kelompok sisanya (Peringkat 4 & 5 jika ada):
     - Ditampilkan sebagai baris horizontal besar di bawah podium (`#result-remaining-container`) dengan kartu terstruktur, nama tebal, badge skor, dan waktu berpikir.
     - Jika sesi diikuti 2 atau 3 kelompok, kontainer ini otomatis disembunyikan (`display: none;`).
  3. Aturan peringkat & pemecah seri (Tie-breaking):
     - Peringkat utama diurutkan berdasarkan skor tertinggi.
     - Bila skor sama: nomor peringkat tetap sama (misal sama-sama `#1`), dan urutan tampil diatur berdasarkan rata-rata waktu menjawab benar yang lebih cepat.
     - Format label waktu: `"rata-rata menjawab 13,3 dtk"` menggunakan koma lokal desimal Indonesia.
  4. Dua sistem lencana yang adil:
     - **"Skor Tertinggi":** dianugerahkan kepada kelompok dengan perolehan skor tertinggi (boleh lebih dari 1 tim jika terjadi seri).
     - **"Tercepat":** dianugerahkan kepada kelompok dengan rata-rata waktu terendah HANYA jika kelompok tersebut memiliki minimal 3 jawaban benar (`correctCount >= 3`).
     - Kelompok dengan kurang dari 3 jawaban benar: menampilkan keterangan jelas `"belum cukup 3 jawaban benar untuk peringkat kecepatan"` dan tidak berhak menerima lencana Tercepat.
  5. Bagian "Kasus yang perlu dibahas bersama":
     - Diringkas menjadi satu bilah kompak di bagian bawah (`#result-unsolved-box`) yang memuat maksimal 3 kasus dalam bentuk kapsul ringkas (tag norma + kalimat kasus), tidak mendominasi layar. Jika semua kasus terpecahkan, menampilkan pesan gemilang dengan ikon centang.
  6. Tombol aksi layar hasil:
     - Tombol "Main Lagi (Kelompok Sama)" dirancang paling besar dan menonjol (`.btn-primary-big`, tinggi hingga 68px, font 19px, bayangan tebal).
     - Tombol "Papan Peringkat Kecepatan" dan "Menu Utama" tampil rapi dan proporsional.
- **Apa yang diuji:**
  - Pengujian otomasi visual CDP Edge (`test_phase4.py`):
    - Uji 5 kelompok di 1920x1080: podium 3 kolom, remaining 2 baris tim, Harimau & Elang seri di skor 24 mendapatkan `#1` dan "Skor Tertinggi", Harimau yang lebih cepat tampil di tengah dan mendapatkan lencana "Tercepat", Tim Banteng (< 3 benar) menampilkan teks belum cukup 3 jawaban, bebas scrollbar (`hasScrollbar: false`).
    - Uji responsivitas di 1366x768: `hasVScroll: false`, `hasHScroll: false`, 100% rapi tanpa scrollbar.
    - Uji 2 kelompok: podium 2 kolom, 0 remaining cards, pesan sukses kasus terpecahkan tampil.
    - Uji 3 kelompok: podium 3 kolom, remaining container tersembunyi (`display: none;`), tombol Main Lagi terverifikasi lebih tinggi dan menonjol dibanding tombol lainnya.
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Pada kasus skor seri, urutan array semula mengandalkan urutan kemunculan default sehingga kelompok yang lebih cepat tidak otomatis tampil di tengah podium juara.
  - *Perbaikan:* Menerapkan pengurutan sekunder bertingkat `(b.skor - a.skor) || (timeA - timeB)` sehingga tim yang berpikir lebih cepat otomatis diprioritaskan di posisi tengah podium.
- **Keputusan:**
  - Menjaga persistensi data rekor `localStorage` tetap tidak berubah agar kompatibel dengan data yang telah tersimpan dari sesi-sesi sebelumnya.

---

## FASE 5: SETUP KELOMPOK DAN MODAL PENGINGAT
- **Status:** SELESAI ✅
- **Apa yang dibuat/diubah:**
  1. Merapikan dan memperbesar layar setup kelompok (`screen-setup`):
     - Kartu pertanyaan "Berapa kelompok yang bertugas hari ini?" diperbesar (`max-width: 980px`) agar mengisi layar TV secara proporsional.
     - Empat tombol angka pilihan kelompok (2, 3, 4, 5) diperbesar signifikan (tinggi hingga 155px di 1080p, digit 72px) dengan label tebal.
     - Menghapus tombol "Ubah Nama" dari pojok kanan atas layar agar tidak terlewat atau mengaburkan tata letak.
     - Memindahkan pengaturan nama ke DALAM kartu tepat di bawah empat tombol angka sebagai baris permanen (`.setup-names-strip`): menampilkan preview nama "Nama kelompok: Tim Elang, Tim Harimau, Tim Kancil, Tim Banteng, Tim Rusa" berdampingan langsung dengan tombol aksi "Ubah".
     - Memindahkan tombol "Menu Awal" ke bilah bawah (`.setup-bottom-bar`) agar terpisah bersih dan tidak bersaing dengan pilihan kelompok utama.
  2. Sinkronisasi nama kelompok instan:
     - Modal edit nama kelompok (`modal-edit-names`) langsung memperbarui teks pada baris nama di layar setup begitu tombol "Simpan Nama" diklik.
     - Menyimpan modifikasi nama kelompok ke `localStorage` (`detektif_norma_custom_names`) sehingga nama pilihan guru tetap tersimpan di sesi berikutnya.
  3. Perancangan ulang modal pengingat peran & aturan (`modal-role-reminder`):
     - Menghapus tombol ✕ merah di sudut kanan atas untuk mencegah ambiguitas penutup ganda.
     - Menyisakan SATU tombol besar "Siap Menyelidiki Kasus" di tengah bawah footer modal (tanpa ikon roket).
     - Menyederhanakan kartu peran menjadi daftar kompak satu baris per peran (`.roles-compact-list`) dengan ikon SVG mandiri dari Fase 1.
     - Aturan utama kelas "Tidak boleh mengejek jawaban kelompok lain!" tetap dipertahankan sebagai spanduk sorotan utama berlatar krem-merah.
     - Modal terkonfigurasi muncul HANYA pada permainan pertama setelah halaman dibuka (`State.hasShownRoleReminder` disimpan di memori, bukan localStorage). Pada sesi permainan berikutnya tanpa reload browser, pemilihan kelompok langsung menuju papan kasus tanpa menampilkan modal lagi.
- **Apa yang diuji:**
  - Pengujian otomasi visual CDP Edge (`test_phase5.py`):
    - Layout setup: tombol "Ubah Nama" dan "Menu Awal" terbukti tidak lagi berada di header atas; strip nama tampil di bawah tombol angka; tombol Menu Awal berada di bawah; tinggi tombol angka teruji >= 100px.
    - Sinkronisasi ubah nama: pengubahan nama ke "Garuda Sakti" langsung tampil di strip teks layar setup secara instan dan tersimpan.
    - Modal peran: verifikasi ketiadaan tombol ✕, tombol tunggal "Siap Menyelidiki Kasus" beroperasi, 4 peran ringkas berikon SVG tampil, spanduk aturan utama tampil utuh.
    - Penanda memori 1 kali: sesi pertama memunculkan modal peran; sesi kedua terbukti langsung membuka `screen-board` tanpa memunculkan modal peran lagi.
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Klik di area luar (backdrop) atau tombol Escape pada modal pengingat peran sebelumnya hanya menutup modal tanpa memicu pembukaan kasus, sehingga pengguna tertahan di layar setup.
  - *Perbaikan:* Menambahkan pemicu `startNewCaseSession()` pada penutupan modal pengingat peran lewat backdrop dan tombol Escape agar alur permainan tetap meluncur mulus ke papan kasus.
- **Keputusan:**
  - Menyimpan penanda `hasShownRoleReminder` murni di objek memori JavaScript `State` (bukan di `localStorage`) agar siswa dan guru selalu mendapatkan pengingat aturan saat pertama kali membuka halaman web di hari baru.

---

## FASE 6: LAYAR AWAL
- **Status:** SELESAI ✅
- **Apa yang dibuat/diubah:**
  1. Tipografi & Tata Letak Hero Layar Awal (`screen-start`):
     - Memperbesar judul "DETEKTIF NORMA" sekitar 1,5 kali (`clamp(48px, 8.5vh, 84px)`, mencapai 84px pada 1080p) dengan ketebalan 900, outline gelap 8px berkarakter, dan kerning 2px agar terbaca tegas dari bangku paling belakang kelas.
     - Menyederhanakan lencana di atas judul menjadi teks murni kurikulum: "PPKn KELAS 5 SD" (menghapus frasa "EDISI PEMBELAJARAN").
  2. Ilustrasi Vektor SVG Mandiri (Tema Kantor Detektif):
     - Menambahkan ilustrasi besar terpadu di sisi kiri layar hero (`.hero-detective-svg` di dalam `.hero-illustration-wrap`):
       - Berkas kasus krem fisik dengan tab arsip bertuliskan "KASUS #01 DETEKTIF" dan baris teks bukti.
       - Klip logam berkilau di sudut kiri atas dokumen.
       - Stempel merah cap bata miring bertuliskan "TERPECAHKAN".
       - Kaca pembesar detektif raksasa berbingkai emas, lensa kaca bening dengan pantulan cahaya melengkung, serta gagang kayu bertekstur cokelat.
       - Bintang emas pencapaian kecil di sekitar ilustrasi.
     - 100% vektor SVG murni inline tanpa dependensi file eksternal (bekerja mulus saat folder `assets/` kosong).
     - Menghubungkan variabel CSS `background-image: url("assets/bg-home.png");` dengan fallback warna hijau botol tua yang rapi jika gambar tidak tersedia.
  3. Tombol Aksi & Resume Terstruktur:
     - Tombol "MULAI PETUALANGAN BARU" tetap dirancang paling besar dan menonjol (`.start-btn-play`, tinggi 82px di 1080p, bayangan fisik 8px).
     - Tombol resume sesi sebelumnya disingkat menjadi: "Lanjutkan dengan X kelompok" dengan subjudul kecil di bawahnya yang memuat daftar nama kelompok tanpa memicu teks meluber atau bertumpuk.
  4. Bilah toolbar kecil (Suara ON/OFF, Layar Penuh, Cara Main, Peringkat, Tentang) tetap dipertahankan dengan rapi di bagian header atas menggunakan ikon SVG satu gaya dari Fase 1.
- **Apa yang diuji:**
  - Pengujian otomasi visual CDP Edge (`test_phase6.py`):
    - Uji 1920x1080: ukuran font judul teruji 84px (>= 70px); lencana terverifikasi persis "PPKn KELAS 5 SD"; ilustrasi SVG hadir; tombol Mulai memiliki tinggi 82px; tombol resume menampilkan "Lanjutkan dengan 5 kelompok" dan subteks tim; bebas scrollbar horizontal & vertikal (`hasVScroll: false`, `hasHScroll: false`).
    - Uji responsivitas 1366x768: ukuran judul menyesuaikan secara proporsional (65.28px), tata letak seimbang bebas overflow di kedua sumbu (`scrollHeight === clientHeight === 768`).
    - Verifikasi toolbar: kelima tombol toolbar (Suara, Layar Penuh, Cara Main, Peringkat, Tentang) terverifikasi utuh dengan ikon SVG.
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Pada tata letak hero awal, judul sempat bergeser ke tengah layar saat tombol resume muncul sehingga memicu lompatan tata letak (layout shift).
  - *Perbaikan:* Menata `.start-hero-grid` dengan flexbox dua kolom proporsional (kiri: ilustrasi vektor, kanan: judul & tombol aksi) sehingga tata letak tetap stabil dan seimbang baik saat tombol resume tersembunyi maupun muncul.
- **Keputusan:**
  - Mengatur ukuran maksimal teks subjudul nama kelompok di tombol resume dengan `text-overflow: ellipsis` agar nama kelompok yang sangat panjang tetap rapi dan tidak merusak batas tombol.

---

## FASE 7: PENGUJIAN MENYELURUH DAN PENUTUP (ITERASI v1.2)
- **Status:** SELESAI ✅
- **Apa yang dibuat & diuji:**
  1. Audit Kepatuhan & Standar Anti-Slop:
     - **0 Emojis di seluruh codebase:** Verifikasi otomatis lewat `audit_codebase.py` pada seluruh berkas (`index.html`, `style.css`, `game.js`, `data.js`).
     - **100% Offline-Ready:** Tidak ada request CDN luar atau font web eksternal.
     - **Warna Tombol Normal State:** Audit DOM terprogram pada seluruh tombol membuktikan 100% tombol memiliki background solid dan border tegas dalam kondisi normal/idle tanpa bergantung pada hover (aman untuk TV interaktif / layar sentuh).
  2. Pengujian Alur Penuh Permainan (`test_phase7_master_audit.py`):
     - Menjalankan 12 kasus penuh secara berurutan dengan 4 kelompok:
       - Penguncian kelompok & penguncian stempel norma saat tebakan salah terverifikasi aktif.
       - Giliran kelompok berikutnya terverifikasi berjalan lancar.
       - Skor petunjuk dan poin evaluasi alasan guru terhitung akurat.
       - Transisi otomatis ke layar hasil podium (`screen-result`) terbukti mulus tanpa error race-condition.
  3. Verifikasi Panggung Podium Hasil:
     - Teruji dengan 4 kelompok: 3 kolom podium di atas (Emas, Perak, Perunggu) dan 1 kartu kelompok ke-4 di baris bawah.
     - Format waktu koma lokal Indonesia (`13,3 dtk`), penanganan skor seri alami, dan lencana teranugerahkan tepat sasaran.
  4. Pengujian Responsivitas Bebas Scrollbar:
     - Resolusi 1920×1080: `hasVScroll: false`, `hasHScroll: false` (100% pas tanpa scrollbar).
     - Resolusi 1366×768: `hasVScroll: false`, `hasHScroll: false` (100% pas tanpa scrollbar).
  5. Pembaruan Dokumentasi:
     - `README.md` diperbarui mencakup daftar 36 ikon SVG mandiri, dukungan opsional wallpaper `assets/bg-home.png`, panduan ubah nama kelompok di layar setup, serta mekanisme podium hasil & lencana.
- **Bug yang ditemukan & Perbaikan:**
  - *Temuan:* Pada simulasi transisi cepat antar-kasus, jeda waktu fisik stempel (animasi 120ms tekan) membutuhkan penanganan asinkron agar DOM terbarui sebelum selektor kasus berikutnya dipanggil.
  - *Perbaikan:* Menyelaraskan event handler animasi CSS dengan penyelesaian kalkulasi state di JavaScript sehingga seluruh alur stabil.
- **Keputusan:**
  - Menjaga seluruh aturan skor, komposisi 24 kasus, dan format penyimpanan `localStorage` tetap identik agar kompatibel dengan PRD v1.1 dan sesi terdahulu.

---

## 🏆 KESIMPULAN AKHIR ITERASI v1.2
Seluruh 7 Fase Perbaikan Tampilan & UX Game **"Detektif Norma"** telah tuntas 100%:
1. **Fase 1:** 100% Emoji bersih digantikan 36 Sprite SVG mandiri satu gaya garis tebal 24px.
2. **Fase 2:** Stempel fisik "TERPECAHKAN" dengan tinta bertekstur SVG `feTurbulence`, zona khusus bebas overlap teks, dan Web Audio multi-layer.
3. **Fase 3:** Stempel karet norma fisik dengan gagang kayu, bantalan karet berwarna, dan 3 kondisi visual (Waiting, Active, Locked).
4. **Fase 4:** Layar Hasil Podium megah 3 balok fisik, tie-breaking pintar, lencana Skor Tertinggi & Tercepat, serta kotak refleksi ringkas.
5. **Fase 5:** Setup kelompok lapang dengan baris nama terintegrasi dan modal pengingat peran tunggal 1 kali kemunculan.
6. **Fase 6:** Hero Layar Awal berkarakter dengan judul 1.5x lebih besar dan ilustrasi vektor detektif mandiri.
7. **Fase 7:** Audit master lulus 100% di semua resolusi target, tanpa error, dan dokumentasi lengkap.

---

## 🛠️ PERBAIKAN UX LANJUTAN: TUNTAS TABRAKAN KARTU & PENAMPILAN PERTANYAAN ALASAN (DASAR & HOTS)
- **Status:** SELESAI & TERVERIFIKASI 100% ✅
- **1. Pengembalian ke Desain Taktil Asli (Sesuai Permintaan User - Persis Pict 3):**
  - Pendekatan overlay lembar berkas penuh (`.case-reason-overlay`) dibatalkan demi mempertahankan nuansa permainan anak yang taktil dan interaktif, di mana berkas kertas krem, 3 kartu petunjuk, cap stempel fisik "TERPECAHKAN" miring di kanan bawah, dan umpan balik tetap berada langsung di dalam alur berkas (in-place).
- **2. Penjelasan Kasus Dasar vs HOTS (Mengapa Sebelumnya Tidak Ada Pertanyaan di Kasus #02):**
  - Di bank soal (`data.js`):
    - **Kasus HOTS** (8 kasus) memiliki `pertanyaanLanjutan` berupa pertanyaan analisis mendalam.
    - **Kasus DASAR** (16 kasus, seperti kasus #02 Rina mengembalikan dompet) di data aslinya memiliki `pertanyaanLanjutan: null`.
    - Sebelumnya, kode hanya memunculkan kotak pertanyaan jika kasus tersebut HOTS (`tingkat === "hots"`). Akibatnya, pada Kasus Dasar, kotak pertanyaan disembunyikan total (`display: none`), sehingga guru dan siswa hanya melihat tombol evaluasi alasan tanpa ada teks pengarah apa pun, dan bagian tengah berkas tampak kosong melompong.
- **3. Solusi UX: Kartu Alasan Detektif untuk Semua Tipe Kasus:**
  - **Pada Kasus Dasar:**
    - Tag: `Tantangan Alasan Detektif (Lisan):`
    - Pertanyaan: *"Mengapa perbuatan ini termasuk dalam [Nama Norma]?"* (misal: Norma Kesusilaan).
    - Panduan Guru: Tampil contekan kunci alasan dari data kasus (*Panduan Guru: "Mengembalikan barang milik orang lain didorong oleh kejujuran hati nurani."*).
  - **Pada Kasus HOTS:**
    - Tag: `Pertanyaan Lanjutan Kasus (HOTS):`
    - Pertanyaan: Menampilkan pertanyaan lanjutan analitis dari data kasus.
  - Hasil: Siswa dan guru **selalu punya pertanyaan pemandu yang jelas**, ruang berkas tidak lagi kosong melompong, dan guru mudah menilai alasan berkat contekan panduan.
- **4. Solusi Bebas Tabrakan: Pengungkapan Progresif In-Place (2-Fase):**
  - **Fase 1 (Tebakan Tepat & Alasan Lisan Siswa):**
    - Saat kelompok menjawab benar, stempel "TERPECAHKAN" mendarat di kanan bawah.
    - Menampilkan banner umpan balik hijau: *"Tepat Sekali! [Kelompok] berhasil memecahkan kasus (+X Poin)!"*.
    - Menampilkan kartu pertanyaan alasan detektif (oranye/krem) + tombol evaluasi guru.
    - Kotak Penjelasan Norma dan tombol Kasus Berikutnya **disembunyikan** (`display: none`).
  - **Fase 2 (Penjelasan Materi & Lanjut Kasus):**
    - Begitu guru mengevaluasi alasan, kartu pertanyaan dan tombol evaluasi **disembunyikan**.
    - Banner umpan balik diperbarui: *"Hebat, [Kelompok]! Alasan lisan diterima (+X Poin Alasan)."*
    - Kotak Penjelasan Norma (`#explanation-box`) dan tombol *"Kasus Berikutnya"* ditampilkan.
    - Tinggi stabil ~135px, tidak pernah bertumpuk dengan Fase 1.
- **5. Hasil Uji Otomasi Headless Edge CDP (`verify_all.py`):**
  - **Kasus Dasar (k07 - Rina Dompet):**
    - 1920×1080: Jarak aman petunjuk ke kartu = **330 px** (Fase 1) & **371 px** (Fase 2). Scrollbar: **0**.
    - 1366×768: Jarak aman petunjuk ke kartu = **122 px** (Fase 1) & **137 px** (Fase 2). Scrollbar: **0**.
  - **Kasus HOTS (k12 - Kiki Difitnah):**
    - 1920×1080: Jarak aman petunjuk ke kartu = **330 px** (Fase 1) & **371 px** (Fase 2). Scrollbar: **0**.
    - 1366×768: Jarak aman petunjuk ke kartu = **95 px** (Fase 1) & **137 px** (Fase 2). Scrollbar: **0**.
  - 100% Emoji-Free & 100% Offline.

---

## 🏆 PERBAIKAN TOTAL LAYAR HASIL ("HASIL PENYELIDIKAN KELAS") - FASE 1 S.D. FASE 5
- **Status:** SELESAI & TERVERIFIKASI 100% ✅

### 1. FASE 1: TATA LETAK VERTIKAL 6 ZONA BEBAS OVERFLOW & BEBAS SCROLL
- **Apa yang diubah:**
  - Mengubah struktur `.result-stage-container` di `index.html` dan `style.css` menjadi tata letak flex vertikal terstruktur 6 zona:
    1. `(a)` Header: Judul "HASIL PENYELIDIKAN KELAS" & Subjudul "Semua detektif hebat dan belajar banyak hari ini!"
    2. `(b)` Info Bar Ringkas (`#result-info-bar`): 2 pil info ("X dari Y Kasus" & "Rata-rata menjawab X dtk")
    3. `(c)` Podium Utama (`#result-podium-container`): Balok fisik proporsional (Juara 1 tengah/tertinggi, Juara 2 kiri, Juara 3 kanan)
    4. `(d)` Baris Kelompok Sisa (`#result-remaining-container`): Peringkat 4 & 5 dalam baris horizontal rapi
    5. `(e)` Strip Bawah (`#result-bottom-strip`): Kotak refleksi HOTS & kotak kasus unsolved / sukses
    6. `(f)` Tombol Aksi (`.result-actions-footer`): 3 tombol taktil tinggi >= 80px (1080p) / >= 60px (768p)
  - Menerapkan variabel CSS proporsional: `--fs-result-title`, `--fs-result-score`, `--fs-result-team`, `--fs-result-body`, `--gap-result`.
  - Mengatasi masalah teks terpotong dengan `white-space: normal`, `overflow-wrap: break-word`, dan `word-break: break-word`.
  - Badge poin kelompok sisa dipastikan terkunci di dalam batas kartu (`scoreInside: true`).

### 2. FASE 2: STANDARISASI LENCANA (HANYA 2 LENCANA RESMI)
- **Apa yang diubah:**
  - Menghapus total 4 lencana lama yang memadati kartu: "Penakluk Tantangan", "Paling Gesit", "Paling Kritis", dan "Detektif Kompak".
  - Menetapkan HANYA 2 lencana resmi:
    1. **"Skor Tertinggi"** (Ikon piala `#icon-trophy`, emas): Diberikan kepada seluruh kelompok dengan skor tertinggi (`skor === maxScore`).
    2. **"Tercepat"** (Ikon stopwatch `#icon-stopwatch`, teal): Diberikan kepada 1 kelompok dengan waktu rata-rata tercepat **dengan syarat ketat minimal 3 jawaban benar** (`correctCount >= 3`).
  - Jika tidak ada kelompok yang mencapai 3 jawaban benar, lencana "Tercepat" tidak diberikan kepada siapa pun.
  - Kelompok yang tidak memenuhi syarat lencana tampil bersih tanpa lencana hiburan.

### 3. FASE 3: PERBAIKAN PODIUM, SKOR SERI, DAN TEKS WAKTU
- **Apa yang diubah:**
  - Penataan podium:
    - 3 kelompok atau lebih: Juara 2 di kiri (balok sedang ~105px), Juara 1 di tengah (balok tertinggi ~140px), Juara 3 di kanan (balok terpendek ~75px).
    - 2 kelompok: 2 balok (#1 di kiri/tengah, #2 di sisi kanan).
  - Penanganan skor seri:
    - Kelompok dengan skor sama mendapatkan nomor peringkat yang sama (misal dua kelompok di puncak sama-sama `#1`).
    - Diberikan label tegas `[SKOR SAMA]` pada balok peringkat untuk kelompok yang seri.
    - Tie-breaker posisi: diurutkan berdasarkan rata-rata waktu yang lebih cepat.
  - Pembersihan teks waktu:
    - Menghapus kalimat panjang berulang *"belum cukup 3 jawaban benar..."*.
    - Digantikan format ringkas: `⏱️ rata-rata X,X dtk`.
    - Jika kelompok belum mencapai 3 jawaban benar, ditampilkan tanda bintang `*` di samping waktu, disertai 1 catatan kaki di bawah: `* Peringkat kecepatan butuh minimal 3 jawaban benar.`
  - Ukuran teks TV 1080p:
    - Nama kelompok: 36.72px (memenuhi syarat min. 36px)
    - Skor: 59.4px (memenuhi syarat min. 56px)
    - Waktu: 24.84px (memenuhi syarat min. 24px)

### 4. FASE 4: STRIP INFO & KASUS YANG PERLU DIBAHAS
- **Apa yang diubah:**
  - Info bar atas: Hanya berisi 2 angka kunci (jumlah kasus terpecahkan & rata-rata kecepatan kelas). Teks non-informatif dihapus.
  - Strip bawah:
    - Kotak kiri: Pertanyaan refleksi kelas mengambil `pertanyaanLanjutan` dari kasus HOTS terakhir yang dimainkan. Teks membungkus utuh tanpa terpotong ellipsis. Sembunyi otomatis jika tidak ada kasus HOTS yang dimainkan.
    - Kotak kanan: Menampilkan maksimal 3 kartu kecil kasus gagal (unsolved) dengan nomor kasus, norma, dan potongan kasus.
    - Jika semua kasus berhasil dipecahkan, menampilkan kalimat apresiasi tunggal yang bersih: *"Semua kasus terpecahkan dengan baik!"*.

### 5. FASE 5: TOMBOL AKSI & HASIL PENGUJIAN MENYELURUH (CDP)
- **Pengujian Terprogram (`verify_result_screen.py`):**
  - **Skenario 1 (5 Kelompok, 0 Gagal, HOTS Ada, 1080p):**
    - Scrollbar: `False` (1080/1080)
    - Tinggi tombol: Replay = 84px, Lead = 80px, Menu = 80px (Semua >= 80px, font 24px)
    - Lencana di DOM: Hanya 'Skor Tertinggi' & 'Tercepat'
    - Catatan kaki `*`: Aktif (karena ada kelompok < 3 jawaban benar)
    - Pesan sukses: Tampil
  - **Skenario 2 (4 Kelompok, Seri di #1, 2 Gagal, 1080p):**
    - Scrollbar: `False` (1080/1080)
    - Tie tag: Kedua tim #1 memiliki badge `[SKOR SAMA]` dan balok emas 140px
    - Unsolved cases: 2 kartu pil tampil rapi
  - **Skenario 3 (3 Kelompok, Seri di #2, Semua < 3 Jawaban Benar, 1080p):**
    - Scrollbar: `False` (1080/1080)
    - Lencana 'Tercepat': 0 kelompok (aturan >= 3 jawaban benar terbukti ditegakkan)
    - Kotak refleksi: Tersembunyi (karena tidak ada kasus HOTS)
  - **Skenario 4 (2 Kelompok, 0 HOTS, 768p / 1366×768):**
    - Scrollbar: `False` (768/768)
    - Jumlah balok: 2 balok (#1 dan #2)
    - Tinggi tombol: Replay = 61.4px, Lead = 60px, Menu = 60px (Semua >= 60px)
  - **Skenario 5 (5 Kelompok, 4 Gagal / >3 Kasus, 768p / 1366×768):**
    - Scrollbar: `False` (768/768)
    - Pembatasan kasus gagal: Tepat dibatasi maks. 3 kartu pil
    - Bounding box badge skor kelompok 4 & 5: 100% berada di dalam kartu (`scoreInside: true`)
- **Hasil:** 100% Lolos Uji Otomasi CDP tanpa error.

---

## 📱 TAHAP RESPONSIF MOBILE (HP ANDROID & IPHONE) - v1.3

### FASE 1: FONDASI RESPONSIF HP
- **Status:** SELESAI & TERVERIFIKASI PENUH ✅
- **1. Hasil Audit Sebelum Perubahan (375×667, 390×844, 667×375, 844×390):**
  - *Letterboxing & Squeeze:* Akibat rasio tetap 16:9 dengan `transform: scale()`, game pada layar HP tegak menyusut drastis menjadi pita kecil di tengah layar (hanya 375×211 pada iPhone SE portrait; 390×219 pada iPhone 13/14 portrait).
  - *Target Sentuh < 44px:*
    - Tombol Menu di header berukuran 87×38px (< 44px tinggi).
    - Tombol Suara dan Layar Penuh berukuran 40×40px / 42×42px (< 44px).
    - Pada orientasi tegak, tombol stempel norma terhimpit parah hingga lebarnya hanya 8px (tinggi 80–94px), mustahil disentuh jari anak.
  - *Ukuran Teks < 14px:*
    - Ditemukan 31 hingga 45 elemen teks berukuran di bawah 14px (misal timer 12px, label sub-kelompok 11px, Menu 13px, nama kelompok 13px) karena menggunakan kalkulasi `clamp(..vh..)`.
  - *Tumpang Tindih / Collision (Kotak Petunjuk vs Lembar Alasan HOTS):*
    - Pada hp-tegak, ruang vertikal terbatas menyebabkan kotak petunjuk dan lembar alasan saling menimpa jika dibuka bersamaan. Dicatat sebagai target perbaikan tata letak di Fase 2 & 3.
- **2. Apa yang Diubah:**
  - `index.html`:
    - Menambahkan `viewport-fit=cover` pada `<meta name="viewport">` untuk menangani notch/pulau kamera iPhone & Android.
    - Menambahkan spanduk notifikasi ringan bebas emoji: `#inapp-browser-banner` (notifikasi pembuka browser eksternal) dan `#rotate-phone-banner` (saran memutar layar HP yang dapat ditutup).
    - Menambahkan panduan praktis pada modal Cara Main: *"Satu HP bisa dipakai bergantian: pemegang HP berperan sebagai guru. Di iPhone, matikan mode senyap agar suara terdengar."*
  - `style.css`:
    - Menambahkan `overscroll-behavior: none; -webkit-touch-callout: none;` pada `html, body` guna mencegah gesture pull-to-refresh dan callout pop-up default iOS.
    - Membuat variabel `:root` baru (`--btn-h-pri`, `--btn-h-sec`, `--btn-h-act`, `--btn-h-dan`, `--btn-h-sm`, `--btn-sz-icon`, `--board-margin`, `--board-border-sz`) sehingga ukuran tombol dan papan diatur dinamis lewat CSS variable tanpa mengganggu desktop.
    - Menambahkan media query murni responsif:
      - `@media (orientation: portrait) and (max-width: 820px)` (`hp-tegak`): `#app-viewport` beralih ke `position: fixed; inset: 0; width: 100%; height: 100dvh; transform: none; padding: env(safe-area-inset-*);`. Variabel font teks kasus diatur min 20px, tombol min 48px/52px.
      - `@media (orientation: landscape) and (max-height: 520px)` (`hp-mendatar`): `#app-viewport` beralih ke `position: fixed; inset: 0; width: 100%; height: 100dvh; transform: none; padding: env(safe-area-inset-*);`. Variabel font teks kasus diatur min 18px, tombol min 44px/48px.
      - Mode TV (1920×1080 dan 1366×768) 100% tidak terpengaruh oleh media query ini.
  - `game.js`:
    - Logika Layar Penuh: menyembunyikan kedua tombol fullscreen jika browser tidak mendukung API Fullscreen (`!(documentElement.requestFullscreen || webkitRequestFullscreen)`).
    - Kunci Orientasi HP: jika pengguna berada di perangkat layar sentuh mobile (`matchMedia("(pointer: coarse) and (max-width: 900px)")`), setelah memasuki fullscreen sistem memanggil `screen.orientation.lock("landscape")` (dalam blok try/catch yang aman); kuncinya otomatis dilepas saat keluar dari fullscreen.
    - Browser Dalam Aplikasi: mendeteksi WebView Instagram dan Facebook (`/Instagram|FBAN|FBAV/i`), menampilkan bilah anjuran buka di browser asli.
    - Saran Rotasi: menampilkan bilah anjuran putar HP hanya pada `hp-tegak`, dapat ditutup pengguna dan tidak memblokir permainan.
- **3. Apa yang Diuji & Hasil Verifikasi Otomasi (`test_phase1_hp.py`):**
  - **Uji Selisih Piksel TV / Desktop (Target: 0 Piksel):**
    - `Start Screen (1080p)`: 0 piksel berbeda ✅
    - `Board Screen (1080p)`: 0 piksel berbeda ✅
    - `Result Screen (1080p)`: 0 piksel berbeda ✅
    - `Start Screen (768p)`: 0 piksel berbeda ✅
    - `Board Screen (768p)`: 0 piksel berbeda ✅
    - `Result Screen (768p)`: 0 piksel berbeda ✅
    - **Hasil: 100% IDENTIK (Selisih piksel = 0)**
  - **Uji Scroll Halaman pada 4 Ukuran HP (Target: 0 Scroll):**
    - `iPhone SE Portrait (375×667)`: Page Scroll = False (Start: False, Board: False, Result: False) ✅
    - `iPhone 13/14 Portrait (390×844)`: Page Scroll = False (Start: False, Board: False, Result: False) ✅
    - `iPhone SE Landscape (667×375)`: Page Scroll = False (Start: False, Board: False, Result: False) ✅
    - `iPhone 13/14 Landscape (844×390)`: Page Scroll = False (Start: False, Board: False, Result: False) ✅
  - **Uji Rotasi & Resize HP:**
    - Perubahan ukuran dan rotasi layar dari tegak (390×844) ke mendatar (844×390) tidak mereset state permainan:
      - `currentCaseIndex`: tetap Case 0
      - `timerRunning`: tetap `True`
      - `timerSeconds`: terus berlanjut (2 detik ➔ 3 detik) tanpa reset
- **4. Keputusan:**
  - Sesuai aturan kerja iterasi, Fase 1 dituntaskan dan diverifikasi penuh terlebih dahulu sebelum menyentuh penataan tata letak spesifik grid/flex di Fase 2 (HP-Tegak) dan Fase 3 (HP-Mendatar).
  - Sesuai instruksi: **BERHENTI DAN LAPOR**.

---

### FASE 2: PAPAN KASUS DI HP TEGAK (390×844, 375×667, 360×640, 430×932)
- **Status:** SELESAI & TERVERIFIKASI PENUH ✅
- **1. Apa yang Diubah:**
  - `style.css` (Murni di dalam `@media (orientation: portrait) and (max-width: 820px)`):
    - **Grid Template Areas 5 Zona:** `#screen-board` disusun ulang menggunakan `grid-template-areas: "header" "teams" "case" "teacher" "stamps"` dengan `.board-main-area` dan `.board-center-case` disetel ke `display: contents` sehingga tidak merusak hierarki DOM.
    - **Header Satu Baris:** `#board-header` (Menu, progres kasus, penanda Kasus Tantangan, timer, tombol suara, tombol fullscreen) berada dalam 1 baris tanpa wrapping atau elemen bertumpuk. Tombol memiliki ukuran sentuh >= 44px.
    - **Strip Kelompok Horizontal:** `.teams-sidebar` diubah menjadi deretan chip horizontal nama + skor, tinggi 48px, dengan scroll horizontal otomatis jika bermain 5 kelompok. Kelompok yang aktif menjawab disorot terang (`.active-turn`).
    - **Berkas Kasus (Flex 1):** `#case-folder` menempati sisa ruang vertikal (`flex: 1 1 0`), teks kasus berukuran 20px (memenuhi syarat min 20px), dan 3 petunjuk bertahap ditumpuk secara vertikal dan ringkas.
    - **Bilah Guru:** 4 tombol berderet (`#btn-unlock-clue`, `#btn-pause-game`, `#btn-cancel-turn`, `#btn-finish-now`), ikon di atas label, tinggi 48px, satu ketukan per aksi. Urutan tombol diatur via CSS `order`: (1) Buka Petunjuk, (2) Jeda, (3) Batalkan, (4) Selesai. Tombol "Selesai Sekarang" tetap berwarna beda (`.btn-danger`).
    - **Empat Stempel Norma:** Ditata dalam grid 2×2, tinggi 56px per stempel, menampilkan ikon SVG + nama norma tegas + keterangan kecil, gagang kayu disembunyikan agar seluruh area stempel responsif sentuhan.
    - **Bottom Sheet:** Panel evaluasi alasan + penjelasan + "Alasan masuk akal" (tahan 1 detik) + "Lanjut/Kasus Berikutnya" menjadi bottom sheet (`position: fixed; bottom: 0; max-height: 62%`, scroll internal, tombol aksi menempel di bawah sheet). Teks kasus tetap terlihat di atas sheet. Banner feedback menyatu di kepala sheet. Stempel TERPECAHKAN tampil di sudut kanan atas berkas dan tidak tertutup sheet.
- **2. Apa yang Diuji & Hasil Verifikasi Otomasi (`test_phase2_hp.py`):**
  - **Uji Selisih Piksel TV / Desktop (Target: 0 Piksel):**
    - `Start Screen (1080p)`: 0 piksel berbeda ✅
    - `Board Screen (1080p)`: 0 piksel berbeda ✅
    - `Result Screen (1080p)`: 0 piksel berbeda ✅
    - `Start Screen (768p)`: 0 piksel berbeda ✅
    - `Board Screen (768p)`: 0 piksel berbeda ✅
    - `Result Screen (768p)`: 0 piksel berbeda ✅
    - **Hasil: 100% IDENTIK DENGAN BASELINE ASLI (Selisih piksel = 0)**
  - **Uji 4 Ukuran HP Tegak (390×844, 375×667, 360×640, 430×932) untuk 2 dan 5 Kelompok (termasuk kasus HOTS terpanjang):**
    - `Page Scroll`: `False` (0 scroll) pada seluruh ukuran dan jumlah kelompok ✅
    - `Teks Kasus Font`: 20px (Target: >= 20px) ✅
    - `Tinggi Tombol Bilah Guru`: 48.0px (Target: >= 48px) ✅
    - `Tinggi Stempel Norma`: 56.0px (Target: >= 56px) ✅
    - `Tinggi Chip Kelompok`: 48.0px (Target: >= 48px) ✅
    - `Deteksi Tumpang Tindih (Header, Strip, Berkas, Bilah Guru, Stempel)`: 0 overlap (`False`) ✅
    - `Scroll Horizontal Chip 5 Kelompok`: `True` (scroll-x lancar) ✅
    - `Bottom Sheet Height`: 32.5% – 41.7% (Target: <= 62%) ✅
    - `Teks Kasus di Atas Sheet`: `True` (terbaca utuh tanpa tertutup) ✅
    - `Stempel TERPECAHKAN Tidak Tertutup Sheet`: `True` (tampil di sudut atas berkas) ✅
    - `Banner Feedback di Kepala Sheet`: `True` ✅
    - `Tinggi Tombol Alasan Masuk Akal & Lanjut`: 48.0px (Target: >= 48px) ✅
    - `Tinggi Tombol Kasus Berikutnya`: 48.0px (Target: >= 48px, menempel di bawah sheet) ✅
  - **Uji Simulasi Penuh 12 Kasus di HP Tegak:**
    - Menyelesaikan 12 kasus berturut-turut dari kasus 1 hingga 12 dengan rotasi giliran 5 kelompok.
    - Pindah ke layar hasil (`screen-result`) dengan lancar tanpa error ✅
- **3. Keputusan:**
  - Seluruh layout HP Tegak diimplementasikan murni lewat CSS tanpa mengubah struktur DOM atau ID elemen `index.html`.
  - Sesuai instruksi: **BERHENTI DAN LAPOR**.

---

### FASE 3: PAPAN KASUS DI HP MENDATAR (667x375, 844x390, 740x360, 932x430)
- **Status:** SELESAI & TERVERIFIKASI PENUH ✅
- **1. Apa yang Diubah:**
  - `style.css` (Murni di dalam `@media (orientation: landscape) and (max-height: 520px)`):
    - **Grid Template Areas Papan Kasus:** `#screen-board` disusun dengan `grid-template-columns: 1fr 96px`, `grid-template-rows: auto auto 1fr auto`, dan `grid-template-areas: "header header" "teams teams" "case teacher" "stamps stamps"`.
    - **Header Satu Baris Tipis:** `#board-header` disetel tinggi 38px (rentang target: 36-40px), memuat tombol Menu, indikator progres & HOTS, timer, tombol suara, dan tombol fullscreen.
    - **Strip Kelompok Tipis di Bawah Header:** `.teams-sidebar` disetel tinggi 34px (rentang target: 32-34px) dengan kartu kelompok model chip horizontal 32px, menampilkan nama, dot warna, dan badge skor, dengan dukungan scroll horizontal jika bermain 5 kelompok.
    - **Area Tengah (Berkas Kasus & Petunjuk Horizontal):** `#case-folder` memakai sisa lebar layar di sebelah kiri rel guru, teks kasus berukuran 18px (`--fs-case`), dan 3 kotak petunjuk berderet horizontal (`grid-template-columns: repeat(3, 1fr)`).
    - **Rel Guru di Sisi Kanan:** `.teacher-sidebar` disetel lebar 96px di sisi kanan berkas kasus, memuat 4 tombol vertikal dengan tinggi minimal >= 44px (ikon di atas label: Petunjuk, Jeda, Batal, Selesai). Tombol "Selesai Sekarang" tetap berwarna merah bahaya (`.btn-danger`).
    - **Stempel Norma Satu Baris di Bawah:** `.stamps-section` menata 4 stempel norma dalam satu baris horizontal (4 kolom, tinggi 54px, rentang target: 52-56px). Keterangan kecil norma disembunyikan (`display: none`), sedangkan nama norma dan ikon SVG tetap tampil jelas dan kontras.
    - **Bottom Sheet Alasan & Penjelasan:** Panel evaluasi alasan diformat menjadi bottom sheet (`position: fixed; bottom: 0; max-height: min(70%, calc(100vh - 128px))`, scroll internal, tombol aksi menempel di bawah sheet).
    - **Stempel TERPECAHKAN di Sudut Berkas:** `#stamp-terpecahkan` diposisikan di sudut kanan atas berkas kasus dengan ukuran proporsional (`scale(0.38)`), sehingga tetap terlihat utuh dan tidak tertutup oleh bottom sheet pada seluruh ukuran layar landscape.
    - **Penanganan Animasi Bounce:** Menonaktifkan animasi keyframe `stamp-bounce` pada `#case-folder` di mode mobile agar browser tidak membentuk containing block baru yang dapat memerangkap elemen `position: fixed`.
- **2. Apa yang Diuji & Hasil Verifikasi Otomasi (`test_phase3_hp.py`):**
  - **Uji Selisih Piksel TV / Desktop (Target: 0 Piksel):**
    - `Start Screen (1080p)`: 0 piksel berbeda ✅
    - `Board Screen (1080p)`: 0 piksel berbeda ✅
    - `Result Screen (1080p)`: 0 piksel berbeda ✅
    - `Start Screen (768p)`: 0 piksel berbeda ✅
    - `Board Screen (768p)`: 0 piksel berbeda ✅
    - `Result Screen (768p)`: 0 piksel berbeda ✅
    - **Hasil: 100% IDENTIK DENGAN BASELINE ASLI (Selisih piksel = 0)**
  - **Uji 4 Ukuran HP Mendatar (667x375, 844x390, 740x360, 932x430) untuk 2 dan 5 Kelompok (termasuk kasus HOTS terpanjang):**
    - `Page Scroll`: `False` (0 scroll) pada semua ukuran dan skenario ✅
    - `Tinggi Header`: 38.0px (Target: 36-40px) ✅
    - `Tinggi Strip Kelompok`: 34.0px (Target: 32-34px) ✅
    - `Petunjuk 1-3 Horizontal`: `True` (3 kolom horizontal) ✅
    - `Lebar Rel Guru`: 96.0px (Target: ~96px) ✅
    - `Tinggi Tombol Rel Guru`: 53.0px - 70.5px (Target: >= 44px) ✅
    - `Tinggi Stempel Norma`: 54.0px (Target: 52-56px, 1 baris 4 kolom) ✅
    - `Keterangan Kecil Stempel Norma Tersembunyi`: `True` ✅
    - `Deteksi Tumpang Tindih (Header, Strip, Berkas, Rel Guru, Stempel)`: 0 overlap (`False`) ✅
    - `Bottom Sheet Height`: 64.4% - 67.4% (Target: <= 70%) ✅
    - `Teks Kasus di Atas Sheet`: `True` (terbaca utuh tanpa tertutup) ✅
    - `Stempel TERPECAHKAN Tidak Tertutup Sheet`: `True` (tampil di sudut atas berkas) ✅
    - `Tinggi Tombol Alasan Masuk Akal & Lanjut`: 44.0px (Target: >= 44px) ✅
    - `Tinggi Tombol Kasus Berikutnya`: 44.0px (Target: >= 44px, menempel di bawah sheet) ✅
  - **Uji Rotasi dari Tegak ke Mendatar di Tengah Permainan:**
    - State sebelum rotasi: Case=0, Timer=2s, Running=True, ActiveTeam=2
    - State setelah rotasi: Case=0, Timer=3s, Running=True, ActiveTeam=2
    - **Hasil: State, timer, dan kelompok terpilih tidak berubah sama sekali ✅**
  - **Uji Simulasi Penuh 12 Kasus di HP Mendatar (844x390):**
    - Menyelesaikan 12 kasus berturut-turut dari kasus 1 hingga 12 dalam orientasi landscape.
    - Berhasil transisi ke layar hasil (`screen-result`) dengan perhitungan skor dan lencana akurat ✅
- **3. Keputusan:**
  - Layout HP Mendatar didefinisikan murni lewat media query `@media (orientation: landscape) and (max-height: 520px)`.
  - ID elemen, struktur DOM, logika skor, timer, dan aturan alur game 100% dipertahankan tanpa perubahan.
  - Sesuai instruksi: **BERHENTI DAN LAPOR**.

---

### FASE 4: LAYAR LAIN DI HP (TEGAK DAN MENDATAR)
- **Status:** SELESAI & TERVERIFIKASI PENUH ✅
- **1. Apa yang Diubah:**
  - `style.css` (Murni di dalam media query mobile):
    - **Layar Awal (`#screen-start`):**
      - Judul diskalakan dengan aman menggunakan `clamp(22px, 6.8vw, 32px)` pada HP Tegak dan `20px` pada HP Mendatar.
      - Tombol Mulai berukuran besar (tinggi minimal 52px di tegak, 44px di mendatar, mudah dijangkau jempol).
      - Tombol toolbar kecil menggunakan flex wrap pada HP tegak dan baris tipis pada HP mendatar sehingga muat di seluruh lebar layar tanpa terpotong.
      - Ilustrasi SVG detektif diskalakan proporsional (`max-height: clamp(60px, 14vh, 120px)`) agar footer kredit materi Bu Fina & hak cipta Mas Dirga tetap tampil utuh tanpa scroll.
    - **Setup Kelompok (`#screen-setup`):**
      - Tombol pilihan jumlah kelompok (2, 3, 4, 5) ditata dalam satu baris grid (`repeat(4, 1fr)`), tinggi >= 52px di tegak dan >= 44px di mendatar.
      - Pratinjau nama kelompok aktif dengan tombol Ubah. Input penamaan di modal edit nama dilengkapi `scrollIntoView` otomatis saat fokus agar tidak tertutup virtual keyboard ponsel.
    - **Modal-Modal (`modal-rules`, `modal-about`, `modal-role-reminder`, `modal-edit-names`):**
      - Tinggi maksimal dibatasi `90dvh` (dengan fallback `90vh`).
      - Bagian isi menggunakan scroll vertikal mandiri (`overflow-y: auto`, `-webkit-overflow-scrolling: touch`).
      - Tombol tutup ✕ dan tombol konfirmasi selalu terlihat dengan target sentuh minimal 44px.
    - **Blok Pindai QR di Modal Tentang (`#qr-mobile-block`):**
      - Menampilkan kartu kode QR dengan ilustrasi dari `assets/qr-detektif-norma.png` dan alamat teks `detektif-norma.pages.dev`.
      - Dilengkapi penanganan `onerror` cerdas yang otomatis menyembunyikan blok jika berkas gambar tidak ditemukan, tanpa memicu error atau merusak layout.
    - **Layar Hasil Penyelidikan (`#screen-result`):**
      - Podium juara menyesuaikan lebar layar ponsel (100% lebar, tanpa scroll horizontal).
      - Kelompok peringkat 4 dan 5 tampil sebagai kartu horizontal penuh lebar (`remaining-team-card`) sehingga teks tidak bertumpuk atau patah.
      - Lencana prestasi tetap terbaca jelas (`podium-badge`).
      - Tiga tombol aksi (Main Lagi, Peringkat, Menu Utama) menempel rapi di bagian bawah layar (`position: sticky; bottom: 0`) dengan tinggi >= 44px.
    - **Papan Peringkat (`#screen-leaderboard`):**
      - Baris tabel beralih menjadi format kartu fleksibel per baris di HP tegak (`#leaderboard-rows tr` display flex column).
      - Tombol bilah alat guru (Ekspor, Impor, Hapus) membungkus rapi dalam lebar layar ponsel.
      - Input file impor cadangan menggunakan teknik cross-platform (`position: absolute; opacity: 0; width: 1px; height: 1px;`) yang bekerja sempurna di browser seluler Android dan iOS Safari tanpa diblokir sistem keamanan file picker.
- **2. Apa yang Diuji & Hasil Verifikasi Otomasi (`test_phase4_hp.py`):**
  - **Uji Selisih Piksel TV / Desktop (Target: 0 Piksel):**
    - `Start Screen (1080p)`: 0 piksel berbeda ✅
    - `Board Screen (1080p)`: 0 piksel berbeda ✅
    - `Result Screen (1080p)`: 0 piksel berbeda ✅
    - `Start Screen (768p)`: 0 piksel berbeda ✅
    - `Board Screen (768p)`: 0 piksel berbeda ✅
    - `Result Screen (768p)`: 0 piksel berbeda ✅
    - **Hasil: 100% IDENTIK DENGAN BASELINE ASLI (Selisih piksel = 0)**
  - **Uji Layar Awal di 5 Viewport HP (Tegak & Mendatar):**
    - `Page Scroll`: `False` (0 scroll) pada iPhone 13/14, iPhone SE, Android Small Portrait, iPhone SE Landscape, Android Small Landscape ✅
    - `Judul Pas di Layar`: `True` ✅
    - `Tinggi Tombol Mulai`: 52.0px di Tegak, 44.0px di Mendatar (Target: >= 44px) ✅
    - `Toolbar Muat Lebar`: `True` ✅
    - `Footer Kredit Utuh`: `True` ✅
  - **Uji Setup Kelompok & Ubah Nama:**
    - `Tombol 2,3,4,5 Muat 1 Baris`: `True` ✅
    - `Tinggi Tombol Pilihan`: 56.0px - 61.0px (Target: >= 44px) ✅
    - `Modal Edit Nama Max Height`: <= 90% (47% - 90%) ✅
    - `Fokus Input & ScrollIntoView`: `True` ✅
  - **Uji Seluruh Modal:**
    - `Tinggi Modal Card`: <= 90dvh (84.9% - 90.0%) ✅
    - `Tinggi Tombol Tutup / Aksi`: 44.0px - 48.0px (Target: >= 40px) ✅
    - `Scroll Internal Modal Body`: `True` ✅
    - `Konfigurasi Blok QR di Modal Tentang`: `True` ✅
  - **Uji Layar Hasil Penyelidikan:**
    - `Bebas Scrollbar Halaman`: `True` ✅
    - `Podium Pas di Lebar Layar`: `True` ✅
    - `Kartu Tim Peringkat 4 & 5 Penuh Lebar`: `True` (width >= 75% viewport) ✅
    - `Lencana Terlihat & Terbaca`: `True` ✅
    - `Tombol Aksi Menempel di Bawah`: `True` (Sticky bottom) ✅
    - `Tinggi Tombol Aksi`: 44.0px (Target: >= 44px) ✅
  - **Uji Papan Peringkat:**
    - `Bebas Scrollbar Halaman`: `True` ✅
    - `Tampilan Kartu di HP Tegak`: `True` (Display flex column) ✅
    - `Tombol Admin Guru Muat Lebar`: `True` ✅
    - `Input File Cadangan Cross-Platform`: `True` ✅
- **3. Keputusan:**
  - Seluruh layout layar tambahan HP dibuat murni lewat CSS media query yang terisolasi ketat.
  - Sesuai instruksi: **BERHENTI DAN LAPOR**.

---

### FASE 5: QA DAN REGRESI (FINAL LAPORAN)
- **Status:** SELESAI & TERVERIFIKASI PENUH ✅
- **1. Apa yang Dikerjakan:**
  - Menjalankan matriks pengujian otomatis menyeluruh melalui Chrome DevTools Protocol (CDP) dengan `Emulation.setDeviceMetricsOverride` dan `Emulation.setTouchEmulationEnabled`.
  - Menguji 12 resolusi perangkat:
    - 6 Resolusi HP Tegak: 360x640, 375x667, 390x844, 412x915, 430x932, 768x1024.
    - 6 Resolusi HP Mendatar: 640x360, 667x375, 844x390, 915x412, 932x430, 1024x768.
    - Ditambah resolusi TV Interaktif: 1920x1080 dan 1366x768.
  - Memverifikasi setiap layar (Layar Awal, Setup Kelompok, Papan Kasus semua fase, Layar Hasil, Papan Peringkat, serta 4 Modal):
    - `scrollWidth` dan `scrollHeight` tidak melebihi viewport (halaman utama 0 scrollbar).
    - Tidak ada elemen yang keluar batas layar.
    - Tidak ada tumpang tindih area utama.
    - Ukuran tombol interaktif memenuhi standar sentuhan (HP >= 44px, TV >= 80px untuk tombol utama).
    - Konsol peramban bersih (0 error console / exception).
  - Menjalankan 3 sesi permainan berturut-turut di TV 1080p tanpa reload halaman untuk membuktikan stabilitas memori dan siklus state.
  - Menjalankan sesi 12 kasus penuh dengan 2 dan 5 kelompok di mode HP tegak dan mendatar.
  - Menambahkan bab dokumentasi *"Panduan Bermain di HP (Android & iPhone)"* ke dalam `README.md`.
- **2. Ringkasan Hasil Pengujian:**
  - **Regresi TV (1080p & 768p):** 0 piksel berbeda terhadap baseline awal (100% pixel-perfect preservation) ✅
  - **Stabilitas 3 Sesi TV Tanpa Reload:** Berhasil menyelesaikan 3 sesi berturut-turut dengan skor dan lencana akurat ✅
  - **Matriks Responsif 12 Resolusi:** 100% lolos verifikasi layout, bebas scroll luar, dan target sentuhan valid ✅
  - **Simulasi 12 Kasus HP (2 dan 5 Tim):** Transisi lancar, podium 2 kolom untuk 2 tim, podium 3 kolom + 2 kartu sisa untuk 5 tim ✅
  - **Console Error:** 0 error terdeteksi ✅
- **3. Keputusan:**
  - Aplikasi siap untuk dirilis dan dipush ke repositori GitHub.
