import pandas as pd
import re

# =============================================================================
# FUNGSI HELPER
# =============================================================================

def clean_pemohon(dataset):
    if 'PEMOHON ' in dataset.columns:
        dataset = dataset.rename(columns={'PEMOHON ': 'PEMOHON'})
    
    if 'PEMOHON' in dataset.columns:
        dataset["PEMOHON"] = dataset["PEMOHON"].str.strip().str.upper()
        dataset["PEMOHON"] = dataset["PEMOHON"].str.replace(r"[\n:/\(\),.]", " ", regex=True)
        dataset["PEMOHON"] = dataset["PEMOHON"].str.replace(r"\s+", " ", regex=True).str.strip()
        mapping = {
            "PT. CHAROEN POKPHAND INDONESIA , BANDUNG": "PT CHAROEN POKPHAND INDONESIA",
            "PT. CHAROEN POKPHAND INDONESIA - PLANT MAKASSAR": "PT CHAROEN POKPHAND INDONESIA",
            "PT CHAROEN POKPHAND INDONESIA - PLANT MAKASSAR": "PT CHAROEN POKPHAND INDONESIA",
            "PT MALLESSO INVESTAMA ABAD": "PT MALLESSO INVESTAMA ABADI",
            "PT SREEYA SEWU INDONESIA. TBK": "PT SREEYA SEWU INDONESIA",
            "PT CIOMAS ADISATWA JTMII": "PT CIOMAS ADISATWA",
            "PT SANTI WIJAYA MEAT /": "PT SANTI WIJAYA MEAT",
            ": PT SANTOSA AGRINDO": "PT SANTOSA AGRINDO",
            ": PT HAVI INDONESIA": "PT HAVI INDONESIA"
        }
        dataset["PEMOHON"] = dataset["PEMOHON"].replace(mapping)
    else:
        print("⚠️ Kolom 'PEMOHON' tidak ditemukan di Excel, lewati proses clean_pemohon")
    return dataset

def clean_uraian(dataset):
    if 'URAIAN' in dataset.columns:
        dataset["URAIAN"] = (
            dataset["URAIAN"]
            .str.strip()
            .str.upper()
            .str.replace(r"[\n/]", " ", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )
        mapping = {
            "AYAM PEDAGING RAS PEDAGING": "AYAM PEDAGING",
            "AYAM KAMPUNG AYAM JANTAN BETINA": "AYAM KAMPUNG",
            "AYAM KAMPUNG AYAM JANTAN": "AYAM KAMPUNG",
            "AYAM KAMPUNG PHILIPIN": "AYAM KAMPUNG",
            "SAPI SAPI": "SAPI",
            "SAPI SAPI MADURA CROSS DAN SAPI MADURA JANTAN UMUR 2-3 TAHUN": "SAPI MADURA",
            "SAPI SAPI MADURA DAN SAPI MADURA CROSS": "SAPI MADURA",
            "SAPI MADURA DAN MADURA CROSS": "SAPI MADURA",
            "SAPI LIMOUSIN, SIMENTAL, MADURA": "SAPI LIMOSIN",
            "KARKAS DAGING (SEGAR DAN BEKU": "KARKAS DAGING SEGAR DAN BEKU",
            "SUSU PASTEURISASI SUSU ULTRAPASTEURISAS": "SUSU PASTEURISASI/ULTRAPASTEURISASI",
            "KERBAU KERBAU JANTAN": "KERBAU",
            "KERBAU KERBAU LOKAL JANTAN": "KERBAU",
            "KUCING PERSIA 4": "KUCING PERSIA",
        }
        dataset["URAIAN"] = dataset["URAIAN"].replace(mapping)
    return dataset

def split_jumlah_hpm(dataset):
    if 'JUMLAH' in dataset.columns:
        col_sumber = dataset['JUMLAH'].astype(str)
        dataset['JUMLAH'] = col_sumber.apply(lambda x: re.findall(r"[\d\.]+", x)[0] if re.findall(r"[\d\.]+", x) else None)
        dataset['JUMLAH'] = pd.to_numeric(dataset['JUMLAH'], errors='coerce')
        dataset['SATUAN'] = col_sumber.apply(lambda x: re.findall(r'[a-zA-Z]+', x)[-1] if re.findall(r'[a-zA-Z]+', x) else None)
        dataset['SATUAN'] = dataset['SATUAN'].str.upper()
    return dataset

def clean_prov_kota(dataset):
    if 'KOTA_ASAL' in dataset.columns:
        dataset = dataset.rename(columns={'KOTA_ASAL': 'KOTA'})
    if 'PROV ASAL' in dataset.columns:
        dataset = dataset.rename(columns={'PROV ASAL': 'PROVINSI'})
    if 'KOTA' in dataset.columns:
        dataset["KOTA"] = dataset["KOTA"].str.strip().str.upper()
    if 'PROVINSI' in dataset.columns:
        dataset["PROVINSI"] = dataset["PROVINSI"].astype(str).str.strip().str.upper()
    return dataset

# =============================================================================
# FUNGSI UTAMA
# =============================================================================

def process_excel_data(file_object, jenis_transaksi, bulan_manual=None, tahun_manual=None, jenis_hpm_manual=None):
    try:
        dataset = pd.read_excel(file_object, sheet_name='Sheet1')
    except Exception as e:
        print(f"Error membaca file Excel: {e}")
        return None

    # Drop kolom NO jika ada
    dataset = dataset.drop(columns=[col for col in ['NO ', 'NO'] if col in dataset.columns], errors='ignore')

    # Tambahkan bulan/tahun manual
    month_mapping = {
        'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4, 'Mei': 5, 'Juni': 6,
        'Juli': 7, 'Agustus': 8, 'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12
    }
    if 'BULAN' in dataset.columns:
        dataset['TAHUN'] = dataset['BULAN'].astype(str).str.extract(r'(\d{4})').fillna(tahun_manual).astype(int)
        dataset['BULAN_NAMA'] = dataset['BULAN'].astype(str).str.extract(r'([A-Za-z]+)')
        dataset['BULAN_ANGKA'] = dataset['BULAN_NAMA'].str.capitalize().map(month_mapping)
    else:
        dataset['TAHUN'] = tahun_manual
        dataset['BULAN_ANGKA'] = month_mapping.get(bulan_manual, 1)

    dataset['TANGGAL'] = pd.to_datetime(dataset['TAHUN'].astype(str) + '-' + dataset['BULAN_ANGKA'].astype(str) + '-01')
    dataset = dataset.drop(columns=[col for col in ['BULAN', 'BULAN_NAMA', 'BULAN_ANGKA', 'TAHUN'] if col in dataset.columns], errors='ignore')

    # Tambahkan kolom JENIS_TRANSAKSI
    dataset['JENIS_TRANSAKSI'] = jenis_transaksi

    # Tambahkan JENIS_HPM dari dropdown
    if jenis_hpm_manual is not None:
        dataset['JENIS_HPM'] = jenis_hpm_manual

    # Jalankan fungsi cleaning
    dataset = clean_pemohon(dataset)
    dataset = clean_uraian(dataset)
    dataset = split_jumlah_hpm(dataset)
    dataset = clean_prov_kota(dataset)

    # Tambahkan kolom ALAMAT_PT & NO_HP
    if 'ALAMAT PEMASUKAN' in dataset.columns:
        dataset['ALAMAT_PT'] = dataset['ALAMAT PEMASUKAN'].astype(str).str.strip()
    elif 'ALAMAT PENGELUARAN' in dataset.columns:
        dataset['ALAMAT_PT'] = dataset['ALAMAT PENGELUARAN'].astype(str).str.strip()
    else:
        dataset['ALAMAT_PT'] = None

    if 'HP' in dataset.columns:
        dataset['NO_HP'] = dataset['HP'].astype(str).str.strip()
    else:
        dataset['NO_HP'] = None

    # Pilih kolom final sesuai database
    final_columns = [
        'TANGGAL', 'JENIS_TRANSAKSI', 'JENIS_HPM', 'PEMOHON', 'URAIAN',
        'JUMLAH', 'SATUAN', 'KOTA', 'PROVINSI', 'ALAMAT_PT', 'NO_HP'
    ]
    dataset_final = dataset[[col for col in final_columns if col in dataset.columns]]
    return dataset_final
