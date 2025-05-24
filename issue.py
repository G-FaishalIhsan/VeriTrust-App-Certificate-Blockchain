import os
from dotenv import load_dotenv
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from web3 import Web3
from eth_account.messages import encode_defunct
import json
import uuid
import time
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import navy, gold, black
import hashlib
from reportlab.lib.colors import lightgrey

# Muat variabel lingkungan
load_dotenv()

# Konfigurasi untuk Web3
def setup_web3_connection():
    # URL provider untuk jaringan Ethereum (testnet/mainnet)
    infura_url = os.getenv("INFURA_URL")
    private_key = os.getenv("PRIVATE_KEY")
    
    if not infura_url or not private_key:
        st.error("INFURA_URL atau PRIVATE_KEY tidak ditemukan dalam variabel lingkungan")
        return None, None, None
    
    w3 = Web3(Web3.HTTPProvider(infura_url))
    
    # Periksa koneksi
    if not w3.is_connected():
        st.error("Gagal terhubung ke jaringan Ethereum. Periksa konfigurasi Infura.")
        return None, None, None
    
    # Buat akun dari private key
    account = w3.eth.account.from_key(private_key)
    
    # Muat informasi kontrak
    try:
        with open("artifacts/contract_info.json", "r") as file:
            contract_info = json.load(file)
        
        contract_address = contract_info["address"]
        contract_abi = contract_info["abi"]
        
        # Buat instance kontrak
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
        return w3, contract, account
    except FileNotFoundError:
        st.error("File contract_info.json tidak ditemukan. Pastikan smart contract sudah di-deploy.")
        return None, None, None
    except Exception as e:
        st.error(f"Error saat mengatur koneksi Web3: {str(e)}")
        return None, None, None

# Fungsi untuk membuat PDF sertifikat - FIXED VERSION
# Fungsi untuk membuat PDF sertifikat - UPDATED VISUAL DESIGN
# Fungsi untuk membuat PDF sertifikat - UPDATED VISUAL DESIGN
def create_certificate_pdf(name, title, date, certificate_id, issuer):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Set white background
    c.setFillColor('white')
    c.rect(0, 0, width, height, fill=1)
    
    # Add outer decorative border (gold)
    c.setStrokeColor(gold)
    c.setLineWidth(8)
    c.rect(25, 25, width-50, height-50, fill=0)
    
    # Add inner border (thinner gold)
    c.setStrokeColor(gold)
    c.setLineWidth(2)
    c.rect(45, 45, width-90, height-90, fill=0)
    
    # Add logo/emblem placeholder at top center
    # Circle for logo
    center_x = width / 2
    logo_y = height - 120
    c.setStrokeColor(gold)
    c.setLineWidth(3)
    c.circle(center_x, logo_y, 25, fill=0)
    
    # Inner circle
    c.setLineWidth(1)
    c.circle(center_x, logo_y, 15, fill=0)
    
    # Add small decorative elements in logo
    c.setFillColor(gold)
    c.circle(center_x, logo_y, 8, fill=1)
    
    # Title "CERTIFICATE" - large and bold
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 42)
    title_text = "CERTIFICATE"
    text_width = c.stringWidth(title_text, "Helvetica-Bold", 42)
    c.drawString((width - text_width) / 2, height-200, title_text)
    
    # Subtitle
    c.setFont("Helvetica", 14)
    c.setFillColor(black)
    subtitle_text = "OF PARTICIPATION"
    text_width = c.stringWidth(subtitle_text, "Helvetica", 14)
    c.drawString((width - text_width) / 2, height-230, subtitle_text)
    
    # Decorative line under subtitle
    line_width = 200
    line_start_x = (width - line_width) / 2
    c.setStrokeColor(gold)
    c.setLineWidth(1)
    c.line(line_start_x, height-245, line_start_x + line_width, height-245)
    
    # Participant name with underline
    c.setFont("Times-Italic", 32)
    c.setFillColor(black)
    name_y = height - 320
    text_width = c.stringWidth(name, "Times-Italic", 32)
    name_x = (width - text_width) / 2
    c.drawString(name_x, name_y, name)
    
    # Underline for name
    underline_margin = 50
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.line(name_x - underline_margin, name_y - 10, name_x + text_width + underline_margin, name_y - 10)
    
    # Description text
    c.setFont("Helvetica", 12)
    c.setFillColor(black)
    
    # Multi-line description
    desc_lines = [
        f"Telah Mengikuti Dan Menyelesaikan Seminar Dengan Judul",
        f'"{title}"',
        f"Yang Diselenggarakan Pada Tanggal {date}",
        f"Dan Telah Memenuhi Semua Persyaratan Yang Ditetapkan"
    ]
    
    desc_start_y = height - 380
    line_height = 20
    
    for i, line in enumerate(desc_lines):
        if i == 1:  # Seminar title - make it bold and slightly larger
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(navy)
        else:
            c.setFont("Helvetica", 12)
            c.setFillColor(black)
        
        text_width = c.stringWidth(line, c._fontname, c._fontsize)
        c.drawString((width - text_width) / 2, desc_start_y - (i * line_height), line)
    
    # Certificate ID (nearly invisible but still extractable)
    c.setFont("Helvetica", 1)  # Very small font size
    c.setFillColor('lightgrey')  # Very light gray - almost invisible
    id_text = f"Certificate ID: {certificate_id}"
    text_width = c.stringWidth(id_text, "Helvetica", 1)
    c.drawString((width - text_width) / 2, 15, id_text)  # Position at very bottom
    
    # Signature section - bottom left
    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    
    # Left signature area
    left_sig_x = 80
    sig_y = 180
    
    c.drawString(left_sig_x, sig_y, "PANITIA SEMINAR")
    c.drawString(left_sig_x, sig_y - 40, issuer)
    
    # Signature line for issuer
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.line(left_sig_x, sig_y - 20, left_sig_x + 120, sig_y - 20)
    
    # Right signature area
    right_sig_x = width - 200
    
    c.drawString(right_sig_x, sig_y, "SIGNATURE")
    c.drawString(right_sig_x, sig_y - 40, "BY VERITRUST")
    
    # Signature line for authorized signatory
    c.line(right_sig_x, sig_y - 20, right_sig_x + 120, sig_y - 20)
    
    # Add some decorative corner elements
    corner_size = 20
    
    # Top left corner
    c.setStrokeColor(gold)
    c.setLineWidth(2)
    c.line(60, height-60, 60+corner_size, height-60)
    c.line(60, height-60, 60, height-60-corner_size)
    
    # Top right corner
    c.line(width-60, height-60, width-60-corner_size, height-60)
    c.line(width-60, height-60, width-60, height-60-corner_size)
    
    # Bottom left corner
    c.line(60, 60, 60+corner_size, 60)
    c.line(60, 60, 60, 60+corner_size)
    
    # Bottom right corner
    c.line(width-60, 60, width-60-corner_size, 60)
    c.line(width-60, 60, width-60, 60+corner_size)
    
    c.save()
    buffer.seek(0)
    return buffer

# Fungsi untuk membuat hash dari data sertifikat
def create_certificate_hash(certificate_id, name, title, date, issuer):
    # Gabungkan semua data sertifikat
    data_string = f"{certificate_id}{name}{title}{date}{issuer}"
    # Buat hash SHA256
    certificate_hash = hashlib.sha256(data_string.encode()).hexdigest()
    return certificate_hash

# Fungsi untuk menyimpan hash ke blockchain
def store_hash_to_blockchain(w3, contract, account, certificate_id, certificate_hash):
    try:
        # Siapkan transaksi untuk menyimpan hash
        tx = contract.functions.storeCertificateHash(
            certificate_id, certificate_hash
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Tanda tangani transaksi
        signed_tx = w3.eth.account.sign_transaction(tx, account.key)
        
        # Kirim transaksi
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Tunggu konfirmasi
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return receipt.transactionHash.hex()
    except Exception as e:
        st.error(f"Error menyimpan hash ke blockchain: {str(e)}")
        return None

# Fungsi untuk membuat digital signature dengan ECDSA
def sign_certificate_data(w3, account, certificate_id, name, title):
    # Buat message hash dengan format yang sama seperti di smart contract
    message = Web3.solidity_keccak(['string', 'string', 'string'], 
                                    [certificate_id, name, title])
    
    # Buat signed message menggunakan private key
    signed_message = w3.eth.account.sign_message(
        encode_defunct(message),
        private_key=account.key
    )
    
    return signed_message.signature

# Fungsi untuk menerbitkan sertifikat ke blockchain
def issue_certificate_to_blockchain(w3, contract, account, certificate_id, name, email, title, date, signature, issuer):
    try:
        # Siapkan transaksi
        tx = contract.functions.issueCertificate(
            certificate_id, name, email, title, date, signature, issuer
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Tanda tangani transaksi
        signed_tx = w3.eth.account.sign_transaction(tx, account.key)
        
        # Kirim transaksi
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Tunggu konfirmasi
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return receipt.transactionHash.hex()
    except Exception as e:
        st.error(f"Error menerbitkan sertifikat: {str(e)}")
        return None

# Fungsi untuk mengkonversi PDF ke base64 (untuk download sertifikat)
def get_pdf_as_base64(pdf_buffer):
    pdf_buffer.seek(0)
    pdf_bytes = pdf_buffer.read()
    pdf_str = base64.b64encode(pdf_bytes).decode()
    return pdf_str

# Fungsi untuk menampilkan UI penerbitan sertifikat
def show_issuance_page(w3, contract, account):
    st.title("Penerbitan Sertifikat Seminar")
    st.markdown("""
    Gunakan halaman ini untuk menerbitkan sertifikat digital untuk peserta seminar.
    Sertifikat akan ditandatangani secara digital dan disimpan di blockchain untuk verifikasi.
    """)
    
    # Buat form input menggunakan kolom
    col1, col2 = st.columns(2)
    
    with col1:
        participant_name = st.text_input("Nama Peserta")
        participant_email = st.text_input("Email Peserta")
        issuer_name = st.text_input("Nama Penerbit", placeholder="Contoh: PT. Seminar Indonesia")
    
    with col2:
        seminar_title = st.text_input("Judul Seminar")
        seminar_date = st.date_input("Tanggal Seminar")
    
    # Button untuk menerbitkan sertifikat
    if st.button("Terbitkan Sertifikat"):
        if participant_name and participant_email and seminar_title and issuer_name:
            with st.spinner("Memproses sertifikat..."):
                # Membuat ID unik untuk sertifikat
                certificate_id = str(uuid.uuid4())
                
                # Format tanggal
                formatted_date = seminar_date.strftime("%d %B %Y")
                
                # Buat hash sertifikat
                certificate_hash = create_certificate_hash(
                    certificate_id, participant_name, seminar_title, formatted_date, issuer_name
                )
                
                # Buat PDF sertifikat
                cert_pdf = create_certificate_pdf(
                    participant_name, seminar_title, formatted_date, certificate_id, issuer_name
                )
                
                # Buat digital signature menggunakan ECDSA
                signature = sign_certificate_data(
                    w3, account, certificate_id, participant_name, seminar_title
                )
                
                # Terbitkan ke blockchain
                tx_hash = issue_certificate_to_blockchain(
                    w3, contract, account, certificate_id, 
                    participant_name, participant_email, 
                    seminar_title, formatted_date, signature, issuer_name
                )
                
                # Simpan hash ke blockchain
                hash_tx_hash = store_hash_to_blockchain(
                    w3, contract, account, certificate_id, certificate_hash
                )
                
                if tx_hash and hash_tx_hash:
                    st.success(f"✅ Sertifikat berhasil diterbitkan!")
                    
                    # Info sertifikat
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**ID Sertifikat:** {certificate_id}")
                        st.info(f"**Hash Sertifikat:** {certificate_hash}")
                        st.info(f"**Transaction Hash:** {tx_hash}")
                        st.info(f"**Hash Transaction Hash:** {hash_tx_hash}")
                    
                    with col2:
                        # Download link untuk sertifikat PDF
                        pdf_base64 = get_pdf_as_base64(cert_pdf)
                        href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="certificate_{participant_name.replace(" ", "_")}.pdf">📄 Klik disini untuk mengunduh sertifikat PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    
                    # Simpan informasi sertifikat di session state
                    if 'issued_certificates' not in st.session_state:
                        st.session_state.issued_certificates = []
                    
                    st.session_state.issued_certificates.append({
                        'id': certificate_id,
                        'name': participant_name,
                        'email': participant_email,
                        'title': seminar_title,
                        'date': formatted_date,
                        'issuer': issuer_name,
                        'hash': certificate_hash,
                        'tx_hash': tx_hash,
                        'hash_tx_hash': hash_tx_hash
                    })
                    
                    # Tampilkan preview PDF
                    st.subheader("Preview Sertifikat:")
                    st.write("Sertifikat telah dibuat dalam format PDF. Klik link download di atas untuk mengunduh.")
                    
                else:
                    st.error("❌ Gagal menerbitkan sertifikat di blockchain")
        else:
            st.error("Mohon lengkapi semua informasi yang diperlukan")
    
    # Tampilkan daftar sertifikat yang telah diterbitkan sebelumnya
    if 'issued_certificates' in st.session_state and st.session_state.issued_certificates:
        st.subheader("Sertifikat yang Telah Diterbitkan:")
        for i, cert in enumerate(st.session_state.issued_certificates):
            with st.expander(f"{i+1}. {cert['name']} - {cert['title']}"):
                st.write(f"**ID:** {cert['id']}")
                st.write(f"**Email:** {cert['email']}")
                st.write(f"**Penerbit:** {cert['issuer']}")
                st.write(f"**Tanggal Seminar:** {cert['date']}")
                st.write(f"**Hash:** {cert['hash']}")
                st.write(f"**TX Hash:** {cert['tx_hash']}")
                st.write(f"**Hash TX Hash:** {cert['hash_tx_hash']}")

# Main function untuk halaman penerbitan
def issuance_main():
    st.set_page_config(page_title="Penerbitan Sertifikat Blockchain", page_icon="📜", layout="wide")
    
    st.sidebar.title("Tentang")
    st.sidebar.info(
        "Aplikasi ini menggunakan teknologi blockchain dan digital signature "
        "untuk menerbitkan dan memverifikasi keaslian sertifikat seminar."
    )
    
    # Setup koneksi Web3
    w3, contract, account = setup_web3_connection()
    
    if w3 and contract and account:
        show_issuance_page(w3, contract, account)
    else:
        st.error("Tidak dapat menerbitkan sertifikat karena masalah koneksi. Silakan periksa konfigurasi.")

if __name__ == "__main__":
    issuance_main()                                 