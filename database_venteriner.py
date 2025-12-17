from sqlalchemy import create_engine
import pandas as pd

# --- Konfigurasi koneksi ---
DB_USER = "root"
DB_PASS = "cCoiaAEpiqVgAaqcAyjdxORwIDyKWGZw"
DB_HOST = "tramway.proxy.rlwy.net"
DB_PORT = "27684"
DB_NAME = "railway"

# --- Buat engine di luar try biar bisa diimport ---
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    # --- Baca file Excel ---
    df = pd.read_excel("DATA UTAMA FINAL SERTIFIKAT VENTERINER.xlsx")
    
    # --- Upload data ke tabel 'sertifikat' ---
    df.to_sql('sertifikat', con=engine, if_exists='append', index=False)
    
    print("✅ Data berhasil dikirim ke database.")

except FileNotFoundError:
    print("❌ File Excel tidak ditemukan. Pastikan file ada di folder yang sama dengan script ini.")
except Exception as e:
    print("❌ Terjadi error saat koneksi atau upload data:", e)
