import unicodedata
import pandas as pd
from datetime import datetime
import calendar
import streamlit as st
import pymysql
import difflib


# =============================================
# Fungsi bantu: cari kolom paling mirip
# =============================================
def match_column(col_name, expected_cols):
    """
    Mencari kolom di Excel yang paling mirip dengan expected_cols
    """
    match = difflib.get_close_matches(col_name.upper().strip(), expected_cols, n=1, cutoff=0.6)
    if match:
        return match[0]
    return None

# =============================================
# Fungsi utama untuk proses Excel
# =============================================
def process_excel_masuk(uploaded_file, jenis_hpm, bulan, tahun=None):
    if uploaded_file is None:
        st.error("❌ File Excel tidak ditemukan. Silakan upload file terlebih dahulu.")
        return None

    if tahun is None:
        tahun = datetime.now().year

    try:
        # === Baca Excel dan pastikan kolom HP dibaca sebagai string ===
        df = pd.read_excel(uploaded_file, dtype={'HP': str})

        # === Bersihkan kolom HP supaya 0 di depan tidak hilang ===
        df['HP'] = df['HP'].astype(str).str.strip().str.replace('.0', '', regex=False)

    except Exception as e:
        st.error(f"❌ Gagal membaca Excel: {e}")
        return None

    # Bersihkan nama kolom
    df.columns = df.columns.str.strip()

    # Daftar kolom yang diharapkan
    expected_cols = [
        'NO', 'PEMOHON', 'JENIS HPM', 'URAIAN', 'JUMLAH HPM',
        'ALAMAT PEMASUKAN', 'PROV ASAL', 'KOTA ASAL', 'HP'
    ]

    # Rename kolom Excel sesuai expected_cols (pakai fuzzy match)
    rename_dict = {}
    for col in df.columns:
        matched = match_column(col, expected_cols)
        if matched:
            rename_dict[col] = matched
    df.rename(columns=rename_dict, inplace=True)

    # Pastikan semua kolom ada
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""

    # Normalisasi teks
    text_cols = ['PEMOHON', 'URAIAN', 'ALAMAT PEMASUKAN', 'PROV ASAL', 'KOTA ASAL', 'HP']
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip().replace('nan', '', regex=False)

    # Pastikan kolom HP selalu string dan leading zero tidak hilang
    df['HP'] = df['HP'].astype(str).str.strip().replace('nan', '', regex=False)

    # Ekstrak JUMLAH dan SATUAN
    qty = df['JUMLAH HPM'].astype(str).str.replace(',', '.')
    extracted = qty.str.extract(r'([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z]+)?', expand=True)
    df['JUMLAH'] = pd.to_numeric(extracted[0], errors='coerce').astype(float)
    df['SATUAN'] = extracted[1].fillna('').str.upper()

    # KONVERSI TON → KG (jika diperlukan)
    df.loc[df['SATUAN'] == 'TON', 'JUMLAH'] = df.loc[df['SATUAN'] == 'TON', 'JUMLAH'] * 1000
    df.loc[df['SATUAN'] == 'TON', 'SATUAN'] = 'KG'

    konversi = {
    "TON": 1000,
    "KWINTAL": 100,
    "GRAM": 0.001
    }

    for satuan, faktor in konversi.items():
        df.loc[df['SATUAN'] == satuan, 'JUMLAH'] *= faktor
        df.loc[df['SATUAN'] == satuan, 'SATUAN'] = 'KG'



    # Mapping bulan Indonesia ke angka
    bulan_mapping = {
        'JANUARI': 1, 'FEBRUARI': 2, 'MARET': 3, 'APRIL': 4,
        'MEI': 5, 'JUNI': 6, 'JULI': 7, 'AGUSTUS': 8,
        'SEPTEMBER': 9, 'OKTOBER': 10, 'NOVEMBER': 11, 'DESEMBER': 12
    }

    bulan_num = bulan_mapping.get(str(bulan).strip().upper(), 1)

    # Simpan TANGGAL_BULAN sebagai tanggal 1
    df['TANGGAL_BULAN'] = pd.to_datetime({
        'year': [int(tahun)] * len(df),
        'month': [bulan_num] * len(df),
        'day': [1] * len(df)
    })

    # Kolom BULAN & TAHUN
    df['BULAN'] = bulan_num
    df['TAHUN'] = int(tahun)

    # Mapping nama kolom Excel ke SQL
    df.rename(columns={
        'ALAMAT PEMASUKAN': 'ALAMAT_PEMASUKAN',
        'PROV ASAL': 'PROV_ASAL',
        'KOTA ASAL': 'KOTA_ASAL',
        'JENIS HPM': 'JENIS_HPM'
    }, inplace=True)


    # Susun kolom final
    final_cols = [
        'TANGGAL_BULAN', 'BULAN', 'TAHUN',
        'PEMOHON', 'JENIS_HPM', 'URAIAN',
        'JUMLAH', 'SATUAN',
        'ALAMAT_PEMASUKAN', 'PROV_ASAL', 'KOTA_ASAL', 'HP'
    ]

    # Pastikan semua kolom final ada
    for col in final_cols:
        if col not in df.columns:
            df[col] = ""

    # Trim whitespace untuk kolom string
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()
        # Normalisasi tambahan
    import unicodedata

    string_cols = [
        'PEMOHON','JENIS_HPM','URAIAN','ALAMAT_PEMASUKAN',
        'PROV_ASAL','KOTA_ASAL','HP','SATUAN'
        ]

    def normalize_string(s):
        if pd.isna(s):
            return ""
        return unicodedata.normalize('NFKD', str(s)).encode('ascii','ignore').decode().strip().upper()

# Apply normalisasi
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].apply(normalize_string)
        else:
            df[col] = ""
# Round jumlah
    df['JUMLAH'] = df['JUMLAH'].fillna(0).astype(float).round(2)

# Fill NaN aman
    df = df.fillna({
         'PEMOHON':'', 'JENIS_HPM':'', 'URAIAN':'', 'ALAMAT_PEMASUKAN':'',
         'PROV_ASAL':'', 'KOTA_ASAL':'', 'HP':'', 'SATUAN':'', 'JUMLAH':0
         })
    df = df[final_cols].copy()
    return df

# =============================================
# Fungsi insert ke MySQL
# =============================================

from sqlalchemy import create_engine
from sqlalchemy import text
import streamlit as st

def insert_to_mysql(df, table_name, engine):
    """
    Insert semua DataFrame ke MySQL tanpa cek duplikasi.
    """
    inserted_rows = 0

    with engine.begin() as conn:  # commit otomatis
        for i, row in df.iterrows():
            columns = ", ".join(row.index)
            placeholders = ", ".join([f":{col}" for col in row.index])
            sql_insert = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
            conn.execute(sql_insert, row.to_dict())
            inserted_rows += 1

    st.success(f"✅ Berhasil insert {inserted_rows} baris ke tabel {table_name}!")

#-----------------------------------------------------------------

from sqlalchemy import text

def insert_to_mysql(df, table_name, engine):
    """
    Insert DataFrame ke MySQL menggunakan SQLAlchemy engine.
    Cek duplikasi sebelum insert.
    """
    inserted_rows = 0
    skipped_rows = 0

    with engine.begin() as conn:  # commit otomatis
        for i, row in df.iterrows():
            # Normalisasi string untuk cek duplikasi
            def clean_string(s):
                if pd.isna(s):
                    return ""
                import unicodedata
                return unicodedata.normalize('NFKD', str(s)).encode('ascii','ignore').decode().strip().upper().replace(" ","")

            # Insert data baru
            columns = ", ".join(row.index)
            placeholders = ", ".join([f":{col}" for col in row.index])
            sql_insert = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
            conn.execute(sql_insert, row.to_dict())
            inserted_rows += 1

    st.success(f"✅ Berhasil insert {inserted_rows} baris ke tabel {table_name}!")

