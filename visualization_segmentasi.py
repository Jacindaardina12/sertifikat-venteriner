# visualization_segmentasi.py

import streamlit as st
import numpy as np


def tampilkan_ringkasan(df):
    st.subheader("📌 Ringkasan Segmentasi")

    col1, col2, col3 = st.columns(3)

    col1.metric("Jumlah Entitas", df.shape[0])
    col2.metric("Jumlah Cluster", df['cluster'].nunique())
    col3.metric("Total Volume", int(df['total_volume'].sum()))


def tabel_segmentasi(df):
    st.subheader("📋 Tabel Hasil Segmentasi")
    st.dataframe(df, use_container_width=True)


def profil_cluster(df):
    st.subheader("📊 Profil Rata-rata Tiap Cluster")

    numerik = df.select_dtypes(include=[np.number])
    profil = numerik.groupby(df['cluster']).mean().round(2)

    st.dataframe(profil, use_container_width=True)


def top_entitas(df, kolom_id, top_n=10):
    st.subheader("🏆 Top Entitas Berdasarkan Volume")

    top = (
        df.sort_values('total_volume', ascending=False)
        .head(top_n)[[kolom_id, 'total_volume', 'cluster']]
    )

    st.dataframe(top, use_container_width=True)
