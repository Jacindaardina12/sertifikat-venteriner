# preprocessing_segmentasi.py

def segmentasi_per_kota(df):
    segment = df.groupby('KOTA_ASAL').agg(
        total_volume=('JUMLAH', 'sum'),
        frekuensi=('JUMLAH', 'count'),
        rata_volume=('JUMLAH', 'mean'),
        jenis_produk=('URAIAN', 'nunique'),
        jenis_hewan=('JENIS_HPM', 'nunique')
    ).reset_index()

    return segment


def segmentasi_per_provinsi(df):
    segment = df.groupby('PROV_ASAL').agg(
        total_volume=('JUMLAH', 'sum'),
        frekuensi=('JUMLAH', 'count'),
        rata_volume=('JUMLAH', 'mean'),
        jenis_produk=('URAIAN', 'nunique'),
        jenis_hewan=('JENIS_HPM', 'nunique')
    ).reset_index()

    return segment


def segmentasi_hewan_berdasarkan_satuan(df):
    df_hewan = df[df['SATUAN'].str.strip().str.lower() == 'ekor']

    segment = df_hewan.groupby('JENIS_HPM').agg(
        total_volume=('JUMLAH', 'sum'),
        frekuensi=('JUMLAH', 'count'),
        rata_volume=('JUMLAH', 'mean'),
        jumlah_kota=('KOTA_ASAL', 'nunique'),
        jumlah_provinsi=('PROV_ASAL', 'nunique')
    ).reset_index()

    return segment


def segmentasi_produk_berdasarkan_satuan(df):
    df_produk = df[df['SATUAN'].str.strip().str.lower() == 'kg']

    segment = df_produk.groupby('URAIAN').agg(
        total_volume=('JUMLAH', 'sum'),
        frekuensi=('JUMLAH', 'count'),
        rata_volume=('JUMLAH', 'mean'),
        jumlah_kota=('KOTA_ASAL', 'nunique'),
        jumlah_provinsi=('PROV_ASAL', 'nunique')
    ).reset_index()

    return segment


def preprocess_segmentasi(df, mode='kota'):
    if mode == 'provinsi':
        return segmentasi_per_provinsi(df)
    elif mode == 'hewan':
        return segmentasi_hewan_berdasarkan_satuan(df)
    elif mode == 'produk':
        return segmentasi_produk_berdasarkan_satuan(df)
    else:
        return segmentasi_per_kota(df)
