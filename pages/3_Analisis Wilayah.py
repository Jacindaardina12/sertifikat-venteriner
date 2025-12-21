# pages/segmentasi.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from clustering_segmentasi import scaling_data, train_kmeans
from evaluation_segmentasi import elbow_method, silhouette_scores
from visualization_segmentasi import (
    tampilkan_ringkasan,
    tabel_segmentasi,
    profil_cluster,
    top_entitas
)
from insight_segmentasi import tampilkan_insight

from sklearn.decomposition import PCA


st.title("📊 Proses Segmentasi Pemohon (End-to-End)")

# =========================
# LOAD DATA (CONTOH)
# =========================
# df_agg HARUS sudah berupa data agregasi
# contoh kolom: PEMOHON, total_volume, total_transaksi, variasi_jenis_hpm

df_agg = st.session_state.get("df_segmentasi")

if df_agg is None:
    st.warning("Data segmentasi belum dimuat.")
    st.stop()

kolom_id = "PEMOHON"

# =========================
# 1. PEMILIHAN FITUR
# =========================
st.subheader("1️⃣ Pemilihan Fitur")

fitur_opsi = df_agg.select_dtypes(include="number").columns.tolist()
fitur = st.multiselect(
    "Pilih fitur untuk segmentasi:",
    fitur_opsi,
    default=fitur_opsi
)

# =========================
# 2. SCALING
# =========================
st.subheader("2️⃣ Scaling Data")

X_scaled, scaler = scaling_data(df_agg, fitur)
st.success("Scaling berhasil dilakukan")

# =========================
# 3. EVALUASI CLUSTER
# =========================
st.subheader("3️⃣ Evaluasi Jumlah Cluster")

k_range = range(2, 7)
inertia = elbow_method(X_scaled, k_range)
silhouette = silhouette_scores(X_scaled, k_range)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Elbow Method**")
    fig, ax = plt.subplots()
    ax.plot(list(k_range), inertia, marker="o")
    ax.set_xlabel("Jumlah Cluster (k)")
    ax.set_ylabel("Inertia")
    st.pyplot(fig)

with col2:
    st.markdown("**Silhouette Score**")
    fig, ax = plt.subplots()
    ax.plot(list(k_range), silhouette, marker="o")
    ax.set_xlabel("Jumlah Cluster (k)")
    ax.set_ylabel("Silhouette Score")
    st.pyplot(fig)

# =========================
# 4. MODEL FINAL
# =========================
st.subheader("4️⃣ Model K-Means Final")

k = st.slider("Pilih jumlah cluster terbaik:", 2, 6, 3)

model, labels = train_kmeans(X_scaled, k)
df_agg["cluster"] = labels

# =========================
# 5. PCA VISUALIZATION
# =========================
st.subheader("5️⃣ Visualisasi PCA")

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

df_pca = pd.DataFrame(X_pca, columns=["PC1", "PC2"])
df_pca["cluster"] = df_agg["cluster"]

fig, ax = plt.subplots()
scatter = ax.scatter(
    df_pca["PC1"],
    df_pca["PC2"],
    c=df_pca["cluster"],
    cmap="tab10"
)
ax.set_xlabel("PC1")
ax.set_ylabel("PC2")
st.pyplot(fig)

# =========================
# 6. HASIL & INSIGHT
# =========================
tampilkan_ringkasan(df_agg)
tabel_segmentasi(df_agg)
profil_cluster(df_agg)
top_entitas(df_agg, kolom_id)
tampilkan_insight(df_agg)
