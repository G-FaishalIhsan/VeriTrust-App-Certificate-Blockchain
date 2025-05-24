import os
from dotenv import load_dotenv
import streamlit as st
from web3 import Web3
from eth_account.messages import encode_defunct
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
import base64
import time
import PyPDF2
import hashlib
import re

# Muat variabel lingkungan
load_dotenv()

# Konfigurasi untuk Web3
def setup_web3_connection():
    # URL provider untuk jaringan Ethereum (testnet/mainnet)
    infura_url = os.getenv("INFURA_URL")
    if not infura_url:
        st.error("INFURA_URL tidak ditemukan dalam variabel lingkungan")
        return None, None
    
    w3 = Web3(Web3.HTTPProvider(infura_url))
    
    # Periksa koneksi
    if not w3.is_connected():
        st.error("Gagal terhubung ke jaringan Ethereum. Periksa konfigurasi Infura.")
        return None, None
    
    # Muat informasi kontrak
    try:
        with open("artifacts/contract_info.json", "r") as file:
            contract_info = json.load(file)
        
        contract_address = contract_info["address"]
        contract_abi = contract_info["abi"]
        
        # Buat instance kontrak
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
        return w3, contract
    except FileNotFoundError:
        st.error("File contract_info.json tidak ditemukan. Pastikan smart contract sudah di-deploy.")
        return None, None
    except Exception as e:
        st.error(f"Error saat mengatur koneksi Web3: {str(e)}")
        return None, None

# Fungsi untuk mengekstrak teks dari PDF dengan berbagai metode
def extract_text_from_pdf(pdf_file):
    try:
        # Reset file pointer
        pdf_file.seek(0)
        
        # Metode 1: PyPDF2 standar
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            text += page_text
        
        # Reset file pointer lagi untuk metode alternatif
        pdf_file.seek(0)
        
        # Metode 2: Ekstraksi dengan encoding berbeda jika text kosong atau minimal
        if len(text.strip()) < 50:
            try:
                import pdfplumber
                with pdfplumber.open(pdf_file) as pdf:
                    alternative_text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            alternative_text += page_text
                    if len(alternative_text) > len(text):
                        text = alternative_text
            except ImportError:
                st.warning("pdfplumber tidak tersedia, menggunakan PyPDF2 saja")
        
        return text
    except Exception as e:
        st.error(f"Error saat membaca PDF: {str(e)}")
        return None

# Fungsi untuk mengekstrak ID sertifikat dari teks PDF - UPDATED
def extract_certificate_id_from_text(text):
    try:
        # Pattern untuk mencari Certificate ID dengan berbagai format
        patterns = [
            r"Certificate ID:\s*([a-f0-9\-]{36})",  # Format: Certificate ID: uuid
            r"ID Sertifikat:\s*([a-f0-9\-]{36})",   # Format: ID Sertifikat: uuid
            r"CertificateID:\s*([a-f0-9\-]{36})",   # Format tanpa spasi
            r"Cert\.?\s*ID:?\s*([a-f0-9\-]{36})",   # Format singkat
            r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", # UUID pattern langsung
        ]
        
        # Coba setiap pattern
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Ambil match pertama yang ditemukan
                certificate_id = matches[0]
                st.info(f"Certificate ID ditemukan dengan pattern: {pattern}")
                return certificate_id
        
        # Jika tidak ditemukan dengan pattern, coba cari UUID dalam teks
        # UUID format: 8-4-4-4-12 characters
        uuid_pattern = r"\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b"
        uuid_matches = re.findall(uuid_pattern, text, re.IGNORECASE)
        
        if uuid_matches:
            st.info(f"UUID ditemukan dalam teks: {uuid_matches[0]}")
            return uuid_matches[0]
        
        # Debug: tampilkan sebagian teks untuk troubleshooting
        st.warning("Certificate ID tidak ditemukan. Menampilkan sebagian teks untuk debug:")
        st.text_area("Debug - Teks yang diekstrak (500 karakter pertama):", 
                    value=text[:500], height=100, disabled=True)
        
        return None
    except Exception as e:
        st.error(f"Error saat mengekstrak ID: {str(e)}")
        return None

# Fungsi untuk membuat hash dari data sertifikat
def create_certificate_hash(certificate_id, name, title, date, issuer):
    # Gabungkan semua data sertifikat
    data_string = f"{certificate_id}{name}{title}{date}{issuer}"
    # Buat hash SHA256
    certificate_hash = hashlib.sha256(data_string.encode()).hexdigest()
    return certificate_hash

# Fungsi untuk memeriksa detail sertifikat dari blockchain
def get_certificate_details(contract, certificate_id):
    try:
        # Panggil fungsi dari smart contract
        return contract.functions.verifyCertificate(certificate_id).call()
    except Exception as e:
        st.error(f"Error saat mengambil detail sertifikat: {str(e)}")
        return None

# Fungsi untuk memverifikasi hash dari blockchain
def verify_certificate_hash(contract, certificate_id, expected_hash):
    try:
        # Panggil fungsi untuk mendapatkan hash yang tersimpan
        stored_hash = contract.functions.getCertificateHash(certificate_id).call()
        return stored_hash == expected_hash, stored_hash
    except Exception as e:
        st.error(f"Error saat memverifikasi hash: {str(e)}")
        return False, None

# Fungsi untuk menampilkan UI verifikasi sertifikat
def show_verification_page(w3, contract):
    st.title("Verifikasi Sertifikat")
    st.markdown("""
    Unggah file PDF sertifikat untuk memverifikasi keasliannya secara otomatis.
    Sistem akan mengekstrak ID sertifikat dari PDF dan memverifikasi data di blockchain.
    """)
    
    # Form input - hanya upload file PDF
    uploaded_file = st.file_uploader("Unggah file PDF sertifikat", type=["pdf"])
    
    # Tambahkan opsi manual input sebagai backup
    with st.expander("Atau masukkan Certificate ID secara manual (opsional)"):
        manual_cert_id = st.text_input("Certificate ID", placeholder="Masukkan Certificate ID jika ekstraksi PDF gagal")
    
    if st.button("Verifikasi Sertifikat"):
        certificate_id = None
        
        # Coba ekstraksi dari PDF terlebih dahulu
        if uploaded_file:
            with st.spinner("Memproses file PDF..."):
                # Ekstrak teks dari PDF
                pdf_text = extract_text_from_pdf(uploaded_file)
                
                if pdf_text:
                    # Ekstrak ID sertifikat dari teks
                    certificate_id = extract_certificate_id_from_text(pdf_text)
                    
                    if certificate_id:
                        st.success(f"✅ ID Sertifikat berhasil diekstrak dari PDF: {certificate_id}")
                    else:
                        st.warning("⚠️ ID sertifikat tidak dapat diekstrak dari PDF")
                else:
                    st.error("❌ Gagal mengekstrak teks dari PDF")
        
        # Gunakan manual input sebagai fallback
        if not certificate_id and manual_cert_id:
            certificate_id = manual_cert_id.strip()
            st.info(f"Menggunakan Certificate ID manual: {certificate_id}")
        
        # Jika masih tidak ada certificate_id
        if not certificate_id:
            st.error("Tidak dapat menemukan Certificate ID. Pastikan PDF valid atau masukkan ID secara manual.")
            return
        
        with st.spinner("Memverifikasi sertifikat di blockchain..."):
            # Ambil detail sertifikat dari blockchain
            certificate_details = get_certificate_details(contract, certificate_id)
            
            if not certificate_details:
                st.error("Sertifikat tidak ditemukan di blockchain atau terjadi kesalahan saat memverifikasi")
                return
            
            # Ekstrak data dari hasil query
            (
                participant_name, 
                participant_email, 
                seminar_title, 
                seminar_date, 
                signature, 
                issuer, 
                timestamp, 
                is_valid
            ) = certificate_details
            
            # Buat hash dari data yang ditemukan
            expected_hash = create_certificate_hash(
                certificate_id, participant_name, seminar_title, seminar_date, issuer
            )
            
            # Verifikasi hash di blockchain
            hash_valid, stored_hash = verify_certificate_hash(contract, certificate_id, expected_hash)
            
            # Tampilkan hasil
            st.subheader("Hasil Verifikasi")
            
            # Buat tampilan yang menarik
            col1, col2 = st.columns(2)
            
            with col1:
                # Tampilkan status validasi
                if is_valid and hash_valid:
                    st.success("✅ Sertifikat Valid dan Terpverifikasi!")
                elif is_valid and not hash_valid:
                    st.warning("⚠️ Sertifikat ditemukan di blockchain tetapi hash tidak cocok!")
                else:
                    st.error("❌ Sertifikat Tidak Valid atau Telah Dibatalkan!")
                
                # Tampilkan data sertifikat
                st.subheader("Data Sertifikat:")
                st.write(f"**ID Sertifikat:** {certificate_id}")
                st.write(f"**Nama Peserta:** {participant_name}")
                st.write(f"**Email Peserta:** {participant_email}")
                st.write(f"**Judul Seminar:** {seminar_title}")
                st.write(f"**Tanggal Seminar:** {seminar_date}")
                st.write(f"**Penerbit:** {issuer}")
                
                # Verifikasi hash
                if hash_valid:
                    st.success("✅ Hash Sertifikat Valid!")
                else:
                    st.error("❌ Hash Sertifikat Tidak Valid!")
                
                st.write(f"**Hash yang Diharapkan:** {expected_hash}")
                st.write(f"**Hash Tersimpan:** {stored_hash}")
                
                # Verifikasi signature tambahan dengan ECDSA
                try:
                    is_signature_valid = contract.functions.validateSignature(
                        certificate_id, 
                        participant_name, 
                        seminar_title, 
                        signature, 
                        issuer
                    ).call()
                    
                    if is_signature_valid:
                        st.success("✅ Digital Signature Valid!")
                    else:
                        st.error("❌ Digital Signature Tidak Valid!")
                except Exception as e:
                    st.error(f"Error saat memverifikasi tanda tangan: {str(e)}")
            
            with col2:
                # Tampilkan informasi blockchain
                st.subheader("Informasi Blockchain:")
                st.write(f"**Waktu Penerbitan:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))}")
                
                # Tampilkan sebagian teks PDF yang diekstrak jika ada
                if uploaded_file and 'pdf_text' in locals():
                    st.subheader("Isi PDF Sertifikat:")
                    # Batasi tampilan teks untuk readability
                    display_text = pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text
                    st.text_area("Teks yang diekstrak:", value=display_text, height=200, disabled=True)
                
                # Status ringkasan
                st.subheader("Ringkasan Verifikasi:")
                verification_status = []
                verification_status.append(f"✅ Sertifikat ditemukan di blockchain" if certificate_details else "❌ Sertifikat tidak ditemukan")
                verification_status.append(f"✅ Status sertifikat valid" if is_valid else "❌ Status sertifikat tidak valid")
                verification_status.append(f"✅ Hash cocok" if hash_valid else "❌ Hash tidak cocok")
                
                for status in verification_status:
                    st.write(status)

# Main function untuk halaman verifikasi
def verification_main():
    st.set_page_config(page_title="Verifikasi Sertifikat Blockchain", page_icon="🔐", layout="wide")
    
    st.sidebar.title("Tentang")
    st.sidebar.info(
        "Aplikasi ini menggunakan teknologi blockchain dan digital signature "
        "untuk memverifikasi keaslian sertifikat seminar. Cukup unggah file PDF "
        "sertifikat untuk verifikasi otomatis."
    )
    
    st.sidebar.title("Cara Menggunakan")
    st.sidebar.markdown("""
    1. Klik 'Browse files' dan pilih file PDF sertifikat
    2. Klik tombol 'Verifikasi Sertifikat'
    3. Sistem akan otomatis:
       - Mengekstrak ID dari PDF
       - Memeriksa data di blockchain
       - Memverifikasi hash dan signature
       - Menampilkan hasil verifikasi
    4. Jika ekstraksi gagal, masukkan Certificate ID secara manual
    """)
    
    # Setup koneksi Web3
    w3, contract = setup_web3_connection()
    
    if w3 and contract:
        show_verification_page(w3, contract)
    else:
        st.error("Tidak dapat melanjutkan verifikasi karena masalah koneksi. Silakan periksa konfigurasi.")

if __name__ == "__main__":
    verification_main()