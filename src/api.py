from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
from sklearn.cluster import DBSCAN

from src.model import calculate_distance_matrix, solve_tsp

app = FastAPI(title="Last Mile Optimizer API", version="0.1.0")


class DeliveryPoint(BaseModel):
    id: str
    lat: float
    lng: float


class OptimizationRequest(BaseModel):
    points: List[DeliveryPoint]
    epsilon_km: float = 2.0
    min_samples: int = 5


@app.post("/optimize")
def optimize_routes(request: OptimizationRequest):
    if len(request.points) < 3:
        raise HTTPException(status_code=400, detail="Wymagane minimum 3 punkty.")

    coords = np.array([[p.lat, p.lng] for p in request.points])

    # Klastrowanie
    KILOMETERS_PER_RADIAN = 6371.0088
    eps_rad = request.epsilon_km / KILOMETERS_PER_RADIAN
    dbscan = DBSCAN(eps=eps_rad, min_samples=request.min_samples, algorithm='ball_tree', metric='haversine')
    labels = dbscan.fit_predict(np.radians(coords))

    response = {"routes": {}, "unassigned_noise": []}
    unique_clusters = set(labels)

    # Wyznaczanie tras dla klastrów
    for cluster_id in unique_clusters:
        cluster_indices = np.where(labels == cluster_id)[0]

        if cluster_id == -1:
            response["unassigned_noise"] = [request.points[i].id for i in cluster_indices]
            continue

        cluster_coords = coords[cluster_indices]
        dist_matrix = calculate_distance_matrix(cluster_coords)
        route_order = solve_tsp(dist_matrix)

        if route_order:
            ordered_points = [request.points[cluster_indices[idx]].id for idx in route_order]
            response["routes"][f"courier_{cluster_id}"] = ordered_points
        else:
            response["routes"][f"courier_{cluster_id}"] = []

    return response