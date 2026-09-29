# 🌾 AGROTEK AI
### Spatial Agriculture Intelligence Platform — Kabupaten Jember

Platform informasi spasial dan sistem pendukung keputusan (Spatial Decision Support System) untuk pertanian, irigasi, hidrologi, dan pengelolaan sumber daya lahan.

---

## 📊 Status: 16/16 Fase Selesai ✅

| Fase | Modul | Status |
|------|-------|--------|
| 1-3 | Foundation, Homepage, Dashboard | ✅ |
| 4 | Peta GIS Leaflet (31 marker) | ✅ |
| 5 | Database SQLite + Login 3 Role | ✅ |
| 6 | Data Center | ✅ |
| 7 | Pertanian | ✅ |
| 8 | Smart Irrigation (Neraca Air) | ✅ |
| 9 | Hidrologi | ✅ |
| 10 | Early Warning | ✅ |
| 11 | Kesesuaian Lahan | ✅ |
| 12 | AGROTEK AI | ✅ |
| 13 | IoT Ready | ✅ |
| 14 | Reports (CSV) | ✅ |
| 15 | Admin Panel | ✅ |
| 16 | Polish & Docs | ✅ |

---

## 🚀 Cara Menjalankan

```bash
# 1. Buka folder project
cd D:\agrotek_bersih

# 2. Aktifkan venv (Windows)
venv\Scripts\activate

# 3. Install dependency (kalau belum)
pip install -r requirements.txt

# 4. Jalankan
python app.py
```

## Asisten tanya-jawab pertanian

Halaman **AGROTEK AI** menyediakan chat konsultasi pertanian menggunakan Gemini API. Buat API key melalui Google AI Studio, lalu simpan sebagai environment variable di server—jangan menaruhnya di kode JavaScript atau membagikannya.

Untuk menjalankan lokal di PowerShell:

```powershell
$env:GEMINI_API_KEY = "API_KEY_ANDA"
python app.py
```

Di Railway, tambahkan `GEMINI_API_KEY` pada **Project → Service → Variables**, lalu deploy/restart aplikasi. Opsional, atur `GEMINI_MODEL` untuk memilih model; nilai default adalah `gemini-3.5-flash-lite`.

Ketersediaan dan batas pemakaian gratis ditentukan oleh Google dan dapat berubah. Chat mengirim pertanyaan serta konteks percakapan singkat ke Gemini; jangan masukkan data pribadi atau rahasia. Jawaban AI adalah informasi awal, bukan diagnosis pasti—konfirmasikan saran berisiko dengan penyuluh pertanian dan ikuti label resmi produk.

## Layer aset irigasi SHP-Epaksi

Layer bangunan irigasi, jaringan saluran, dan petak SHP-Epaksi disimpan di luar folder publik `static/` dan tidak disertakan dalam repository publik. Secara lokal, letakkan GeoJSON di `private_data/irigasi_epaksi/`; di Railway, pasang penyimpanan privat (misalnya volume `/data`) dan atur `EPAKSI_DATA_DIR=/data/irigasi_epaksi`, lalu salin tiga GeoJSON ke folder itu. Peta GIS, endpoint layer, dan unduhan paket hanya tersedia untuk role `admin`, dengan respons tanpa cache. Jika file tidak ada, kontrol layer dan unduhan tidak ditampilkan.

Sebelum deploy Railway, isi variabel `SECRET_KEY` dengan nilai acak minimal 32 karakter. Pada database baru, isi `ADMIN_INITIAL_PASSWORD` dengan password minimal 12 karakter; variabel itu juga dipakai sekali untuk mengganti password admin bawaan `admin123` jika masih aktif. Aplikasi produksi menolak startup jika secret tidak aman atau admin awal masih memakai password bawaan. Jangan menyimpan data SHP atau nilai rahasia di repository publik. Arsip sumber tidak disimpan di repository; tahun data tidak tercantum, sehingga layer ini bukan pemantauan real-time.