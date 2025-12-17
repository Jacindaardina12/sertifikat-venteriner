import pandas as pd

def prepare_monthly(df, satuan):
    """
    Filter berdasarkan satuan (KG/Ekor/Liter/TON)
    Convert tanggal ke datetime
    Resample jadi bulanan
    """
    df = df[df["SATUAN"].str.upper() == satuan.upper()]

    df["TANGGAL_BULAN"] = pd.to_datetime(df["TANGGAL_BULAN"])
    df = df.set_index("TANGGAL_BULAN")

    ts = df["JUMLAH"].resample("M").sum()
    return ts
