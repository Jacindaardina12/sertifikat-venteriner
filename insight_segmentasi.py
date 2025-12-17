import streamlit as st

def tampilkan_insight(df):
    st.subheader("🧠 Insight Segmentasi")

    summary = (
        df.groupby('cluster')
        .agg(
            rata_volume=('total_volume', 'mean'),
            rata_frekuensi=('frekuensi', 'mean')
        )
        .reset_index()
    )

    cluster_tinggi = summary.loc[summary['rata_volume'].idxmax(), 'cluster']
    cluster_rendah = summary.loc[summary['rata_volume'].idxmin(), 'cluster']

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔥 Aktivitas Tertinggi")
        st.success(f"Cluster {int(cluster_tinggi)}")
        st.caption("Wilayah dengan volume pemasukan paling besar")

    with col2:
        st.markdown("### 💤 Aktivitas Terendah")
        st.warning(f"Cluster {int(cluster_rendah)}")
        st.caption("Wilayah dengan aktivitas pemasukan rendah")

    st.divider()

    st.markdown("### 📍 Wilayah Dominan per Cluster")

    for c in sorted(df['cluster'].unique()):
        wilayah = (
            df[df['cluster'] == c]
            .sort_values('total_volume', ascending=False)
            .iloc[:5, 0]
            .tolist()
        )

        st.markdown(f"""
**Cluster {c}**  
<span style="color:#9ef0c3">{", ".join(wilayah)}</span>
""", unsafe_allow_html=True)
