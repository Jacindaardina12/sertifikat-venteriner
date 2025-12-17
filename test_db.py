# app.py
import streamlit as st
from processing_masuk import process_excel_masuk
from database_venteriner import engine
import pandas as pd
import unicodedata

# ====== Streamlit Page Config ======
st.set_page_config(page_title="Sertifikat Veteriner - Upload Masuk", layout="wide")
st.title("Upload Data Masuk")

# ====== Fungsi Bantu ======
def clean_string(s):
    """Normalisasi string: hapus spasi, karakter non-ascii, uppercase"""
    if pd.isna(s):
        return ""
    return unicodedata.normalize('NFKD', str(s)).encode('ascii','ignore').decode().strip().upper().replace(" ","")

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
    """
    Tampilkan status bulan sampai bulan terakhir yang ada di DB + bulan berikutnya untuk upload
    Mendukung BULAN di DB berupa angka (1-12) atau string (Januari, Februari,...)
    """
    cursor = conn.raw_connection().cursor()
    sql = f"SELECT DISTINCT BULAN, TAHUN FROM {table_name}"
    cursor.execute(sql)
    results = cursor.fetchall()

    # Daftar nama bulan
    months = ["Januari","Februari","Maret","April","Mei","Juni",
              "Juli","Agustus","September","Oktober","November","Desember"]

    # Mapping angka -> nama bulan
    month_mapping = {i+1: months[i] for i in range(12)}  # 1 -> 'Januari'

    # Ambil bulan yang ada di DB untuk tahun_filter
    existing_months_db_raw = [b for b, t in results if t == tahun_filter]

    # Konversi semua bulan ke nama bulan
    existing_months_db = []
    for b in existing_months_db_raw:
        try:
            existing_months_db.append(month_mapping[int(b)])
        except:
            existing_months_db.append(str(b))

    # Tentukan indeks bulan terakhir
    last_month_idx = max([months.index(b) for b in existing_months_db], default=-1)

    # Ambil bulan sampai bulan terakhir + 1 bulan berikutnya
    display_months = months[:last_month_idx+2]  # +1 untuk bulan berikutnya

    # Render di Streamlit
    st.info(f"📌 Status Bulan di Database Tahun {tahun_filter}:")
    cols = st.columns(len(display_months))
    for idx, month in enumerate(display_months):
        if month in existing_months_db:
            # Bulan sudah ada → merah
            cols[idx].markdown(
                f"<div style='background-color:#ff6961; padding:8px; text-align:center; border-radius:5px; font-weight:bold'>{month}</div>",
                unsafe_allow_html=True
            )
        else:
            # Bulan berikutnya → hijau
            cols[idx].markdown(
                f"<div style='background-color:#77dd77; padding:8px; text-align:center; border-radius:5px; font-weight:bold'>{month}</div>",
                unsafe_allow_html=True
            )

# ====== Fungsi Insert ke MySQL dengan cek duplikasi ======
def insert_to_mysql(df_final, table_name, conn):
    cursor = conn.raw_connection().cursor()
    inserted_rows = 0
    skipped_rows = 0

    for i, row in df_final.iterrows():
        bulan_val = month_to_int(row['BULAN'])
        tahun_val = int(row['TAHUN'])
        jenis_hpm_val = clean_string(row['JENIS_HPM'])
        pemohon_val = clean_string(row['PEMOHON'])

        sql_check = f"""
            SELECT COUNT(*) 
            FROM {table_name} 
            WHERE BULAN=%s AND TAHUN=%s 
              AND REPLACE(UPPER(TRIM(JENIS_HPM)),' ','')=%s
              AND REPLACE(UPPER(TRIM(PEMOHON)),' ','')=%s
        """
        cursor.execute(sql_check, (bulan_val, tahun_val, jenis_hpm_val, clean_string(row['PEMOHON'])))
        if cursor.fetchone()[0] > 0:
            st.warning(f"❌ Data {row['JENIS_HPM']} bulan {bulan_val} tahun {tahun_val} sudah ada. Baris dilewati.")
            skipped_rows += 1
            continue

        # Prepare values
        placeholders = ", ".join(["%s"] * len(row))
        columns = ", ".join(row.index)
        values = []
        for col in row.index:
            if col.upper() == "BULAN":
                values.append(bulan_val)
            elif col.upper() == "JENIS_HPM":
                values.append(jenis_hpm_val)
            else:
                values.append(row[col])

        sql_insert = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql_insert, tuple(values))
        inserted_rows += 1

    conn.raw_connection().commit()
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
