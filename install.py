#!/usr/bin/env python3
"""
Script instalasi untuk dependencies PDF Digital Signature
"""

import subprocess
import sys
import os

def install_package(package):
    """Install package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} berhasil diinstall")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Gagal menginstall {package}")
        return False

def main():
    print("🚀 Memulai instalasi dependencies untuk PDF Digital Signature...")
    print("=" * 60)
    
    # List of required packages
    packages = [
        "streamlit",
        "python-dotenv", 
        "Pillow",
        "web3",
        "eth-account",
        "reportlab",
        "PyPDF2",
        "cryptography",
        "pyHanko>=0.12.0",
        "pyhanko-certvalidator>=0.19.5",
        "asn1crypto>=1.4.0",
        "oscrypto>=1.3.0",
        "certifi",
        "click",
        "pyyaml",
        "tzlocal",
        "uritools",
        "qrcode[pil]",
        "pymupdf",
        "pdfplumber"
    ]
    
    failed_packages = []
    
    for package in packages:
        print(f"📦 Installing {package}...")
        if not install_package(package):
            failed_packages.append(package)
    
    print("=" * 60)
    
    if not failed_packages:
        print("🎉 Semua dependencies berhasil diinstall!")
        print("\n✅ Fitur yang tersedia:")
        print("   - PDF Digital Signature compatible dengan Adobe Reader")
        print("   - Blockchain certificate verification")
        print("   - ECDSA digital signature")
        print("   - Self-signed certificate generation")
        print("   - Automatic PDF signing")
        
        print("\n🚀 Cara menjalankan aplikasi:")
        print("   streamlit run main.py")
        
    else:
        print("⚠️  Beberapa packages gagal diinstall:")
        for package in failed_packages:
            print(f"   - {package}")
        
        print("\n💡 Solusi:")
        print("   1. Pastikan pip sudah update: python -m pip install --upgrade pip")
        print("   2. Install manual: pip install -r requirements.txt")
        print("   3. Gunakan virtual environment jika memungkinkan")

if __name__ == "__main__":
    main()