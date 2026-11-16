# Deteksi Intrusi Jaringan dengan Random Forest (NSL-KDD)

Video: menjelaskan cara kerja model ML untuk keamanan sistem — kasus **Network Intrusion Detection**.

## Isi folder

| File | Fungsi |
|---|---|
| `train.py` | download data → EDA → preprocessing → training → evaluasi → simpan `model.joblib` |
| `predict.py` | inference: prediksi 5 record baru + contoh input manual |
| `data/` | `KDDTrain+.txt`, `KDDTest+.txt` (auto-download saat run pertama) |
| `plots/` | 5 gambar siap tampil di video |
| `metrics.csv` | tabel perbandingan model |

## Cara run

```
pip install -r requirements.txt
python train.py     # ±1 menit, CPU saja
python predict.py
```

## Angka kunci (sebut di video)

- Data: 125.973 record train, 22.544 record test, 41 fitur, 0 missing.
- Distribusi train: Normal 67.343 (53,5%) · DoS 45.927 (36,5%) · Probe 11.656 (9,3%) · R2L 995 (0,8%) · U2R 52 (0,04%).
- `num_outbound_cmds` konstan → dibuang.
- Hasil test: RandomForest accuracy 74,2% / F1-macro 0,515 · DecisionTree 75,0% / 0,513 · LogisticRegression 76,1% / 0,569.
- RandomForest: DoS F1 0,85 · Normal 0,77 · Probe 0,71 · R2L 0,03 · U2R 0,20.
- Insight utama: **accuracy tinggi ≠ model aman**. R2L recall 1,7% → serangan lolos (false negative).

## Storyboard (±13 menit)

**0:00–0:40 — Hook**
Tampilkan: judul + satu baris masalah.
Bicara: "IDS berbasis signature hanya kenal serangan yang sudah pernah tercatat. Model ML bisa mengenali pola baru dari data. Video ini membangun dan menguji satu model tersebut dari nol."

**0:40–1:30 — Kasus & algoritma**
Tampilkan: slide/teks 3 baris (kasus, data, algoritma).
Bicara: klasifikasi trafik per koneksi ke 5 kelas; Random Forest karena tahan fitur campuran + tidak perlu scaling, plus Decision Tree & Logistic Regression sebagai pembanding.

**1:30–3:30 — Data**
Tampilkan: `train.py` bagian `1. DATA` + output terminal (`shape`, `head`, `value_counts`).
Bicara: 41 fitur = statistik per koneksi (durasi, bytes, flag TCP, jumlah koneksi ke host yang sama). Label asli 20+ nama serangan dikelompokkan jadi DoS/Probe/R2L/U2R.

**3:30–5:30 — EDA**
Tampilkan: `plots/01_class_distribution.png`, `02_correlation.png`.
Bicara: imbalance ekstrem (U2R 0,04%) → metric harus per-kelas, bukan accuracy. Korelasi antar fitur rate tinggi → redundan tapi aman untuk tree.

**5:30–7:30 — Preprocessing**
Tampilkan: kode `ColumnTransformer` + `Pipeline`.
Bicara: 3 kolom kategorikal di-OneHot (`service` ±70 nilai), sisanya di-StandardScaler untuk LogisticRegression; semua transformer **fit hanya di train** agar tidak bocor (data leakage).

**7:30–10:00 — Training & evaluasi**
Tampilkan: tabel `metrics.csv`, `plots/04_confusion_matrix.png`, `plots/05_feature_importance.png`.
Bicara: `class_weight="balanced"` memberi bobot lebih besar ke kelas langka; confusion matrix menunjukkan 2.821 dari 2.885 R2L diprediksi Normal dan 1.745 DoS lolos, sementara Normal hanya salah 269 dari 9.711; fitur teratas `src_bytes`, `dst_host_srv_count`, `flag`. Sebut bahwa Logistic Regression justru menang F1-macro — bukti selalu bandingkan baseline.

**10:00–12:00 — Inference**
Tampilkan: `python predict.py` live.
Bicara: 3 record baru terklasifikasi benar; 2 serangan langka diprediksi Normal dengan probabilitas rendah (0,06 dan 0,26) → model tidak yakin, di produksi bisa pakai threshold/alert manual. Contoh input manual = cara "deploy" ke data baru via `joblib`.

**12:00–13:00 — Limitasi & kesimpulan**
Bicara: dataset 1998, ada duplikat, serangan modern berbeda (UNSW-NB15/CICIDS2017); false negative adalah risiko utama; next step = class-weight lebih agresif, SMOTE, atau anomaly detection (Isolation Forest) untuk serangan baru.

## Tips rekaman

- OBS Studio, 1920x1080, 30 fps, audio 48 kHz. Tes mic 10 detik dulu.
- Font editor minimal 16pt, terminal minimal 14pt — teks harus terbaca di HP.
- Jangan rekam sekali jadi: rekam per scene, gabung di editor (CapCut/Kdenlive).
- Kalau perintah terminal lambat, jalankan sekali dulu agar data sudah terunduh saat rekaman.
- Tampilkan gambar plot full-screen 3–4 detik saat menjelaskan, bukan sekadar di-scroll.
- Larangan umum: jangan sekadar baca kode baris per baris. Jelaskan **kenapa**, bukan **apa**.

## Upload

- Judul: `Deteksi Intrusi Jaringan dengan Machine Learning (Random Forest + NSL-KDD)`
- Deskripsi: ringkas kasus, dataset, hasil, link repo, timestamp per bab.
- Tag: `machine learning`, `cybersecurity`, `intrusion detection`, `random forest`, `nsl-kdd`, `python`.
- Thumbnail: confusion matrix + teks "Accuracy 74% tapi R2L cuma 1,7%?" — angka mengejutkan menarik klik.
- Set visibility Unlisted kalau ini tugas kuliah, share link ke dosen.

## Pertanyaan yang mungkin ditanya dosen

- Kenapa bukan accuracy? → imbalance; accuracy 74% tapi model melewatkan hampir semua R2L.
- Kenapa bukan deep learning? → data tabular kecil, RF sudah kuat, training cepat, mudah dijelaskan.
- Kenapa serangan R2L tidak terdeteksi? → pola R2L di test berbeda dari train (serangan baru), fitur yang tersedia kurang menangkap isi payload.
- Bagaimana deploy nyata? → `model.joblib` disimpan, disajikan via FastAPI/Flask, input = fitur koneksi dari log firewall/NetFlow.