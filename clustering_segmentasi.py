# clustering_segmentasi.py

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def kmeans_segmentasi(df, n_clusters=3):
    """
    Melakukan clustering K-Means
    """
    fitur = df.select_dtypes(include='number')


    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(fitur)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    return df
