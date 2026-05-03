import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import mlflow
import mlflow.sklearn
import os
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math

# Konfiguracja ścieżek (zakładamy, że uruchamiamy z głównego folderu projektu)
DATA_PATH = "data/processed/sao_paulo_deliveries.csv"


def train_clustering_model(epsilon_km: float, min_samples: int, sample_size: int = 15000):
    # Konfiguracja MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("last_mile_clustering")

    print("Ładowanie danych...")
    df = pd.read_csv(DATA_PATH)

    coords = df[['geolocation_lat', 'geolocation_lng']].dropna().values[:sample_size]

    with mlflow.start_run():
        print(f"Start eksperymentu z parametrami: eps={epsilon_km}km, min_samples={min_samples}")

        # Logowanie hiperparametrów do MLflow
        mlflow.log_param("epsilon_km", epsilon_km)
        mlflow.log_param("min_samples", min_samples)
        mlflow.log_param("sample_size", sample_size)

        # Promień Ziemi w kilometrach
        KILOMETERS_PER_RADIAN = 6371.0088
        eps_rad = epsilon_km / KILOMETERS_PER_RADIAN
        coords_rad = np.radians(coords)

        print("Trenowanie modelu DBSCAN...")
        dbscan = DBSCAN(eps=eps_rad, min_samples=min_samples, algorithm='ball_tree', metric='haversine')
        labels = dbscan.fit_predict(coords_rad)

        # Szum w DBSCAN jest oznaczany jako -1. To paczki zbyt odosobnione na standardowy rewir.
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)
        noise_ratio = n_noise / len(labels)

        # Logowanie metryk do MLflow
        mlflow.log_metric("n_clusters", n_clusters)
        mlflow.log_metric("noise_points", n_noise)
        mlflow.log_metric("noise_ratio", noise_ratio)

        print(f"Zakończono. Znaleziono {n_clusters} rewirów.")
        print(f"Odrzucono {n_noise} paczek jako szum ({noise_ratio:.1%}).")

        mlflow.sklearn.log_model(dbscan, "dbscan_model")
        print("Model zapisany w MLflow.")

        print("\nWyliczanie optymalnej trasy (TSP) dla klastra nr 0...")

        # Pobieramy współrzędne paczek, które trafiły do klastra nr 0
        cluster_0_indices = np.where(labels == 0)[0]
        cluster_0_coords = coords[cluster_0_indices]

        if len(cluster_0_coords) > 2:  # Trasa ma sens dla minimum 3 punktów
            # 1. Obliczamy macierz odległości w metrach
            dist_matrix = calculate_distance_matrix(cluster_0_coords)

            route_indices = solve_tsp(dist_matrix)

            if route_indices:
                print(f"Sukces! Wyznaczono trasę z {len(route_indices)} punktami.")
                print(f"Kolejność indeksów do odwiedzenia: {route_indices}")


                mlflow.log_dict({"route_indices": route_indices}, "sample_route_cluster_0.json")
            else:
                print("Solver nie potrafił wyznaczyć trasy dla tego klastra.")

def calculate_distance_matrix(coordinates):
    """Oblicza macierz odległości Haversine między wszystkimi punktami klastra (wynik w metrach)"""
    n = len(coordinates)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                # Oczekuje współrzędnych w radianach
                coords_rad = np.radians([coordinates[i], coordinates[j]])
                from sklearn.metrics.pairwise import haversine_distances
                dist_rad = haversine_distances([coords_rad[0]], [coords_rad[1]])[0][0]
                matrix[i][j] = dist_rad * 6371000  # Promień Ziemi w metrach
    return matrix.astype(int)

def solve_tsp(distance_matrix):
    """Rozwiązuje problem komiwojażera dla danej macierzy odległości."""
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        index = routing.Start(0)
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        return route
    return None
if __name__ == "__main__":
    # Zakładamy, że klaster to minimum min_samples paczek oddalonych od siebie o max eps_km km
    train_clustering_model(epsilon_km=10.0, min_samples=10)