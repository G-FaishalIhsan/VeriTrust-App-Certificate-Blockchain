
# 🔐 VeriTrust - Sistem Verifikasi Sertifikat Seminar Berbasis Blockchain

**VeriTrust** adalah aplikasi berbasis web untuk **penerbitan dan verifikasi sertifikat seminar** secara digital menggunakan teknologi **blockchain** dan algoritma **digital signature ECDSA**. Sertifikat yang diterbitkan bersifat **tidak dapat dimanipulasi (immutable)** dan dapat **diverifikasi secara terbuka**, meningkatkan kepercayaan dan keamanan dalam proses sertifikasi.

---

## 🚀 Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 📝 **Penerbitan Sertifikat** | Buat sertifikat PDF dari input pengguna dan simpan ke blockchain dengan tanda tangan digital |
| ✅ **Verifikasi Keaslian** | Verifikasi sertifikat melalui file PDF atau ID unik melalui koneksi langsung ke smart contract |
| 🔒 **Keamanan Kriptografi** | Menggunakan algoritma ECDSA + SHA256 untuk autentikasi dan integritas data |
| ⛓️ **Penyimpanan di Blockchain** | Menggunakan Ethereum smart contract untuk menyimpan hash dan data sertifikat |
| 📄 **PDF Digital Signature** | Mendukung integrasi penandatanganan PDF secara digital dengan library `pyHanko` |
| 📎 **Certificate ID + QR Code (opsional)** | Mendukung integrasi Certificate ID dan QR code dalam PDF untuk verifikasi cepat |

---

## 🛠️ Instalasi

### 1. **Clone repositori ini**
```bash
git clone https://github.com/namamu/veritrust-blockchain-certificate.git
cd veritrust-blockchain-certificate
```

### 2. **Buat file `.env` dengan konfigurasi berikut:**
```
INFURA_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
PRIVATE_KEY=YOUR_PRIVATE_KEY
```

> Gunakan Ethereum testnet seperti Sepolia. Jangan gunakan private key utama untuk keamanan.

### 3. **Instal semua dependensi**
```bash
python install.py
```

Atau manual:
```bash
pip install -r requirements.txt
```

---

## ▶️ Cara Menjalankan Aplikasi

```bash
streamlit run main.py
```

Aplikasi akan terbuka di browser (`http://localhost:8501`) dengan tampilan antarmuka elegan yang responsif.

---

## 🧩 Struktur Proyek

```
📦 veritrust/
├── main.py               # Entry point aplikasi (Streamlit)
├── issue.py              # Halaman penerbitan sertifikat
├── verify.py             # Halaman verifikasi sertifikat
├── deploy.py             # Script untuk compile & deploy smart contract Solidity
├── install.py            # Script otomatis instalasi semua dependensi
├── requirements.txt      # Daftar dependensi
├── contracts/
│   └── CertificateVerifier.sol # Smart contract untuk Ethereum
└── artifacts/
    └── contract_info.json # ABI dan alamat kontrak hasil deploy
```

---

## 🧪 Teknologi & Library yang Digunakan

| Kategori | Teknologi |
|----------|-----------|
| Web Framework | `Streamlit` |
| Blockchain | `Web3.py`, `eth-account`, Smart Contract Solidity |
| Kriptografi | `ECDSA`, `SHA-256`, `cryptography`, `pyHanko` |
| PDF Handling | `reportlab`, `PyPDF2`, `pdfplumber`, `qrcode` |
| Utility | `dotenv`, `uuid`, `base64`, `re`, `json` |

---

## 🧠 Alur Kerja Sistem

1. **Input data peserta** oleh admin melalui UI.
2. **Generate UUID dan SHA-256 hash** dari data sertifikat.
3. **Tandatangani digital** dengan algoritma ECDSA menggunakan akun Ethereum.
4. **Simpan ke blockchain** menggunakan smart contract.
5. **Buat file PDF** dengan metadata + optional QR code.
6. **Verifikasi publik** menggunakan file PDF atau ID melalui blockchain.

---

## 🛡️ Keamanan

- 🔑 Tanda tangan digital menggunakan **ECDSA**
- 🔐 Integritas dijamin oleh **SHA-256**
- ⛓️ Penyimpanan data di **Ethereum smart contract**
- 🧾 PDF dapat diparaf secara digital menggunakan **pyHanko**

---

## 📌 Catatan

- Smart contract dapat dideploy melalui `deploy.py`.
- Untuk menjalankan verifikasi, pastikan koneksi ke Ethereum **aktif** dan `contract_info.json` telah tersedia di folder `artifacts`.
- Kompatibel dengan testnet seperti **Sepolia**.
- Dukungan untuk QR code dan signature PDF bersifat **opsional**, namun mudah ditambahkan.

---

## 📜 Lisensi

MIT License - Gratis digunakan dan dimodifikasi untuk keperluan akademik maupun komersial.
