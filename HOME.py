import streamlit as st
from PIL import Image
import os

# -------------------------------------
# LOAD ICON (SEBELUM ST LAIN DIPANGGIL)
# -------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(BASE_DIR, "assets", "dinpert.png")

if os.path.exists(icon_path):
    page_icon = Image.open(icon_path)
else:
    page_icon = "🐄"  # fallback emoji

# -------------------------------------
# PAGE CONFIG (HARUS PALING ATAS)
# -------------------------------------
st.set_page_config(
    page_title="Dashboard NKV Kab. Sidoarjo",
    page_icon=page_icon,
    layout="wide"
)

# -------------------------------------
# CUSTOM CSS
# -------------------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(90deg,rgba(30, 59, 46, 1) 2%, rgba(34, 56, 46, 1) 57%, rgba(29, 133, 112, 1) 100%);
}
</style>
""", unsafe_allow_html=True)


# -------------------------------------
# PAGE CONFIG
# -------------------------------------
st.set_page_config(
    page_title="Dashboard NKV Kab. Sidoarjo",
    layout="wide"
)

# -------------------------------------
# CUSTOM CSS
# -------------------------------------
st.markdown("""
<style>
/* Background gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(90deg,rgba(30, 59, 46, 1) 2%, rgba(34, 56, 46, 1) 57%, rgba(29, 133, 112, 1) 100%);
}
            
/* Sidebar Background */
[data-testid="stSidebar"] {
    background: linear-gradient(90deg,rgba(19, 38, 30, 1) 100%, rgba(29, 133, 112, 1) 100%);
}


/* Remove padding */
.block-container {
    padding-top: 3rem;
}

/* Title styling */
.big-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    color: white;
    margin-bottom: 10px;
}

/* Subtitle */
.sub-text {
    font-size: 17px;
    text-align: center;
    color: #e8e8e8;
    margin-top: -10px;
}

/* Card style */
.home-card {
    background: rgba(255, 255, 255, 0.05);
    padding: 25px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(6px);
    width: 70%;
    margin-left: auto;
    margin-right: auto;
}

.logo-img {
    display: block;
    margin-left: auto;
    margin-right: auto;
    width: 170px;
}
</style>

""", unsafe_allow_html=True)

# -------------------------------------
# CONTENT
# -------------------------------------

# Logo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "assets", "dinpert.png")

if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.image(logo, use_container_width=False, width=170)
else:
    st.write("Logo tidak ditemukan.")

# Title
st.markdown('<div class="big-title">Dashboard Nomor Kontrol Veteriner (NKV)<br>Kabupaten Sidoarjo</div>', unsafe_allow_html=True)

# Description Box
st.markdown("""
<div class="home-card">
    <p style="font-size:16px; color:white; text-align:center;">
        Sistem Dashboard NKV Kabupaten Sidoarjo disusun untuk mempermudah pemantauan sertifikat veteriner, 
        pengelolaan data, serta penyajian informasi statistik secara terstruktur dan terintegrasi.
    </p>
</div>
""", unsafe_allow_html=True)
