import sys
import os

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


# Menambahkan folder root ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from processing_masuk import process_excel_masuk
from database_venteriner import engine
import streamlit as st
import pandas as pd


# app.py
import streamlit as st
import pandas as pd
import unicodedata
from processing_masuk import process_excel_masuk
from database_venteriner import engine  # pastikan ini adalah SQLAlchemy engine

# ====== Streamlit Page Config ======
st.set_page_config(page_title="Sertifikat Veteriner - Upload Masuk", layout="wide")
st.title("Upload Data Masuk")

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

# ====== Fungsi Bantu ======
def clean_string(s):
    """Normalisasi string: hapus spasi, karakter non-ascii, uppercase"""
    if pd.isna(s):
        return ""
    return unicodedata.normalize('NFKD', str(s)).encode('ascii','ignore').decode().strip().upper().replace(" ","")

def normalize_jumlah(x):
    """Convert Excel JUMLAH (string format Indonesia) ke float"""
    if x is None:
        return None
    if isinstance(x, str):
        x = x.replace('.', '').replace(',', '.').strip()
    try:
        return float(x)
    except:
        return None

def month_to_int(month):
    """Konversi nama bulan ke angka"""
    months = ["JANUARI","FEBRUARI","MARET","APRIL","MEI","JUNI",
              "JULI","AGUSTUS","SEPTEMBER","OKTOBER","NOVEMBER","DESEMBER"]
    if isinstance(month, int):
        return month
    month = str(month).strip().upper()
    mapping = {m:i+1 for i,m in enumerate(months)}
    return mapping.get(month, 0)

# ====== Fungsi Visual Bulan Sampai Bulan Terakhir di DB ======
def show_months_until_last(table_name, conn, tahun_filter=None):
    """Tampilkan status bulan sampai bulan terakhir yang ada di DB + bulan berikutnya"""
    cursor = conn.raw_connection().cursor()
    sql = f"SELECT DISTINCT BULAN, TAHUN FROM {table_name}"
    cursor.execute(sql)
    results = cursor.fetchall()

    months = ["Januari","Februari","Maret","April","Mei","Juni",
              "Juli","Agustus","September","Oktober","November","Desember"]
    month_mapping = {i+1: months[i] for i in range(12)}

    existing_months_db_raw = [b for b, t in results if t == tahun_filter]

    existing_months_db = []
    for b in existing_months_db_raw:
        try:
            existing_months_db.append(month_mapping[int(b)])
        except:
            existing_months_db.append(str(b))

    last_month_idx = max([months.index(b) for b in existing_months_db], default=-1)
    display_months = months[:last_month_idx+2]

    st.info(f"📌 Status Bulan di Database Tahun {tahun_filter}:")
    cols = st.columns(len(display_months))
    for idx, month in enumerate(display_months):
        color = "#ff6961" if month in existing_months_db else "#77dd77"
        cols[idx].markdown(
            f"<div style='background-color:{color}; padding:8px; text-align:center; border-radius:5px; font-weight:bold'>{month}</div>",
            unsafe_allow_html=True
        )

# ====== Fungsi Insert ke MySQL  ======
from sqlalchemy import text
import streamlit as st

def insert_to_mysql(df_final, table_name, engine):
    inserted_rows = 0

    with engine.begin() as conn:  # commit otomatis
        for i, row in df_final.iterrows():
            columns = ", ".join(row.index)
            placeholders = ", ".join([f":{col}" for col in row.index])
            sql_insert = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
            conn.execute(sql_insert, row.to_dict())
            inserted_rows += 1

    st.success(f"✅ Berhasil insert {inserted_rows} baris ke tabel {table_name}!")

# ====== Filter Tahun ======
tahun_filter = st.number_input("Filter Tahun (untuk lihat status bulan)", min_value=2000, max_value=2100, value=2025, step=1)
show_months_until_last(table_name='sertifikat_masuk', conn=engine, tahun_filter=tahun_filter)

# ====== Pilihan Dropdown ======
jenis_hpm = st.selectbox("Jenis HPM", ["PRODUK HEWAN", "HEWAN"])
bulan = st.selectbox("Bulan", ["Januari","Februari","Maret","April","Mei","Juni",
                               "Juli","Agustus","September","Oktober","November","Desember"])
# Tahun di bagian upload manual / file
tahun = st.number_input(
    "Tahun", 
    min_value=2000, max_value=2100, value=2025, step=1,
    key="tahun_upload"  # <-- key unik lain
)

# ====== Upload File ======
uploaded_file = st.file_uploader("Upload file Excel (.xlsx)", type=["xlsx"])

# ====== Proses Data ======
if uploaded_file is not None:
    if st.button("Proses Data"):
        try:
            df_processed = process_excel_masuk(uploaded_file, jenis_hpm, bulan, tahun)
            st.session_state['df_processed'] = df_processed
            st.success("✅ Data berhasil diproses")
            st.dataframe(df_processed)
        except Exception as e:
            st.error(f"❌ Terjadi error saat memproses data: {e}")

# ====== Upload ke MySQL ======
if 'df_processed' in st.session_state:
    if st.button("Upload ke database"):
        try:
            insert_to_mysql(st.session_state['df_processed'], 'sertifikat_masuk', engine)
        except Exception as e:
            st.error(f"❌ Terjadi error saat upload ke database: {e}")
 # Clear cache agar dropdown update otomatis
    st.cache_data.clear()

# ====== Info Tambahan ======
if 'df_processed' in st.session_state:
    st.info(f"Jumlah baris siap upload: {len(st.session_state['df_processed'])}")




# File: input_data.py
import streamlit as st
import pandas as pd
from processing_masuk import insert_to_mysql

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from processing_masuk import insert_to_mysql

# ===============================
# Koneksi ke DB
# ===============================
engine = create_engine(f"mysql+pymysql://root:cCoiaAEpiqVgAaqcAyjdxORwIDyKWGZw@tramway.proxy.rlwy.net:27684/railway")

# Load data sertifikat_masuk
@st.cache_data(ttl=10)  # TTL = time to live, data cache akan refresh setiap 10 detik
def load_data():
    df = pd.read_sql("SELECT * FROM sertifikat_masuk", engine)
    return df
# Load data sertifikat_masuk terbaru
df = load_data()

# ===============================
# Header Form
# ===============================

import streamlit as st
import pandas as pd
from processing_masuk import insert_to_mysql


st.header("Input Data Manual Sertifikat Veteriner")

# Ambil daftar pemohon unik dari DB
existing_pemohon = df['PEMOHON'].dropna().unique().tolist()
existing_pemohon = [p.upper() for p in existing_pemohon]
existing_pemohon.sort()

# Ambil daftar jenis HPM unik
existing_jenis_hpm = df['JENIS_HPM'].dropna().unique().tolist()
existing_jenis_hpm = [p.upper() for p in existing_jenis_hpm]
existing_jenis_hpm.sort()

# ===============================
# Pemohon
# ===============================
pemohon_choice = st.selectbox("Pilih Pemohon", ["-- Baru --"] + existing_pemohon)

if pemohon_choice == "-- Baru --":
    pemohon_final = st.text_input("Masukkan Nama Pemohon Baru", key="pemohon_baru").strip().upper()
    ALAMAT_PEMASUKAN = st.text_input("Alamat", key="alamat_baru")
    PROV_ASAL = st.text_input("Provinsi Asal", key="prov_baru")
    KOTA_ASAL = st.text_input("Kabupaten/Kota Asal", key="kota_baru")
    HP = st.text_input("Nomor HP", key="hp_baru")
else:
    pemohon_final = pemohon_choice
    pemohon_data = df[df['PEMOHON'].str.upper() == pemohon_final].iloc[0]
    ALAMAT_PEMASUKAN = st.text_input("Alamat", value=pemohon_data['ALAMAT_PEMASUKAN'], key=f"alamat_{pemohon_final}")
    PROV_ASAL = st.text_input("Provinsi Asal", value=pemohon_data['PROV_ASAL'], key=f"prov_{pemohon_final}")
    KOTA_ASAL = st.text_input("Kabupaten/Kota Asal", value=pemohon_data['KOTA_ASAL'], key=f"kota_{pemohon_final}")
    HP = st.text_input("Nomor HP", value=pemohon_data['HP'], key=f"hp_{pemohon_final}")

# ===============================
# Tanggal
# ===============================
from datetime import datetime

# Ambil tanggal dari date_input
tanggal_bulan_input = st.date_input("Tanggal Masuk", value=datetime.today())

# Konversi ke string YYYY-MM-DD
tanggal_bulan_str = tanggal_bulan_input.strftime("%Y-%m-%d")

# Ambil bulan & tahun
bulan_input = tanggal_bulan_input.month
tahun_input = tanggal_bulan_input.year


# ===============================
# Jenis HPM & Uraian
# ===============================
jenis_hpm_choice = st.selectbox("Pilih Jenis HPM", ["-- Baru --"] + existing_jenis_hpm, key="jenis_hpm_choice")

if jenis_hpm_choice == "-- Baru --":
    jenis_hpm_final = st.text_input("Masukkan Jenis HPM Baru", key="jenis_hpm_baru").strip().upper()
    uraian_final = st.text_input("Masukkan Uraian Baru", key="uraian_baru").strip().upper()
else:
    jenis_hpm_final = jenis_hpm_choice
    uraian_options = df[df['JENIS_HPM'].str.upper() == jenis_hpm_choice.upper()]['URAIAN'].dropna().unique().tolist()
    uraian_options = [u.upper() for u in uraian_options]
    uraian_options.sort()

    uraian_choice = st.selectbox("Pilih Uraian", ["-- Baru --"] + uraian_options, key="uraian")
    if uraian_choice == "-- Baru --":
        uraian_final = st.text_input("Masukkan Uraian Baru", key="uraian_manual").strip().upper()
    else:
        uraian_final = uraian_choice

# ===============================
# Jumlah & Satuan
# ===============================
# Jumlah di input manual (sudah ada key, pastikan unik)
JUMLAH = st.number_input(
    "Jumlah", min_value=0.0, step=1.0, key="jumlah_manual"  # <-- ganti key supaya unik
)
SATUAN = st.selectbox("Satuan", ["KG", "EKOR"], key="satuan")

# ===============================
# Tombol Simpan
# ===============================
if st.button("Simpan", key="simpan_manual"):
    if pemohon_final == "":
        st.warning("⚠️ Mohon isi nama pemohon.")
    else:
        df_manual = pd.DataFrame([{
        "PEMOHON": pemohon_final.upper(),
        "JENIS_HPM": jenis_hpm_final.upper(),
        "URAIAN": uraian_final.upper(),
        "JUMLAH": JUMLAH,
        "SATUAN": SATUAN.upper(),
        "ALAMAT_PEMASUKAN": ALAMAT_PEMASUKAN.upper(),
        "PROV_ASAL": PROV_ASAL.upper(),
        "KOTA_ASAL": KOTA_ASAL.upper(),
        "HP": HP,
        "TANGGAL_BULAN": pd.to_datetime(tanggal_bulan_input),
        "BULAN": bulan_input,
        "TAHUN": tahun_input
}])
        insert_to_mysql(df_manual, 'sertifikat_masuk', engine)

        st.success("✅ Data berhasil disimpan ke database sertifikat_masuk!")
