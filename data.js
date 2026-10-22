/**
 * Detektif Norma - data.js
 * Berkas data dan validasi mandiri
 * Sesuai PRD v1.1 Bagian 7 & Silabus PPKn Kelas 5 SD
 */

const NORMA_LIST = [
  {
    id: "agama",
    nama: "Norma Agama",
    keteranganKecil: "dari ajaran agama & firman Tuhan",
    warna: "#1D6A78", // Biru laut tua / Teal pekat detektif
    warnaTeks: "#FFFFFF",
    warnaBorder: "#0F3D45"
  },
  {
    id: "kesusilaan",
    nama: "Norma Kesusilaan",
    keteranganKecil: "dari hati nurani & kejujuran kalbu",
    warna: "#A93226", // Merah bata / Terakota hangat
    warnaTeks: "#FFFFFF",
    warnaBorder: "#6E1F17"
  },
  {
    id: "kesopanan",
    nama: "Norma Kesopanan",
    keteranganKecil: "dari tata krama pergaulan & adat",
    warna: "#2D6A4F", // Hijau botol / Hijau daun tua
    warnaTeks: "#FFFFFF",
    warnaBorder: "#1B4332"
  },
  {
    id: "hukum",
    nama: "Norma Hukum",
    keteranganKecil: "aturan resmi negara & sanksi tegas",
    warna: "#935116", // Cokelat umber / Kayu matang
    warnaTeks: "#FFFFFF",
    warnaBorder: "#5C310D"
  }
];

const KELOMPOK_DEFAULT = [
  { id: "tim1", nama: "Tim Elang", warna: "#B03A2E", warnaBorder: "#78281F", warnaTeks: "#FFFFFF" },
  { id: "tim2", nama: "Tim Harimau", warna: "#BA4A00", warnaBorder: "#7E3200", warnaTeks: "#FFFFFF" },
  { id: "tim3", nama: "Tim Kancil", warna: "#1E8449", warnaBorder: "#145A32", warnaTeks: "#FFFFFF" },
  { id: "tim4", nama: "Tim Banteng", warna: "#2874A6", warnaBorder: "#1B4F72", warnaTeks: "#FFFFFF" },
  { id: "tim5", nama: "Tim Rusa", warna: "#7D6608", warnaBorder: "#514305", warnaTeks: "#FFFFFF" }
];

const KASUS_POOL = [
  // =================== NORMA AGAMA: 4 DASAR ===================
  {
    id: "k01",
    tingkat: "dasar",
    kasus: "Dito selalu berdoa dengan khusyuk sebelum mulai menyantap makanan yang disajikan ibunya di meja makan.",
    jawabanId: "agama",
    petunjuk: [
      "Aturan ini bersumber dari keyakinan terhadap Tuhan Yang Maha Esa.",
      "Pelanggaran terhadap aturan ini mendatangkan rasa berdosa kepada Sang Pencipta.",
      "Perilaku ini merupakan bentuk syukur dan ibadah dalam kehidupan sehari-hari."
    ],
    pertanyaanLanjutan: null,
    alasan: "Berdoa sebelum makan adalah perintah ajaran agama sebagai wujud rasa syukur kepada Tuhan.",
    penjelasan: "Berdoa bersumber dari wahyu ajaran agama. Perilaku ini juga mendidik adab yang baik dalam bersantap."
  },
  {
    id: "k02",
    tingkat: "dasar",
    kasus: "Siti rajin menjalankan ibadah tepat waktu bersama keluarganya di rumah sesuai ajaran keyakinannya.",
    jawabanId: "agama",
    petunjuk: [
      "Pedoman perilaku ini termuat dalam kitab suci.",
      "Sanksi tidak langsung terasa di dunia, melainkan berupa ganjaran di akhirat.",
      "Ini adalah kewajiban manusia kepada Tuhan Yang Maha Esa."
    ],
    pertanyaanLanjutan: null,
    alasan: "Menjalankan ibadah tepat waktu merupakan kewajiban pokok dari ajaran agama.",
    penjelasan: "Ibadah bersumber dari firman Tuhan. Melaksanakannya melatih kedisiplinan hidup dan keimanan."
  },
  {
    id: "k03",
    tingkat: "dasar",
    kasus: "Edo mengingatkan temannya untuk tidak menghina cara beribadah orang lain saat jam istirahat sekolah.",
    jawabanId: "agama",
    petunjuk: [
      "Terkait dengan penghayatan nilai keimanan dan ketakwaan.",
      "Tuntunan ini mengajarkan kasih sayang dan larangan menodai kesucian ibadah.",
      "Aturan ini bersumber dari ajaran Tuhan untuk saling menjaga kerukunan umat."
    ],
    pertanyaanLanjutan: null,
    alasan: "Menghormati kesucian ibadah orang lain diperintahkan oleh ajaran agama.",
    penjelasan: "Agama melarang penodaan ibadah sesama. Sikap rukun ini juga mendukung norma kesopanan dan hukum."
  },
  {
    id: "k04",
    tingkat: "dasar",
    kasus: "Lani menyisihkan sebagian uang sakunya untuk dimasukkan ke kotak amal tempat ibadah setiap Jumat.",
    jawabanId: "agama",
    petunjuk: [
      "Perbuatan ini didasari niat tulus mencari rida Sang Pencipta.",
      "Pahalanya dipercaya menjadi bekal kebaikan di kehidupan kelak.",
      "Perilaku sedekah ini diperintahkan dalam ajaran kitab suci."
    ],
    pertanyaanLanjutan: null,
    alasan: "Bersedekah di kotak amal tempat ibadah adalah amalan yang diajarkan oleh agama.",
    penjelasan: "Sedekah bersumber dari perintah agama untuk menolong sesama dan melatih keikhlasan."
  },

  // =================== NORMA AGAMA: 2 HOTS ===================
  {
    id: "k05",
    tingkat: "hots",
    kasus: "Saat bermain bola bersama teman, Budi pamit pulang lebih awal karena waktu ibadah telah tiba.",
    jawabanId: "agama",
    petunjuk: [
      "Tokoh menghadapi pilihan antara kesenangan pergaulan dengan panggilan iman.",
      "Prioritas utama tindakan ini adalah menunaikan kewajiban kepada Sang Pencipta.",
      "Ketaatan pada perintah Tuhan diletakkan di atas kepentingan bermain bersama."
    ],
    pertanyaanLanjutan: "Mengapa menunaikan kewajiban beribadah harus diutamakan daripada melanjutkan permainan bersama teman?",
    alasan: "Kewajiban kepada Tuhan berkedudukan lebih utama dibanding kesenangan bermain.",
    penjelasan: "Ketaatan beribadah berakar pada norma agama. Budi juga pamit dengan santun (norma kesopanan)."
  },
  {
    id: "k06",
    tingkat: "hots",
    kasus: "Doni membatalkan niat mengambil buah tetangga saat lapar karena teringat Tuhan selalu melihat perbuatannya.",
    jawabanId: "agama",
    petunjuk: [
      "Tidak ada orang yang melihat, tetapi ia merasa ada Pengawas Yang Maha Mengetahui.",
      "Rasa takut akan dosa menghentikan niat buruk yang hendak dilakukan.",
      "Keyakinan akan pengawasan Tuhan menjadi rem utama perbuatannya."
    ],
    pertanyaanLanjutan: "Apa perbedaan antara menahan diri karena takut dilihat tetangga dengan menahan diri karena takut kepada Tuhan?",
    alasan: "Menahan diri karena keyakinan pengawasan Tuhan berasal langsung dari ajaran agama.",
    penjelasan: "Kesadaran diawasi Tuhan adalah buah norma agama. Tindakan ini sekaligus mencegah pelanggaran hukum dan susila."
  },

  // =================== NORMA KESUSILAAN: 4 DASAR ===================
  {
    id: "k07",
    tingkat: "dasar",
    kasus: "Rina segera mengembalikan dompet berisi uang yang terjatuh di halaman sekolah kepada pemiliknya.",
    jawabanId: "kesusilaan",
    petunjuk: [
      "Perilaku ini didorong oleh suara hati nurani yang mengutamakan kejujuran.",
      "Bila dompet disimpan sendiri, hati pelakunya akan merasa bersalah dan gelisah.",
      "Aturan ini bersumber dari bisikan kalbu tentang mana yang benar dan salah."
    ],
    pertanyaanLanjutan: null,
    alasan: "Mengembalikan barang milik orang lain didorong oleh kejujuran hati nurani.",
    penjelasan: "Kejujuran bersumber dari hati nurani (kesusilaan). Sikap ini juga mencegah pelanggaran norma hukum."
  },
  {
    id: "k08",
    tingkat: "dasar",
    kasus: "Bani mengakui dengan jujur bahwa ia tidak sengaja memecahkan vas bunga di ruang tamu.",
    jawabanId: "kesusilaan",
    petunjuk: [
      "Perilaku ini lahir dari keberanian bersikap jujur pada diri sendiri.",
      "Sanksinya bukan berupa penjara, melainkan beban batin bila berbohong.",
      "Tindakan ini bersumber dari hati nurani yang menolak kebohongan."
    ],
    pertanyaanLanjutan: null,
    alasan: "Mengakui kesalahan sendiri merupakan wujud kejujuran hati nurani.",
    penjelasan: "Mengakui kesalahan bersumber dari hati nurani (kesusilaan), sekaligus bentuk tanggung jawab pribadi."
  },
  {
    id: "k09",
    tingkat: "dasar",
    kasus: "Aris merasa malu dan menyesal di dalam hatinya setelah sempat berniat menyontek saat ulangan.",
    jawabanId: "kesusilaan",
    petunjuk: [
      "Gejolak rasa ini terjadi di dalam batin pelakunya sendiri.",
      "Sanksi yang dialami berupa penyesalan mendalam dan rasa bersalah.",
      "Aturan moral ini lahir dari hati nurani manusia yang menuntut kejujuran."
    ],
    pertanyaanLanjutan: null,
    alasan: "Rasa menyesal dan menolak menyontek timbul dari bisikan hati nurani.",
    penjelasan: "Hati nurani menghasilkan rasa malu saat berniat curang (kesusilaan). Menyontek juga melanggar tata tertib sekolah."
  },
  {
    id: "k10",
    tingkat: "dasar",
    kasus: "Maya menolong anak kucing yang terjepit pagar karena merasa iba dan kasihan melihatnya menderita.",
    jawabanId: "kesusilaan",
    petunjuk: [
      "Dorongan tindakan ini timbul dari rasa welas asih dan perikemanusiaan.",
      "Tidak ada hukum tertulis yang mewajibkan, tetapi batin tergerak membantu.",
      "Kebaikan ini murni bersumber dari kelembutan hati nurani."
    ],
    pertanyaanLanjutan: null,
    alasan: "Rasa iba dan tergerak menolong makhluk hidup bersumber dari kebaikan hati nurani.",
    penjelasan: "Rasa kasihan dan welas asih lahir dari lubuk hati nurani yang bersih (kesusilaan)."
  },

  // =================== NORMA KESUSILAAN: 2 HOTS ===================
  {
    id: "k11",
    tingkat: "hots",
    kasus: "Fajar tetap mengakui gol lawan meski wasit tidak melihat bolanya sudah masuk garis gawang.",
    jawabanId: "kesusilaan",
    petunjuk: [
      "Tokoh bisa saja diam untuk kemenangan timnya, namun memilih bersikap jujur.",
      "Ia memilih kejujuran batin daripada kemenangan yang diperoleh dengan kepalsuan.",
      "Suara hati nuraninya mengalahkan godaan untuk berbuat curang demi kemenangan."
    ],
    pertanyaanLanjutan: "Mengapa kejujuran hati nurani lebih berharga daripada kemenangan yang diraih dengan cara pura-pura tidak tahu?",
    alasan: "Kejujuran batin menolak kecurangan demi keadilan dan kedamaian hati nurani.",
    penjelasan: "Sportivitas sejati berakar pada norma kesusilaan (hati nurani). Ini juga menghormati aturan permainan."
  },
  {
    id: "k12",
    tingkat: "hots",
    kasus: "Kiki membela temannya yang difitnah mengambil uang, meskipun teman-teman lain mendiamkan fitnah tersebut.",
    jawabanId: "kesusilaan",
    petunjuk: [
      "Tokoh berani bersuara demi membela kebenaran yang diketahuinya secara pasti.",
      "Batinnya merasa tidak tenang jika membiarkan orang tak bersalah menanggung derita.",
      "Keberanian menegakkan kebenaran ini bersumber dari kemurnian hati nurani."
    ],
    pertanyaanLanjutan: "Apa yang akan terjadi pada hati nurani kita jika kita membiarkan kebohongan menimpa teman yang tidak bersalah?",
    alasan: "Membela kebenaran melawan fitnah adalah panggilan murni hati nurani dan empati moral.",
    penjelasan: "Membela orang benar bersumber dari norma kesusilaan. Penyampaian pembelaan hendaknya tetap santun (kesopanan)."
  },

  // =================== NORMA KESOPANAN: 4 DASAR ===================
  {
    id: "k13",
    tingkat: "dasar",
    kasus: "Dimas selalu mencium tangan kedua orang tuanya dan mengucapkan salam sebelum berangkat ke sekolah.",
    jawabanId: "kesopanan",
    petunjuk: [
      "Perilaku ini merupakan adat istiadat dan tata krama yang diajarkan sejak kecil.",
      "Jika diabaikan, masyarakat akan menganggap anak tersebut kurang bertata krama.",
      "Aturan ini bersumber dari kebiasaan pergaulan sehari-hari yang saling menghormati."
    ],
    pertanyaanLanjutan: null,
    alasan: "Mencium tangan orang tua adalah tata krama dan adab pergaulan sehari-hari.",
    penjelasan: "Mencium tangan bersumber dari norma kesopanan dan adat penghormatan kepada orang yang lebih tua."
  },
  {
    id: "k14",
    tingkat: "dasar",
    kasus: "Dewi berbicara dengan nada lembut dan tidak menyela saat gurunya sedang menerangkan materi pelajaran.",
    jawabanId: "kesopanan",
    petunjuk: [
      "Tindakan ini mencerminkan etika bertutur kata di hadapan orang yang lebih tua.",
      "Pelanggaran terhadap adab ini akan dinilai tidak santun oleh lingkungan sekitar.",
      "Pedoman ini berakar dari tata krama pergaulan di lingkungan sekolah."
    ],
    pertanyaanLanjutan: null,
    alasan: "Berbicara santun dan tidak memotong pembicaraan guru adalah wujud tata krama pergaulan.",
    penjelasan: "Etika berbicara kepada guru merupakan cerminan norma kesopanan dan tata krama di sekolah."
  },
  {
    id: "k15",
    tingkat: "dasar",
    kasus: "Bagus mengetuk pintu dan mengucap permisi sebelum memasuki ruang kepala sekolah untuk mengantar surat.",
    jawabanId: "kesopanan",
    petunjuk: [
      "Kebiasaan baik ini menunjukkan rasa hormat saat bertamu ke ruangan orang lain.",
      "Sanksi bila melanggar adalah ditegur atau dianggap tidak memiliki sopan santun.",
      "Aturan ini bersumber dari kepatutan tata krama yang berlaku di masyarakat."
    ],
    pertanyaanLanjutan: null,
    alasan: "Mengetuk pintu dan mengucap salam adalah tata cara pergaulan yang santun.",
    penjelasan: "Mengetuk pintu bersumber dari tata krama dan etika bertamu dalam norma kesopanan."
  },
  {
    id: "k16",
    tingkat: "dasar",
    kasus: "Hani menerima bingkisan dari temannya dengan menggunakan tangan kanan sambil tersenyum dan berterima kasih.",
    jawabanId: "kesopanan",
    petunjuk: [
      "Tata cara memakai anggota tubuh ini menjadi kebiasaan elok dalam budaya kita.",
      "Memberi atau menerima dengan cara sebaliknya dinilai kurang pantas dan kurang elok.",
      "Aturan pergaulan ini bersumber dari adat kepantasan hidup bersama."
    ],
    pertanyaanLanjutan: null,
    alasan: "Menerima barang dengan tangan kanan dan berterima kasih adalah adat kesopanan masyarakat.",
    penjelasan: "Menerima barang dengan tangan kanan berakar pada adat pergaulan dan norma kesopanan."
  },

  // =================== NORMA KESOPANAN: 2 HOTS ===================
  {
    id: "k17",
    tingkat: "hots",
    kasus: "Meskipun sangat lapar, Rian menunggu semua tamu dipersilakan mengambil hidangan terlebih dahulu dalam jamuan.",
    jawabanId: "kesopanan",
    petunjuk: [
      "Tokoh mengendalikan dorongan perut demi menjaga adab dan menghormati para tamu.",
      "Jika ia mendahului, orang lain akan memandangnya tidak tahu tata krama jamuan.",
      "Aturan ini menuntut pengendalian diri demi menjunjung tinggi etiket perjamuan."
    ],
    pertanyaanLanjutan: "Mengapa mendahulukan tamu saat jamuan makan penting bagi kerukunan dan saling menghormati?",
    alasan: "Menunggu giliran dan menghormati tamu adalah etika kepantasan tata krama pergaulan.",
    penjelasan: "Menahan diri demi adab perjamuan berakar pada norma kesopanan. Sikap ini juga melatih kesabaran diri."
  },
  {
    id: "k18",
    tingkat: "hots",
    kasus: "Sari menahan diri untuk tidak memarahi temannya di depan umum, melainkan menasihatinya secara pribadi.",
    jawabanId: "kesopanan",
    petunjuk: [
      "Tokoh memilih cara penyampaian yang menjaga harga diri orang lain di depan publik.",
      "Menegur di depan orang banyak dinilai mempermalukan dan melanggar etika pergaulan.",
      "Pedoman tindakan ini bersumber dari tata krama menjaga kehormatan sesama."
    ],
    pertanyaanLanjutan: "Bagaimana cara menegur kesalahan teman tanpa melanggar kesopanan dan tanpa membuatnya malu?",
    alasan: "Menegur secara empat mata menjaga kehormatan teman sesuai tata krama pergaulan santun.",
    penjelasan: "Menjaga martabat orang lain saat menegur berakar pada norma kesopanan serta empati susila."
  },

  // =================== NORMA HUKUM: 4 DASAR ===================
  {
    id: "k19",
    tingkat: "dasar",
    kasus: "Ayah Doni selalu mengenakan helm standar dan membawa SIM saat mengendarai sepeda motor di jalan raya.",
    jawabanId: "hukum",
    petunjuk: [
      "Kewajiban ini tercantum dalam undang-undang lalu lintas yang sah.",
      "Jika melanggar, pelakunya dapat dikenai tilang atau denda oleh petugas berwenang.",
      "Aturan tertulis ini dibuat oleh pemerintah dan memiliki sanksi yang tegas."
    ],
    pertanyaanLanjutan: null,
    alasan: "Mengenakan helm dan membawa SIM adalah peraturan tertulis resmi lalu lintas negara.",
    penjelasan: "Aturan lalu lintas bersumber dari peraturan perundang-undangan resmi negara (hukum) dengan sanksi tegas."
  },
  {
    id: "k20",
    tingkat: "dasar",
    kasus: "Seorang pedagang membayar pajak retribusi resmi kepada petugas pemerintah daerah sesuai aturan yang berlaku.",
    jawabanId: "hukum",
    petunjuk: [
      "Aturan ini ditetapkan secara resmi oleh lembaga kekuasaan negara.",
      "Pelanggar aturan ini dapat dijatuhi sanksi administratif atau penutupan usaha.",
      "Pedoman ini bersumber dari peraturan perundangan tertulis yang bersifat memaksa."
    ],
    pertanyaanLanjutan: null,
    alasan: "Membayar pajak retribusi merupakan kewajiban resmi berdasarkan hukum negara.",
    penjelasan: "Pajak retribusi bersumber dari hukum resmi negara yang bersifat mengikat dan memaksa warga negara."
  },
  {
    id: "k21",
    tingkat: "dasar",
    kasus: "Pengendara mobil berhenti di belakang garis putih saat lampu lalu lintas menyala merah di persimpangan jalan.",
    jawabanId: "hukum",
    petunjuk: [
      "Rambu dan marka jalan ini adalah ketentuan resmi keselamatan berkendara bersama.",
      "Menerobos lampu ini berakibat sanksi tilang serta bahaya pidana kecelakaan.",
      "Aturan tertulis ini dibuat oleh pihak kepolisian dan dinas perhubungan resmi."
    ],
    pertanyaanLanjutan: null,
    alasan: "Berhenti saat lampu merah adalah peraturan resmi perundang-undangan lalu lintas negara.",
    penjelasan: "Lampu lalu lintas adalah aturan hukum resmi. Mematuhinya menjaga ketertiban umum dan keselamatan bersama."
  },
  {
    id: "k22",
    tingkat: "dasar",
    kasus: "Pencuri sepeda di kompleks perumahan ditangkap polisi untuk menjalani pemeriksaan dan persidangan di pengadilan.",
    jawabanId: "hukum",
    petunjuk: [
      "Perbuatan ini melanggar pasal pidana dalam kitab undang-undang negara.",
      "Pelakunya diancam hukuman penjara yang diputuskan oleh hakim di pengadilan.",
      "Aturan yang ditegakkan ini bersumber dari kekuasaan hukum negara yang mengikat."
    ],
    pertanyaanLanjutan: null,
    alasan: "Mencuri adalah tindak pidana yang diatur dan diberi sanksi tegas oleh undang-undang negara.",
    penjelasan: "Larangan mencuri diatur dalam hukum pidana dengan sanksi penjara. Ini juga melanggar norma agama dan kesusilaan."
  },

  // =================== NORMA HUKUM: 2 HOTS ===================
  {
    id: "k23",
    tingkat: "hots",
    kasus: "Pak RT menolak uang sogokan dari pengembang perumahan yang ingin membangun tanpa izin resmi pemerintah.",
    jawabanId: "hukum",
    petunjuk: [
      "Tokoh menolak suap karena menyadari suap adalah tindak pidana korupsi yang melanggar hukum.",
      "Pembangunan tanpa izin resmi melanggar undang-undang dan dapat disegel oleh petugas.",
      "Ketegasan menolak ini berlandaskan pada kepatuhan terhadap regulasi perizinan negara."
    ],
    pertanyaanLanjutan: "Apa bahaya terbesar bagi masyarakat jika aparat lingkungan membiarkan pelanggaran izin demi keuntungan uang sogokan?",
    alasan: "Menolak suap dan menegakkan izin mendirikan bangunan berlandaskan aturan hukum negara.",
    penjelasan: "Perizinan bangunan dan larangan suap diatur dalam hukum positif negara. Sikap ini juga didukung kejujuran hati nurani."
  },
  {
    id: "k24",
    tingkat: "hots",
    kasus: "Pengemudi ambulans membunyikan sirene dan melaju cepat karena undang-undang memprioritaskannya saat membawa pasien kritis.",
    jawabanId: "hukum",
    petunjuk: [
      "Tindakan menerobos kondisi lalu lintas ini memiliki dasar hak prioritas dalam pasal undang-undang.",
      "Pengendara lain wajib memberi jalan berdasarkan perintah aturan hukum resmi negara.",
      "Pengecualian tata tertib di jalan ini diatur secara tegas dalam perundang-undangan resmi."
    ],
    pertanyaanLanjutan: "Mengapa undang-undang lalu lintas memberikan hak prioritas kepada ambulans dibandingkan kendaraan pribadi lainnya?",
    alasan: "Prioritas jalan bagi ambulans diatur secara tegas dalam undang-undang lalu lintas resmi negara.",
    penjelasan: "Hak prioritas ambulans diatur dalam undang-undang lalu lintas demi menyelamatkan nyawa manusia."
  }
];

/**
 * Validasi Data Saat Load
 * Memastikan skema, keunikan, komposisi 4 dasar + 2 hots per norma,
 * petunjuk berjumlah 3, dan pertanyaanLanjutan pada HOTS.
 */
function validasiDataNorma() {
  const errors = [];
  const validNormaIds = NORMA_LIST.map(n => n.id);

  if (KASUS_POOL.length !== 24) {
    errors.push(`Jumlah kasus bukan 24, tetapi ${KASUS_POOL.length}`);
  }

  const seenIds = new Set();
  const komposisi = {};
  validNormaIds.forEach(id => {
    komposisi[id] = { dasar: 0, hots: 0 };
  });

  KASUS_POOL.forEach((item, index) => {
    const label = `Kasus index ${index} (id: ${item.id})`;

    // ID unik
    if (!item.id || typeof item.id !== "string") {
      errors.push(`${label}: ID harus berupa string`);
    } else if (seenIds.has(item.id)) {
      errors.push(`${label}: ID '${item.id}' terduplikasi`);
    } else {
      seenIds.add(item.id);
    }

    // Validitas jawabanId
    if (!validNormaIds.includes(item.jawabanId)) {
      errors.push(`${label}: jawabanId '${item.jawabanId}' tidak valid. Harus salah satu dari: ${validNormaIds.join(", ")}`);
    }

    // Validitas tingkat
    if (item.tingkat !== "dasar" && item.tingkat !== "hots") {
      errors.push(`${label}: tingkat '${item.tingkat}' tidak valid (harus 'dasar' atau 'hots')`);
    } else if (validNormaIds.includes(item.jawabanId)) {
      komposisi[item.jawabanId][item.tingkat]++;
    }

    // Teks kasus
    if (!item.kasus || typeof item.kasus !== "string" || item.kasus.trim().length === 0) {
      errors.push(`${label}: teks kasus kosong`);
    }

    // Petunjuk harus array berisi tepat 3 string
    if (!Array.isArray(item.petunjuk) || item.petunjuk.length !== 3) {
      errors.push(`${label}: petunjuk harus berupa array dengan tepat 3 elemen`);
    } else {
      item.petunjuk.forEach((p, pIdx) => {
        if (!p || typeof p !== "string" || p.trim().length === 0) {
          errors.push(`${label}: petunjuk ke-${pIdx + 1} kosong`);
        }
      });
    }

    // HOTS wajib ada pertanyaanLanjutan, dasar harus null
    if (item.tingkat === "hots") {
      if (!item.pertanyaanLanjutan || typeof item.pertanyaanLanjutan !== "string" || item.pertanyaanLanjutan.trim().length === 0) {
        errors.push(`${label}: kasus HOTS wajib memiliki pertanyaanLanjutan yang terisi`);
      }
    } else {
      if (item.pertanyaanLanjutan !== null) {
        errors.push(`${label}: kasus dasar harus memiliki pertanyaanLanjutan = null`);
      }
    }

    // Alasan dan penjelasan harus terisi
    if (!item.alasan || item.alasan.trim().length === 0) {
      errors.push(`${label}: alasan wajib diisi`);
    }
    if (!item.penjelasan || item.penjelasan.trim().length === 0) {
      errors.push(`${label}: penjelasan wajib diisi`);
    }
  });

  // Periksa komposisi: 4 dasar + 2 hots per norma
  validNormaIds.forEach(id => {
    const count = komposisi[id];
    if (count.dasar !== 4) {
      errors.push(`Norma '${id}': jumlah kasus dasar = ${count.dasar} (wajib 4)`);
    }
    if (count.hots !== 2) {
      errors.push(`Norma '${id}': jumlah kasus HOTS = ${count.hots} (wajib 2)`);
    }
  });

  if (errors.length > 0) {
    console.warn("[PERINGATAN] Validasi Data Detektif Norma:", errors);
    return { valid: false, errors };
  } else {
    console.log("[SUKSES] Validasi data norma berhasil: 24 kasus valid (16 dasar + 8 HOTS, 4 norma seimbang).");
    return { valid: true, errors: [] };
  }
}

// Jalankan validasi otomatis saat file dimuat
if (typeof window !== "undefined") {
  validasiDataNorma();
}
