import pandas as pd
import re

def clean_pemohon(dataset):
    dataset['PEMOHON'] = dataset.get('PEMOHON', '')
    dataset["PEMOHON"] = dataset["PEMOHON"].astype(str).str.strip().str.upper()
    dataset["PEMOHON"] = dataset["PEMOHON"].str.replace(r"[\n:/\(\),.]", " ", regex=True)
    dataset["PEMOHON"] = dataset["PEMOHON"].str.replace(r"\s+", " ", regex=True).str.strip()
    return dataset

def clean_uraian(dataset):
    dataset["URAIAN"] = dataset["URAIAN"].astype(str).str.strip().str.upper()
    dataset["URAIAN"] = dataset["URAIAN"].str.replace(r"[\n/]", " ", regex=True)
    dataset["URAIAN"] = dataset["URAIAN"].str.replace(r"\s+", " ", regex=True).str.strip()
    return dataset

def split_jumlah(dataset):
    col_sumber = dataset['JUMLAH HPM'].astype(str)
    dataset['JUMLAH'] = col_sumber.apply(lambda x: re.findall(r"[\d\.]+", x)[0] if re.findall(r"[\d\.]+", x) else None)
    dataset['JUMLAH'] = pd.to_numeric(dataset['JUMLAH'], errors='coerce')
    dataset['SATUAN'] = dataset.get('SATUAN','Kilogram')  # default
    return dataset

def process_excel_keluar(file_object, jenis_hpm, bulan_manual=None, tahun_manual=None):
    dataset = pd.read_excel(file_object, sheet_name='Sheet1')

    # Pilih kolom penting
    expected_cols = ['PEMOHON','JENIS HPM','URAIAN','JUMLAH HPM','SATUAN','ALAMAT PENGELUARAN','PROV TUJUAN','KOTA TUJUAN']
    dataset = dataset[[col for col in expected_cols if col in dataset.columns]]

    # Tambahkan kolom tambahan
    dataset['ARAH'] = "KELUAR"
    dataset['JENIS_HPM'] = jenis_hpm.upper()
    if 'ALAMAT PEMASUKAN' in dataset.columns:
        dataset['ALAMAT_PT'] = dataset['ALAMAT PEMASUKAN'].astype(str)
    else:
        dataset['ALAMAT_PT'] = ''

    if 'HP' in dataset.columns:
        dataset['NO_HP'] = dataset['HP'].astype(str)
    else:
        dataset['NO_HP'] = ''

    # Cleaning
    dataset = clean_pemohon(dataset)
    dataset = clean_uraian(dataset)
    dataset = split_jumlah(dataset)

    # Tanggal
    import datetime
    month_mapping = {'Januari':1,'Februari':2,'Maret':3,'April':4,'Mei':5,'Juni':6,
                     'Juli':7,'Agustus':8,'September':9,'Oktober':10,'November':11,'Desember':12}
    tahun = tahun_manual if tahun_manual else 2024
    bulan = month_mapping.get(bulan_manual,1)
    dataset['TANGGAL_BULAN'] = pd.to_datetime(f"{tahun}-{bulan}-01")

    # Pilih kolom final sesuai DB
    final_cols = ['TANGGAL_BULAN','ARAH','JENIS_HPM','PEMOHON','URAIAN','JUMLAH','SATUAN','ALAMAT_PT','NO_HP','PROV TUJUAN','KOTA TUJUAN']
    dataset_final = dataset[[col for col in final_cols if col in dataset.columns]]

    return dataset_final