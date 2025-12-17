# pages/2_Eksplorasi_Data.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

import os
import streamlit as st

# PAGE ICON
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # folder Project/
logo_path = os.path.join(BASE_DIR, "assets", "dinpert.png")

st.set_page_config(
    page_title="Dashboard NKV Kab Sidoarjo",
    page_icon=logo_path,
    layout="wide"
)


# ===============================
# Page Config
# ===============================
st.set_page_config(
    page_title="Eksplorasi Data Veteriner",
    layout="wide"
)

st.title("Eksplorasi Data Veteriner")
st.write("Visualisasi interaktif data distribusi komoditas dan hewan masuk.")

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

from sqlalchemy import create_engine

# ===============================
# Koneksi Database
# ===============================
engine = create_engine("mysql+pymysql://root:72741516@localhost:3306/db_venteriner")


# ===============================
# Load Data dengan Cache
# ===============================
@st.cache_data
def load_data():
    query = "SELECT * FROM sertifikat_masuk"
    df = pd.read_sql_query(query, engine)
    return df

df = load_data()

import streamlit as st
import pandas as pd
import plotly.express as px

# ===============================
# Data Source (ASUMSI df SUDAH ADA)
# ===============================

df = df.rename(columns=str.upper)   # 🌟 IMPROVED: konsisten uppercase seluruh kolom

# ===============================
# PRE-PROCESSING BULAN (PERBAIKAN)
# ===============================

# Urutan nama bulan
bulan_order = [
    "JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI",
    "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"
]

# Pastikan bulan berupa angka
df["BULAN"] = pd.to_numeric(df["BULAN"], errors="coerce").astype("Int64")

# Buat nama bulan dari angka
df["NAMA_BULAN"] = df["BULAN"].apply(
    lambda x: bulan_order[x-1] if pd.notnull(x) and 1 <= x <= 12 else None
)

df["NAMA_BULAN"] = pd.Categorical(
    df["NAMA_BULAN"],
    categories=bulan_order,
    ordered=True
)


# ===============================
# KATEGORISASI SATUAN
# ===============================

# 🔧 FIXED: logika kategori diperbaiki
df["KATEGORI"] = df["SATUAN"].str.upper().apply(lambda x: "HEWAN" if "EKOR" in x else "PRODUK")


# ===============================
# FILTER GLOBAL
# ===============================

st.header("📌 Dashboard Monitoring Sertifikat Veteriner")

col_prov, col_kota, col_bulan, col_tahun = st.columns(4)

# ===========================
# Dropdown PROVINSI
# ===========================
provinsi_list = ["Semua"] + sorted(df["PROV_ASAL"].dropna().unique())
provinsi = col_prov.selectbox("Pilih Provinsi:", provinsi_list)

# ===========================
# Dropdown KOTA ASAL (DEPENDENT)
# ===========================
if provinsi == "Semua":
    kota_list = ["Semua"] + sorted(df["KOTA_ASAL"].dropna().unique())
else:
    kota_list = ["Semua"] + sorted(
        df[df["PROV_ASAL"] == provinsi]["KOTA_ASAL"].dropna().unique()
    )

kota_asal = col_kota.selectbox("Pilih Kabupaten/Kota:", kota_list)

# ===========================
# Dropdown BULAN & TAHUN
# ===========================
bulan = col_bulan.selectbox("Pilih Bulan:", ["Semua"] + list(df["NAMA_BULAN"].dropna().unique()))
tahun = col_tahun.selectbox("Pilih Tahun:", ["Semua"] + sorted(df["TAHUN"].unique()))

# ===========================
# APPLY FILTER
# ===========================
df_filtered = df.copy()

if provinsi != "Semua":
    df_filtered = df_filtered[df_filtered["PROV_ASAL"] == provinsi]

if kota_asal != "Semua":
    df_filtered = df_filtered[df_filtered["KOTA_ASAL"] == kota_asal]

if bulan != "Semua":
    df_filtered = df_filtered[df_filtered["NAMA_BULAN"] == bulan]

if tahun != "Semua":
    df_filtered = df_filtered[df_filtered["TAHUN"] == tahun]

st.success(f"Dataset terfilter: {len(df_filtered)} baris")



# ===============================
# 1. TREN DISTRIBUSI KOMODITAS
# ===============================

st.subheader("📈 Tren Distribusi Komoditas per Bulan")

tab_hewan, tab_produk = st.tabs(["🐄 Hewan Hidup", "🍖 Produk Hewan"])

def show_chart(filtered_data, label):
    if filtered_data.empty:
        st.warning(f"Tidak ada data untuk kategori {label}")
        return

    df_line = filtered_data.groupby(["NAMA_BULAN", "URAIAN"])["JUMLAH"].sum().reset_index()

    fig = px.line(df_line, x="NAMA_BULAN", y="JUMLAH", color="URAIAN",
                  markers=True, title=f"Tren {label} per Bulan")

    st.plotly_chart(fig, use_container_width=True)

with tab_hewan:
    show_chart(df_filtered[df_filtered["KATEGORI"] == "HEWAN"], "Hewan Hidup")

with tab_produk:
    show_chart(df_filtered[df_filtered["KATEGORI"] == "PRODUK"], "Produk Hewan")


# ===============================
# 2. TOTAL MASUK PER KOMODITAS
# ===============================

st.subheader("📦 Total Masuk per Komoditas")

df_total = df_filtered.groupby("JENIS_HPM")["JUMLAH"].sum().reset_index()

st.bar_chart(df_total.set_index("JENIS_HPM")["JUMLAH"])

# ===============================
# 5. TOP 5 PEMOHON (BERDASARKAN JUMLAH SERTIFIKAT)
# ===============================

st.subheader("🏆 Top 5 Pemohon – Berdasarkan Jumlah Sertifikat (Frekuensi)")

# Pastikan kolom PEMOHON ada
if "PEMOHON" not in df_filtered.columns:
    st.error("Kolom 'PEMOHON' tidak ditemukan dalam dataframe.")
else:
    df_temp = df_filtered.copy()

    # Normalisasi PEMOHON jadi ALL CAPS
    df_temp["PEMOHON"] = df_temp["PEMOHON"].astype(str).str.upper().str.strip()

    # Hitung jumlah baris per pemohon (berapa kali mereka membuat sertifikat)
    top5_pemohon = (
        df_temp.groupby("PEMOHON")
        .size()
        .reset_index(name="JUMLAH_SERTIFIKAT")
        .sort_values(by="JUMLAH_SERTIFIKAT", ascending=False)
        .head(5)
    )

    # Jika tidak ada data
    if top5_pemohon.empty:
        st.warning("Tidak ada data pemohon untuk filter saat ini.")
    else:
        # Tampilkan tabel
        st.table(top5_pemohon)

        # Bar plot (Plotly)
        fig = px.bar(
            top5_pemohon,
            x="PEMOHON",
            y="JUMLAH_SERTIFIKAT",
            text="JUMLAH_SERTIFIKAT",
            title="Top 5 Pemohon Berdasarkan Jumlah Sertifikat",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_title="Pemohon", yaxis_title="Jumlah Sertifikat")

        st.plotly_chart(fig, use_container_width=True)

