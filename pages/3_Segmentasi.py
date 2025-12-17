from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
logo_path = BASE_DIR / "assets" / "dinpert.png"

st.set_page_config(
    page_title="Segmentasi Pelanggan",
    page_icon=str(logo_path),
    layout="wide"
)


# app.py
import streamlit as st
from clustering_segmentasi import kmeans_segmentasi
from visualization_segmentasi import (
    tampilkan_ringkasan,
    tabel_segmentasi,
    profil_cluster,
    top_wilayah
)
from insight_segmentasi import tampilkan_insight

st.set_page_config(
    page_title="Segmentasi Pelanggan",
    layout="wide"
)


st.markdown("""
<style>
    
    
    /* Main Background with Gradient */
    .stApp {
        background: linear-gradient(90deg,rgba(30, 59, 46, 1) 2%, rgba(34, 56, 46, 1) 57%, rgba(29, 133, 112, 1) 100%);
    }
    .stSidebar {
        background: linear-gradient(90deg,rgba(19, 38, 30, 1) 100%, rgba(29, 133, 112, 1) 100%);

    }
            .stAppHeader {
                display: none;
            }
</style>             
""", unsafe_allow_html=True)  


st.title("📊 Dashboard Segmentasi Pelanggan Veteriner")
st.caption(
    "Segmentasi pelanggan berdasarkan wilayah, jenis hewan, dan produk hewan"
)

# PAGE ICON
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # folder Project/
logo_path = os.path.join(BASE_DIR, "assets", "dinpert.png")

# Load data
import pandas as pd
from database_venteriner import engine
from preprocessing_segmentasi import preprocess_segmentasi

query = """
SELECT
    JUMLAH,
    URAIAN,
    JENIS_HPM,
    SATUAN,
    KOTA_ASAL,
    PROV_ASAL
FROM sertifikat_masuk
"""

df_raw = pd.read_sql(query, engine)

mode = st.selectbox(
    "Pilih Mode Segmentasi",
    ["kota", "provinsi", "hewan", "produk"]
)

df_segment = preprocess_segmentasi(df_raw, mode)

df_clustered = kmeans_segmentasi(df_segment, n_clusters=3)

tampilkan_ringkasan(df_clustered)
st.divider()
tabel_segmentasi(df_clustered)
profil_cluster(df_clustered)
top_wilayah(df_clustered)
tampilkan_insight(df_clustered)

