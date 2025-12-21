# insight_segmentasi.py

import streamlit as st


def tampilkan_insight(df):
    st.subheader("🧠 Insight Segmentasi")

    summary = (
        df.groupby('cluster')
        .mean(numeric_only=True)
        .reset_index()
    )

    cluster_tinggi = summary.loc[
        summary['total_volume'].idxmax(), 'cluster'
    ]
    cluster_rendah = summary.loc[
        summary['total_volume'].idxmin(), 'cluster'
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.success(f"🔥 Cluster Aktivitas Tertinggi: {int(cluster_tinggi)}")
        st.caption("Memiliki rata-rata volume paling besar")

    with col2:
        st.warning(f"💤 Cluster Aktivitas Terendah: {int(cluster_rendah)}")
        st.caption("Memiliki rata-rata volume paling kecil")

    st.divider()

    st.markdown("### 📌 Kesimpulan Umum")
    st.markdown(
        """
        Segmentasi menunjukkan perbedaan pola aktivitas antar cluster
        yang dapat digunakan sebagai dasar pengambilan kebijakan dan prioritas layanan.
        """
    )
