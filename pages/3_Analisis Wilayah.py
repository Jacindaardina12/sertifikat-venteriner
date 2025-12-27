import os
import streamlit as st

# =====================================
# PAGE CONFIG (HARUS PALING ATAS)
# =====================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logo_path = os.path.join(BASE_DIR, "assets", "dinpert.png")

st.set_page_config(
    page_title="Dashboard Segmentasi Pemohon Sertifikat Veteriner",
    page_icon=logo_path,
    layout="wide"
)


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from database_venteriner import engine

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Dashboard Segmentasi Pemohon Sertifikat Veteriner",
    layout="wide"
)
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

# ==================================================
# CUSTOM CSS — CLEAN, INSTITUSIONAL, TENANG
# ==================================================
st.markdown("""
<style>
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

.header-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 0.3rem;
}

.header-subtitle {
    font-size: 1.05rem;
    color: #6b7280;
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.45rem;
    font-weight: 700;
    margin-top: 2.5rem;
    margin-bottom: 0.8rem;
}

.metric-card {
    background-color: #f9fafb;
    padding: 1.3rem;
    border-radius: 14px;
    border-left: 6px solid #2563eb;
}

.metric-label {
    font-size: 0.85rem;
    color: #6b7280;
}

.metric-value {
    font-size: 1.9rem;
    font-weight: 800;
}

.footer-box {
    background-color: #f3f4f6;
    padding: 1.2rem;
    border-radius: 12px;
    font-size: 0.85rem;
    color: #374151;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER (JUDUL & TUJUAN)
# ==================================================
st.markdown(
    """
<div class="header-title">
Dashboard Segmentasi Pemohon Sertifikat Veteriner
</div>
<div class="header-subtitle">
Analisis berbasis data untuk mendukung pengambilan keputusan layanan,
pengawasan, dan pembinaan pemohon
</div>
""",
    unsafe_allow_html=True
)

# ==================================================
# DEFINISI FITUR SEGMENTASI
# ==================================================
fitur = [
    "total_volume",
    "total_transaksi",
    "variasi_jenis_hpm",
    "variasi_bulan",
    "variasi_kota_asal",
    "rata_volume_transaksi"
]

# ==================================================
# AUTO LOAD & SEGMENTASI (ROBUST)
# ==================================================
if "df_segmentasi" not in st.session_state:

    with st.spinner("Memproses data segmentasi pemohon..."):

        query = "SELECT * FROM sertifikat_masuk"
        df_raw = pd.read_sql(query, engine)

        df_agg = df_raw.groupby("PEMOHON").agg(
            total_volume=("JUMLAH", "sum"),
            total_transaksi=("ID", "count"),
            variasi_jenis_hpm=("JENIS_HPM", "nunique"),
            variasi_bulan=("BULAN", "nunique"),
            variasi_kota_asal=("KOTA_ASAL", "nunique")
        ).reset_index()

        df_agg["rata_volume_transaksi"] = (
            df_agg["total_volume"] / df_agg["total_transaksi"]
        )

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_agg[fitur])

        model = KMeans(n_clusters=3, random_state=42)
        df_agg["cluster"] = model.fit_predict(X_scaled)

        st.session_state["df_segmentasi"] = df_agg

    st.success("Segmentasi pemohon berhasil dibangun.")

df_agg = st.session_state["df_segmentasi"]

# ==================================================
# SECTION 1 — RINGKASAN EKSEKUTIF
# ==================================================
st.markdown('<div class="section-title">Ringkasan Eksekutif</div>', unsafe_allow_html=True)

total_volume = df_agg["total_volume"].sum()
cluster_summary = (
    df_agg.groupby("cluster")
    .agg(
        pemohon=("PEMOHON", "count"),
        volume=("total_volume", "sum")
    )
)

cluster_summary["persen_volume"] = (
    cluster_summary["volume"] / total_volume * 100
).round(1)

dominant_cluster = cluster_summary["volume"].idxmax()

st.success(
    f"Segmen {dominant_cluster} menjadi kontributor utama "
    f"dengan {cluster_summary.loc[dominant_cluster, 'persen_volume']}% "
    "dari total volume aktivitas."
)


# ==================================================
# SECTION 2 — KARAKTERISTIK SEGMENTASI
# ==================================================
st.markdown('<div class="section-title">Karakteristik Utama Tiap Segmen</div>', unsafe_allow_html=True)

profil_sederhana = (
    df_agg.groupby("cluster")
    .agg(
        Rata_Volume=("total_volume", "mean"),
        Rata_Frekuensi=("total_transaksi", "mean"),
        Variasi_Aktivitas=("variasi_jenis_hpm", "mean")
    )
    .round(1)
)

st.dataframe(profil_sederhana, use_container_width=True)

for c in profil_sederhana.index:
    vol = profil_sederhana.loc[c, "Rata_Volume"]
    freq = profil_sederhana.loc[c, "Rata_Frekuensi"]

    if vol > profil_sederhana["Rata_Volume"].mean():
        st.success(
            f"Segmen {c}: Volume tinggi meski jumlah pemohon tidak dominan. "
            "Berpotensi berdampak besar."
        )
    else:
        st.info(
            f"Segmen {c}: Aktivitas relatif lebih kecil. "
            "Cocok untuk pembinaan dan peningkatan kapasitas."
        )


# ==================================================
# SECTION 3 — DISTRIBUSI PEMOHON
# ==================================================
import altair as alt

st.markdown('<div class="section-title">Distribusi Pemohon per Segmen</div>', unsafe_allow_html=True)

df_dist = (
    df_agg["cluster"]
    .value_counts()
    .reset_index()
)

df_dist.columns = ["Segmen", "Jumlah Pemohon"]
df_dist["Segmen"] = df_dist["Segmen"].astype(str)

chart = (
    alt.Chart(df_dist)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X("Segmen:N", title="Segmen Pemohon"),
        y=alt.Y("Jumlah Pemohon:Q", title="Jumlah Pemohon"),
        tooltip=["Segmen", "Jumlah Pemohon"],
        color=alt.Color("Segmen:N", legend=None)
    )
    .properties(height=350)
)

st.altair_chart(chart, use_container_width=True)

terbanyak = df_dist.loc[df_dist["Jumlah Pemohon"].idxmax(), "Segmen"]
tersedikit = df_dist.loc[df_dist["Jumlah Pemohon"].idxmin(), "Segmen"]

st.info(
    f"Segmen {terbanyak} memiliki jumlah pemohon terbanyak, "
    f"sementara segmen {tersedikit} relatif paling sedikit."
)



# ==================================================
# SECTION 4 — PEMOHON PRIORITAS
# ==================================================
st.markdown('<div class="section-title">Pemohon Prioritas</div>', unsafe_allow_html=True)

cluster_pilih = st.selectbox(
    "Pilih segmen untuk ditinjau:",
    sorted(df_agg["cluster"].unique())
)

top_pemohon = (
    df_agg[df_agg["cluster"] == cluster_pilih]
    .sort_values("total_volume", ascending=False)
    .head(10)
)

st.dataframe(
    top_pemohon[
        ["PEMOHON", "total_volume", "total_transaksi", "rata_volume_transaksi"]
    ],
    use_container_width=True
)

# ==================================================
# SECTION 5 — REKOMENDASI KEBIJAKAN
# ==================================================
st.markdown('<div class="section-title">Rekomendasi Kebijakan</div>', unsafe_allow_html=True)

rata_global = df_agg["total_volume"].mean()

for c in sorted(df_agg["cluster"].unique()):
    avg_vol = df_agg[df_agg["cluster"] == c]["total_volume"].mean()

    if avg_vol > rata_global:
        st.success(
            f"Segmen {c} menunjukkan aktivitas tinggi dan volume besar. "
            "Direkomendasikan sebagai prioritas layanan dan pengawasan rutin."
        )
    else:
        st.info(
            f"Segmen {c} memiliki skala aktivitas relatif lebih kecil. "
            "Cocok untuk program pembinaan dan peningkatan kapasitas."
        )

# ==================================================
