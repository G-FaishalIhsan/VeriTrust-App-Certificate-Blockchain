import streamlit as st
import sys
import os

# Tambahkan direktori saat ini ke path
sys.path.append(os.path.dirname(__file__))

# Import halaman
from issue import show_issuance_page, setup_web3_connection as setup_issue
from verify import show_verification_page, setup_web3_connection as setup_verify

def apply_custom_css():
    """Menerapkan CSS kustom untuk mempercantik tampilan"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .main {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        font-weight: 300;
        line-height: 1.6;
        max-width: 800px;
        margin: 0 auto;
        text-align: center;
    }
    
    /* Sidebar Navigation Styling */
    .sidebar-nav {
        margin: 1rem 0;
    }
    
    .sidebar-button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 12px 20px;
        border: none;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);
        text-decoration: none;
        display: block;
        width: 100%;
        margin: 10px 0;
        text-align: left;
    }
    
    .sidebar-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 172, 254, 0.4);
        text-decoration: none;
        color: white;
    }
    
    .sidebar-button.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Fix untuk column layout dan dark theme */
    .stColumn > div {
        background: transparent !important;
    }
    
    /* Pastikan tidak ada code yang tertampil */
    .stMarkdown pre {
        display: none !important;
    }
    
    /* Dark background untuk area content */
    .content-area {
        background: #1e1e1e;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .nav-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .nav-button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 15px 30px;
        border: none;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(79, 172, 254, 0.3);
        text-decoration: none;
        display: inline-block;
        min-width: 200px;
        text-align: center;
    }
    
    .nav-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4);
        text-decoration: none;
        color: white;
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Info Card Styling */
    .info-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 5px 20px rgba(240, 147, 251, 0.3);
    }
    
    .info-card h3 {
        margin-top: 0;
        font-weight: 600;
        font-size: 1.3rem;
    }
    
    .info-card p {
        margin-bottom: 0;
        line-height: 1.6;
        opacity: 0.95;
    }
    
    /* Feature Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #666;
        line-height: 1.5;
        font-size: 0.95rem;
    }
    
    /* Status Messages */
    .success-message {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: #d63384;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .nav-container {
            flex-direction: column;
            align-items: center;
        }
        
        .nav-button {
            width: 100%;
            max-width: 300px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def show_header():
    """Menampilkan header utama aplikasi"""
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🔐 VeriTrust</h1>
        <p class="main-subtitle" style="max-width: 800px; margin: 0 auto;">
            Sistem Verifikasi Sertifikat Seminar Menggunakan Digital Signature 
            Berbasis Blockchain dengan Smart Contract Menggunakan Metode Algoritma ECDSA
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_features():
    """Menampilkan fitur-fitur utama aplikasi"""
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">📜</div>
            <div class="feature-title">Penerbitan Sertifikat</div>
            <div class="feature-desc">
                Terbitkan sertifikat seminar dengan tanda tangan digital yang aman menggunakan algoritma ECDSA
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">✅</div>
            <div class="feature-title">Verifikasi Keaslian</div>
            <div class="feature-desc">
                Verifikasi keaslian sertifikat dengan teknologi blockchain yang tidak dapat dipalsukan
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <div class="feature-title">Keamanan Tinggi</div>
            <div class="feature-desc">
                VMenggunakan smart contract dan enkripsi ECDSA untuk menjamin keamanan dan integritas data
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_navigation():
    """Menampilkan navigasi dengan button di halaman utama"""
    st.markdown("### 🎯 Pilih Layanan")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Button untuk Penerbitan Sertifikat
        if st.button("📝 Penerbitan Sertifikat", key="main_issue_btn", use_container_width=True, help="Terbitkan sertifikat baru"):
            st.session_state.current_page = "issue"
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Button untuk Verifikasi Sertifikat
        if st.button("🔍 Verifikasi Sertifikat", key="main_verify_btn", use_container_width=True, help="Verifikasi keaslian sertifikat"):
            st.session_state.current_page = "verify"
            st.rerun()

def show_info_sidebar():
    """Menampilkan informasi dan navigasi di sidebar"""
    with st.sidebar:
        # Navigasi
        st.markdown("### 🧭 Navigasi")
        
        # Button untuk Penerbitan Sertifikat
        if st.button("📝 Penerbitan Sertifikat", key="sidebar_issue", use_container_width=True):
            st.session_state.current_page = "issue"
            st.rerun()
        
        # Button untuk Verifikasi Sertifikat  
        if st.button("🔍 Verifikasi Sertifikat", key="sidebar_verify", use_container_width=True):
            st.session_state.current_page = "verify"
            st.rerun()
            
        # Button untuk kembali ke beranda
        if st.session_state.current_page is not None:
            if st.button("🏠 Kembali ke Beranda", key="sidebar_home", use_container_width=True):
                st.session_state.current_page = None
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("""
        <div class="info-card">
            <h3>💡 Tentang VeriTrust</h3>
            <p>
                VeriTrust menggunakan teknologi blockchain terdepan untuk memastikan 
                keaslian sertifikat seminar Anda. Dengan algoritma ECDSA dan smart contract, 
                setiap sertifikat memiliki jaminan keamanan dan validitas yang tinggi.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        ### 🚀 Fitur Utama
        - **Digital Signature**: Tanda tangan digital dengan ECDSA
        - **Blockchain Technology**: Penyimpanan terdesentralisasi
        - **Smart Contract**: Otomatisasi verifikasi
        - **Anti-Tamper**: Tidak dapat dipalsukan
        """)
        
        st.markdown("---")
        
        st.markdown("""
        ### 📞 Bantuan
        Jika mengalami masalah, pastikan:
        - Koneksi internet stabil
        - Konfigurasi blockchain benar
        - Data input valid dan lengkap
        """)

def main():
    st.set_page_config(
        page_title="VeriTrust - Sistem Verifikasi Sertifikat Blockchain",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Terapkan CSS kustom
    apply_custom_css()
    
    # Inisialisasi session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = None
    
    # Tampilkan header
    show_header()
    
    # Jika belum ada halaman yang dipilih, tampilkan halaman utama
    if st.session_state.current_page is None:
        show_features()
        show_navigation()
        
        # Tampilkan informasi tambahan
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin: 2rem 0;">
            <h4 style="color: #495057; margin-bottom: 1rem;">🌟 Mengapa Memilih VeriTrust?</h4>
            <p style="color: #6c757d; max-width: 600px; margin: 0 auto; line-height: 1.6;">
                Dengan teknologi blockchain dan algoritma ECDSA, VeriTrust memberikan solusi verifikasi 
                sertifikat yang aman, transparan, dan tidak dapat dimanipulasi. Setiap sertifikat memiliki 
                jejak digital yang unik dan dapat diverifikasi kapan saja.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # Beralih antar halaman berdasarkan pilihan
        if st.session_state.current_page == "issue":
            st.markdown("## 📝 Penerbitan Sertifikat")
            # Setup untuk halaman penerbitan
            w3, contract, account = setup_issue()
            if w3 and contract and account:
                show_issuance_page(w3, contract, account)
            else:
                st.markdown("""
                <div class="error-message">
                    <strong>⚠️ Kesalahan Koneksi</strong><br>
                    Tidak dapat menerbitkan sertifikat karena masalah koneksi. 
                    Silakan periksa konfigurasi blockchain Anda.
                </div>
                """, unsafe_allow_html=True)
                
        elif st.session_state.current_page == "verify":
            st.markdown("## 🔍 Verifikasi Sertifikat")
            # Setup untuk halaman verifikasi
            w3, contract = setup_verify()
            if w3 and contract:
                show_verification_page(w3, contract)
            else:
                st.markdown("""
                <div class="error-message">
                    <strong>⚠️ Kesalahan Koneksi</strong><br>
                    Tidak dapat melakukan verifikasi karena masalah koneksi. 
                    Silakan periksa konfigurasi blockchain Anda.
                </div>
                """, unsafe_allow_html=True)
    
    # Tampilkan sidebar info
    show_info_sidebar()

if __name__ == "__main__":
    main()