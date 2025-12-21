# evaluation_segmentasi.py

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def elbow_method(X_scaled, k_range):
    inertia = []
    for k in k_range:
        model = KMeans(n_clusters=k, random_state=42)
        model.fit(X_scaled)
        inertia.append(model.inertia_)
    return inertia


def silhouette_scores(X_scaled, k_range):
    scores = []
    for k in k_range:
        model = KMeans(n_clusters=k, random_state=42)
        labels = model.fit_predict(X_scaled)
        scores.append(silhouette_score(X_scaled, labels))
    return scores
