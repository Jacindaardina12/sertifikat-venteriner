# clustering_segmentasi.py

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def scaling_data(df, fitur):
    """
    Melakukan scaling data numerik
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[fitur])
    return X_scaled, scaler


def train_kmeans(X_scaled, n_clusters):
    """
    Melatih model K-Means
    """
    model = KMeans(n_clusters=n_clusters, random_state=42)
    labels = model.fit_predict(X_scaled)
    return model, labels
