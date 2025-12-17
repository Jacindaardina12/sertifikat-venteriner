# app.py
import streamlit as st
import pandas as pd
import unicodedata
from processing_masuk import process_excel_masuk
from database_venteriner import engine  # pastikan ini adalah SQLAlchemy engine

# ====== Streamlit Page Config ======
st.set_page_config(page_title="Sertifikat Veteriner - Upload Masuk", layout="wide")
st.title("Upload Data Masuk")

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

# ====== Fungsi Insert ke MySQL dengan cek duplikasi ======
from sqlalchemy import text

def insert_to_mysql(df_final, table_name, engine):
    inserted_rows = 0
    skipped_rows = 0

    with engine.begin() as conn:  # commit otomatis
        for i, row in df_final.iterrows():
            # Cek duplikat full row
            # ==== CEK DUPLIKAT YANG BENAR ====
            sql_check = text("""
                SELECT COUNT(*) FROM sertifikat_masuk
                WHERE BULAN = :BULAN
                    AND TAHUN = :TAHUN
                    AND REPLACE(UPPER(TRIM(JENIS_HPM)), ' ', '') = :JENIS_HPM
                    AND REPLACE(UPPER(TRIM(PEMOHON)), ' ', '') = :PEMOHON
                    AND REPLACE(UPPER(TRIM(URAIAN)), ' ', '') = :URAIAN
                    AND REPLACE(UPPER(TRIM(ALAMAT_PEMASUKAN)), ' ', '') = :ALAMAT_PEMASUKAN
                    AND REPLACE(UPPER(TRIM(PROV_ASAL)), ' ', '') = :PROV_ASAL
                    AND REPLACE(UPPER(TRIM(KOTA_ASAL)), ' ', '') = :KOTA_ASAL
                    AND REPLACE(UPPER(TRIM(HP)), ' ', '') = :HP
                    AND ROUND(JUMLAH, 2) = ROUND(:JUMLAH, 2)
                    AND SATUAN = :SATUAN
                """)

            params = {
                "BULAN": row["BULAN"],
                "TAHUN": row["TAHUN"],
                "JENIS_HPM": clean_string(row["JENIS_HPM"]),
                "PEMOHON": clean_string(row["PEMOHON"]),
                "URAIAN": clean_string(row["URAIAN"]),
                "ALAMAT_PEMASUKAN": clean_string(row["ALAMAT_PEMASUKAN"]),
                "PROV_ASAL": clean_string(row["PROV_ASAL"]),
                "KOTA_ASAL": clean_string(row["KOTA_ASAL"]),
                "HP": clean_string(row["HP"]),
                "JUMLAH": normalize_jumlah(row["JUMLAH"]),
                "SATUAN": row["SATUAN"],}

            result = conn.execute(sql_check, params)
            if result.scalar() > 0:
                st.warning(f"❌ Duplikat baris ke-{i+1} (detected). Skip.")
                skipped_rows += 1
                continue

            # Insert semua kolom
            columns = ", ".join(row.index)
            placeholders = ", ".join([f":{col}" for col in row.index])
            sql_insert = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
            conn.execute(sql_insert, row.to_dict())
            inserted_rows += 1

    st.success(f"✅ Berhasil insert {inserted_rows} baris baru. ❌ Dilewati {skipped_rows} baris karena duplikat.")

# ====== Filter Tahun ======
tahun_filter = st.number_input("Filter Tahun (untuk lihat status bulan)", min_value=2000, max_value=2100, value=2025, step=1)
show_months_until_last(table_name='sertifikat_masuk', conn=engine, tahun_filter=tahun_filter)

# ====== Pilihan Dropdown ======
jenis_hpm = st.selectbox("Jenis HPM", ["PRODUK HEWAN", "HEWAN"])
bulan = st.selectbox("Bulan", ["Januari","Februari","Maret","April","Mei","Juni",
                               "Juli","Agustus","September","Oktober","November","Desember"])
tahun = st.number_input("Tahun", min_value=2000, max_value=2100, value=2025, step=1)

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

# ====== Info Tambahan ======
if 'df_processed' in st.session_state:
    st.info(f"Jumlah baris siap upload: {len(st.session_state['df_processed'])}")
