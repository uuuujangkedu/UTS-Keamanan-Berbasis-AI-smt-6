# NASKAH VIDEO

**Judul:** Deteksi Intrusi Jaringan dengan Machine Learning (Random Forest + NSL-KDD)
**Target durasi:** 13–14 menit · **Resolusi:** 1920x1080, 30 fps · **Font editor/terminal:** 16pt / 14pt

---

## A. Persiapan sebelum rekam (jangan direkam)

```powershell
cd "C:\Users\ujangkedu\vscode\UTS Keamanan AI"
.\.venv\Scripts\Activate.ps1
python train.py
python predict.py
```

Alasan: data sudah terunduh, hasil terverifikasi, run rekaman jadi ±40 detik dan deterministik (`random_state=42`).

Checklist layar:

- [ ] Terminal dibersihkan: `clear`
- [ ] Font terminal diperbesar (Ctrl + scroll)
- [ ] Editor: `train.py` terbuka, minimap mati, font 16pt
- [ ] Folder `plots\` terbuka di explorer
- [ ] Notifikasi Windows: Focus Assist ON
- [ ] Mic dites 10 detik, level −12 dB s/d −6 dB
- [ ] Siapkan 2 slide pembuka & penutup (PowerPoint/Google Slides, latar putih, teks besar)

## B. Aset yang dipakai

| Aset | Kapan tampil |
|---|---|
| Slide 1: judul + kasus + algoritma | Scene 1 |
| Terminal output `train.py` (bagian 1. DATA) | Scene 2 |
| `plots\01_class_distribution.png` | Scene 3 |
| `plots\02_correlation.png` | Scene 3 |
| `plots\03_protocol.png` | Scene 3 (opsional, 3 detik) |
| Kode `prep = ColumnTransformer(...)` + `Pipeline(...)` | Scene 4 |
| Terminal output `train.py` (bagian 2 & 3) | Scene 5, 6 |
| `plots\04_confusion_matrix.png` | Scene 6 |
| `plots\05_feature_importance.png` | Scene 6 |
| `metrics.csv` (dibuka di editor) | Scene 6 |
| Terminal `predict.py` | Scene 7 |
| Slide 2: kesimpulan | Scene 8 |

Cara menampilkan gambar: **buka full-screen**, jangan scroll. Zoom gambar 110–125% agar teks terbaca di HP.

---

## Scene 1 — Pembuka + kerangka (0:00–1:40)

**TAMPILKAN:** Slide 1, isinya persis tiga baris:

```
Kasus      : Deteksi intrusi jaringan (Network Intrusion Detection)
Data       : NSL-KDD — 125.973 koneksi, 41 fitur, 5 kelas
Algoritma  : Random Forest (+ Decision Tree, Logistic Regression sebagai pembanding)
```

**NASKAH:**

> "Halo, saya [nama], NIM [nim]. Video ini menjelaskan cara kerja sebuah model machine learning untuk keamanan sistem.
>
> Kasus yang saya pilih: deteksi intrusi jaringan. Setiap koneksi yang masuk ke server harus diputuskan: ini trafik normal, atau serangan?
>
> Kenapa ini butuh machine learning? Selama ini IDS bekerja dengan signature — daftar pola serangan yang sudah pernah tercatat. Masalahnya: begitu penyerang mengubah satu parameter, signature-nya tidak cocok lagi, dan serangan lolos. Model machine learning tidak menghafal pola, dia belajar **ciri-ciri umum** sebuah serangan dari data. Jadi dia bisa mengenali serangan yang belum pernah dia lihat persis.
>
> Alurnya: data, eksplorasi data, praproses, training, evaluasi, lalu uji ke data baru. Saya pakai dataset NSL-KDD dan algoritma Random Forest. Ayo mulai dari datanya."

**JANGAN tampilkan:** kode. Scene ini murni framing.

---

## Scene 2 — Data (1:40–3:30)

**TAMPILKAN:** Terminal, jalankan `python train.py`. Saat output berhenti di bagian `=== 1. DATA ===`, **pause** dan zoom ke baris `shape: (125973, 43)`.

**AKSI:** Jalankan perintah, tunggu sampai `head` dan `distribusi kelas` muncul, lalu scroll pelan ke bawah sekali (jangan bolak-balik).

**NASKAH:**

> "Ini isi datanya. Ada 125.973 baris latihan dan 22.544 baris uji, dengan 43 kolom.
>
> Satu baris = satu koneksi jaringan. Empat puluh satu kolom pertama adalah ciri koneksi itu: berapa lama koneksinya, berapa byte yang dikirim dan diterima, protokolnya TCP atau UDP, servisnya http atau ftp, status koneksinya berhasil atau gagal, dan berapa kali host yang sama dihubungi dalam dua detik terakhir.
>
> Poin penting: model **tidak membaca isi paket**. Dia hanya melihat statistik koneksi. Ini realistis, karena di jaringan nyata isi paket biasanya terenkripsi, sementara statistik koneksi selalu tersedia dari firewall atau NetFlow.
>
> Kolom `label` adalah jawabannya. Label aslinya lebih dari dua puluh nama serangan, seperti `neptune`, `smurf`, `ipsweep`, `guess_passwd`. Saya kelompokkan jadi empat keluarga ditambah normal, karena nama spesifik terlalu banyak dan jumlahnya timpang."

**TAMPILKAN:** zoom ke blok `distribusi kelas`:

```
Normal 67343 | DoS 45927 | Probe 11656 | R2L 995 | U2R 52
```

**NASKAH:**

> "Hasil pengelompokan: normal 67 ribu, DoS 45 ribu, Probe 11 ribu, R2L 995, dan U2R cuma 52 baris — nol koma nol empat persen dari seluruh data.
>
> Nama kelasnya: DoS itu membanjiri server sampai tidak bisa melayani. Probe itu memindai jaringan mencari celah. R2L itu menembus akun dari jarak jauh. U2R itu naik dari user biasa jadi root.
>
> Angka 52 baris untuk U2R ini akan jadi masalah nanti. Ingat angka itu."

**CATATAN:** sebut `kolom konstan (dibuang): ['num_outbound_cmds']` hanya jika sempat — satu kalimat: "Satu kolom isinya nol semua, tidak informatif, saya buang."

---

## Scene 3 — EDA (3:30–5:30)

**TAMPILKAN:** `plots\01_class_distribution.png` full-screen.

**NASKAH:**

> "Ini eksplorasi data. Grafik pertama distribusi kelas. Normal 53 persen, DoS 36 persen, lalu jurang: Probe 9 persen, R2L nol koma delapan persen, U2R nol koma nol empat persen.
>
> Kenapa ini penting? Karena kalau model menebak 'Normal' untuk semua koneksi, dia sudah dapat akurasi 53 persen tanpa belajar apa pun. Jadi akurasi saja tidak cukup untuk menilai model ini. Saya harus lihat performa per kelas."

**TAMPILKAN:** `plots\02_correlation.png` full-screen, zoom ke area merah gelap di kanan bawah.

**NASKAH:**

> "Grafik kedua korelasi antar fitur. Merah gelap berarti dua fitur hampir selalu bergerak bersamaan, misalnya `serror_rate` dengan `srv_serror_rate` — keduanya mengukur hal yang mirip dari sudut berbeda.
>
> Untuk Random Forest ini aman, karena pohon keputusan memilih satu fitur per percabangan, jadi fitur kembar tidak merusak. Tapi ini akan merepotkan Logistic Regression, karena koefisiennya jadi tidak stabil. Itu salah satu alasan saya memilih Random Forest sebagai model utama, meski nanti kita lihat hasil pembandingnya jujur saja."

**TAMPILKAN (opsional 3 detik):** `plots\03_protocol.png`.

**NASKAH (satu kalimat):**

> "Grafik ketiga: sebagian besar DoS datang lewat UDP, trafik normal lewat TCP. Model nanti akan menemukan sendiri pola ini."

---

## Scene 4 — Praproses (5:30–7:30)

**TAMPILKAN:** Editor, blok `def build(...)` di `train.py`:

```python
prep = ColumnTransformer([
    ("num", StandardScaler(), [c for c in features if c not in CATEGORICAL]),
    ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
])
```

Zoom ke dua baris itu saja. Bukan seluruh file.

**NASKAH:**

> "Sebelum dilatih, data harus dirapikan. Dua masalah. Pertama, tiga kolom berisi teks: `protocol_type`, `service`, `flag`. Random Forest hanya mengerti angka, jadi teks ini diubah jadi kolom 0/1 lewat OneHotEncoder. Servis `http` jadi satu kolom sendiri, `ftp` kolom lain, dan seterusnya.
>
> Kenapa tidak diberi nomor, http sama dengan satu, ftp sama dengan dua? Karena nomor itu menciptakan urutan palsu — model akan menganggap ftp lebih besar dari http, padahal tidak ada artinya. OneHot menghindari itu."

**AKSI:** sorot `StandardScaler`.

**NASKAH:**

> "Masalah kedua: skala. `src_bytes` nilainya bisa jutaan, sementara `serror_rate` hanya nol sampai satu. Untuk Random Forest sebenarnya skala tidak berpengaruh, tapi saya tetap menstandarkan, karena pipeline yang sama juga dipakai untuk Logistic Regression — dan model linear sangat sensitif terhadap skala. Satu pipeline, tiga model, perbandingan yang adil."

**AKSI:** sorot `Pipeline([("prep", prep), ("clf", clf)])`.

**NASKAH:**

> "Keduanya dibungkus dalam Pipeline. Fungsinya: preprocessing dan model jadi satu objek. Waktu training, `fit` menjalankan transformasi **hanya** pada data latih. Waktu prediksi, `predict` menjalankan transformasi yang sama persis pada data baru.
>
> Ini bukan sekadar kerapian. Kalau saya menghitung rata-rata dan standar deviasi dari seluruh data sebelum memisahkan latih dan uji, informasi dari data uji sudah bocor ke data latih. Namanya data leakage — model terlihat pintar saat ujian karena sudah mengintip soal. Pipeline mencegah itu secara struktural."

---

## Scene 5 — Training (7:30–9:00)

**TAMPILKAN:** Terminal, output `=== 2. TRAINING & EVALUASI ===`. Kembali ke jendela terminal, tanpa menjalankan ulang (gunakan rekaman Take 2). Jika perlu run ulang, sudah cepat karena data ter-cache.

**AKSI:** zoom ke baris `--- RandomForest (accuracy=0.7416, f1_macro=0.5147) ---`.

**NASKAH:**

> "Sekarang training. Random Forest membangun 150 pohon keputusan. Setiap pohon dilatih pada sampel baris dan sampel fitur yang berbeda, lalu semua pohon memilih bersama — voting. Kenapa begitu? Satu pohon mudah salah dan mudah dihafal. Seratus lima puluh pohon yang masing-masing melihat sudut berbeda jauh lebih tahan terhadap data baru.
>
> Dua parameter penting. `n_estimators=150` jumlah pohon. `class_weight='balanced'` memberi bobot lebih besar ke kelas langka: satu baris U2R dihitung lebih berat daripada satu baris normal, supaya model tidak mengabaikannya hanya karena jumlahnya sedikit.
>
> `random_state=42` membuat hasilnya selalu sama — penting supaya video ini bisa direproduksi."

**CATATAN:** jangan jelaskan teori Random Forest lebih dari ini. 30 detik cukup.

---

## Scene 6 — Evaluasi (9:00–11:30)

**TAMPILKAN:** Terminal, blok `classification_report` Random Forest, zoom ke kolom `recall` dan `f1-score`.

**NASKAH:**

> "Model diuji pada 22.544 koneksi yang tidak pernah dia lihat saat training. Accuracy 74 persen. Terlihat biasa saja. Tapi mari kita baca per kelas.
>
> DoS: F1 nol koma delapan lima — bagus, karena datanya banyak. Normal nol koma tujuh tujuh. Probe nol koma tujuh satu. Lalu R2L: nol koma nol tiga. Dan U2R nol koma dua.
>
> Angka nol koma nol tiga itu artinya begini: dari 2.885 serangan R2L, model hanya menangkap 50. Sisanya diprediksi normal."

**TAMPILKAN:** `plots\04_confusion_matrix.png` full-screen. Pakai kursor/mouse untuk menunjuk baris R2L.

**NASKAH:**

> "Ini confusion matrix. Baris adalah kenyataan, kolom adalah tebakan. Kotak diagonal adalah tebakan benar. Lihat baris R2L: 2.821 dari 2.885 jatuh ke kolom Normal. Di dunia nyata, itu 2.821 serangan yang tidak memicu satu alarm pun.
>
> Sebaliknya, baris Normal hampir seluruhnya benar: dari 9.711 koneksi normal, hanya 269 salah tebak. Model ini sangat pintar bilang 'aman', dan itulah jebakannya. Dalam keamanan, kesalahan yang paling mahal bukan alarm palsu, tapi serangan yang lolos — false negative. Alarm palsu bikin analis repot; serangan yang lolos bisa berarti data bocor."

**TAMPILKAN:** `metrics.csv` di editor, atau tabel terminal `=== 3. PERBANDINGAN MODEL ===`:

```
RandomForest        accuracy 0.7416  f1_macro 0.5147
DecisionTree        accuracy 0.7496  f1_macro 0.5125
LogisticRegression  accuracy 0.7610  f1_macro 0.5688
```

**NASKAH:**

> "Saya juga melatih dua pembanding pada pipeline yang sama. Hasilnya jujur: Logistic Regression, model paling sederhana, justru menang F1-macro — nol koma lima tujuh dibanding nol koma lima satu. Decision Tree di tengah, dan accuracy-nya bahkan lebih tinggi dari Random Forest.
>
> Tiga kesimpulan dari sini. Satu: model paling rumit tidak otomatis terbaik, selalu uji baseline. Dua: accuracy menyesatkan — Decision Tree accuracy-nya tertinggi, tapi F1-macro-nya terendah. Tiga: Random Forest tetap saya pilih untuk demo karena hasilnya lebih stabil dan fiturnya masih bisa dijelaskan — dan itu penting untuk keamanan, karena keputusan memblokir trafik harus bisa dipertanggungjawabkan."

**TAMPILKAN:** `plots\05_feature_importance.png` full-screen.

**NASKAH:**

> "Kenapa bisa dijelaskan? Random Forest mencatat seberapa sering tiap fitur dipakai untuk memisahkan kelas. `src_bytes` — volume data yang dikirim — paling berpengaruh, lalu `dst_host_srv_count` dan `flag`. Masuk akal: DoS mengirim volume tidak wajar, Probe menghubungi banyak host dalam waktu singkat, dan `flag` menandakan koneksi gagal atau setengah terbuka.
>
> Penjelasan ini bukan hiasan. Kalau fitur teratas justru sesuatu yang tidak masuk akal secara keamanan, itu tanda datasetnya bermasalah atau ada kebocoran. Di sini polanya konsisten dengan teori, jadi saya percaya modelnya belajar hal yang benar — meski masih buta pada R2L."

---

## Scene 7 — Inference / uji data baru (11:30–13:10)

**TAMPILKAN:** Terminal, jalankan:

```powershell
python predict.py
```

**AKSI:** biarkan output muncul utuh, lalu zoom ke lima baris pertama.

**NASKAH:**

> "Terakhir, uji ke data baru — inilah bentuk deploy-nya. Model yang sudah dilatih saya simpan dengan joblib jadi file `model.joblib`, jadi tidak perlu training ulang. Script ini memuat model itu, lalu memprediksi lima koneksi baru, satu dari tiap kelas, yang tidak dipakai saat training.
>
> Hasilnya: Normal benar. DoS benar, keyakinan seratus persen. Probe benar, keyakinan sembilan puluh satu persen. Lalu R2L diprediksi Normal dengan keyakinan delapan puluh sembilan persen, dan U2R juga diprediksi Normal.
>
> Ini bukan kegagalan skrip — ini hasil yang konsisten dengan evaluasi tadi. Tapi perhatikan angka keduanya: probabilitas R2L nol koma nol enam, probabilitas U2R nol koma dua enam. Model sebenarnya ragu. Kalau saya turunkan ambang batasnya — misalnya apa pun dengan probabilitas serangan di atas lima persen dikirim ke analis — kedua koneksi ini akan masuk daftar periksa. Jadi menyimpan probabilitas, bukan hanya label, memberi ruang untuk keputusan manusia."

**AKSI:** tunjuk bagian B output (input manual).

**NASKAH:**

> "Bagian kedua adalah inti deploy-nya. Satu koneksi baru saya tulis sebagai dictionary — protokol tcp, servis http, 232 byte dikirim, 8153 diterima, login berhasil, dan statistik host tujuan. Model menerima satu baris itu dan mengembalikan Normal dengan keyakinan penuh. Di sistem nyata, dictionary ini diisi otomatis dari log firewall atau NetFlow, lalu dilayani lewat API — misalnya FastAPI — sehingga keputusan bisa dibuat dalam milidetik untuk setiap koneksi."

---

## Scene 8 — Penutup (13:10–14:00)

**TAMPILKAN:** Slide 2:

```
Kesimpulan
1. Accuracy 74% menyembunyikan R2L recall 1,7%
2. Imbalance = masalah utama IDS → class weight / SMOTE
3. Dataset 1998 → lanjut: UNSW-NB15, CICIDS2017, anomaly detection
```

**NASKAH:**

> "Kesimpulan. Satu: model ini mencapai akurasi 74 persen, tapi melewatkan hampir semua serangan R2L. Angka tunggal selalu menyembunyikan sesuatu, jadi evaluasi harus per kelas. Dua: ketidakseimbangan kelas adalah masalah inti IDS, dan solusinya bertingkat — class weight seperti yang saya pakai, lalu SMOTE untuk membuat data sintetis kelas langka, lalu penyesuaian ambang batas. Tiga: NSL-KDD dibuat tahun 1998. Serangan hari ini berbeda, jadi langkah lanjutnya adalah dataset yang lebih baru seperti UNSW-NB15 atau CICIDS2017, dan untuk serangan yang benar-benar baru, pendekatan anomaly detection seperti Isolation Forest lebih tepat daripada klasifikasi.
>
> Terima kasih."

---

## C. Troubleshooting saat rekam

| Gejala | Sebab | Solusi |
|---|---|---|
| `cannot be loaded because running scripts is disabled` | ExecutionPolicy | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `python` tidak dikenal | venv belum aktif | pakai `& ".\.venv\Scripts\python.exe" train.py` |
| Output terminal terlalu panjang | `head()` + print EDA | zoom ke baris yang dibahas, potong sisanya saat edit |
| Plot terbuka lambat | baca PNG dari disk | buka semua gambar di image viewer sebelum rekam |
| Suara "echo" | ruangan kosong | rekam di ruang berkarpet, atau selimut di belakang |
| Salah ngomong di tengah | — | ulangi dari awal paragraf itu, potong saat edit |

## D. Editing

- Buang jeda > 1,5 detik. Target akhir 13–14 menit.
- Sisipkan teks angka penting (74%, 1,7%, 52 baris) sebagai overlay saat disebut.
- Tambahkan timestamp di deskripsi YouTube sesuai Scene 1–8.
- Musik latar: opsional, volume 8–12% agar suara tetap dominan.

## E. Angka yang harus konsisten (jangan salah sebut)

| Fakta | Nilai |
|---|---|
| Baris train / test | 125.973 / 22.544 |
| Jumlah fitur | 41 |
| Normal / DoS / Probe / R2L / U2R (train) | 67.343 / 45.927 / 11.656 / 995 / 52 |
| RandomForest accuracy / F1-macro | 0,7416 / 0,5147 |
| DecisionTree accuracy / F1-macro | 0,7496 / 0,5125 |
| LogisticRegression accuracy / F1-macro | 0,7610 / 0,5688 |
| R2L tertangkap | 50 dari 2.885 |
| Normal salah tebak | 269 dari 9.711 |
| Probabilitas R2L / U2R pada demo | 0,06 / 0,26 |