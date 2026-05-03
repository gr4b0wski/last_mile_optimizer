# Last Mile Optimizer: Machine Learning Delivery Routing System

An end-to-end Machine Learning pipeline and REST API designed to solve the Last-Mile Delivery routing problem. The system groups unstructured delivery coordinates into optimized courier territories and calculates the shortest possible delivery paths.

Built with production-grade **MLOps** standards, ensuring reproducibility, scalability, and strict environment management.

## Core Algorithms
The core optimization engine relies on a two-step mathematical approach:
1. **Territory Clustering (Scikit-Learn / DBSCAN):** Density-Based Spatial Clustering of Applications with Noise (DBSCAN) utilizes the Haversine distance metric to group geographically close packages into distinct delivery territories, automatically flagging isolated packages as "noise" to avoid unprofitable detours.
2. **Route Optimization (Google OR-Tools):** Solves the Traveling Salesperson Problem (TSP) by building a precise distance matrix for each generated territory and computing the optimal sequence of stops for the courier.

## Architecture & Tech Stack
This project mimics a real-world enterprise ML infrastructure:
* **Dependency Management:** `Poetry` ensures absolute deterministic builds via `poetry.lock`, resolving "dependency hell".
* **Data Versioning:** `DVC` (Data Version Control) separates code from large datasets (like `sao_paulo_deliveries.csv`), managing data states without bloating the Git repository.
* **Experiment Tracking:** `MLflow` tracks hyperparameter tuning (`epsilon_km`, `min_samples`) against business metrics (`noise_ratio`, `n_clusters`), allowing for data-driven model evaluation.
* **Serving Layer:** `FastAPI` exposes the ML models as a high-performance REST API.
* **Containerization:** `Docker` encapsulates the OS, Python environment, and dependencies, guaranteeing a true "run-anywhere" deployment.


## Quick Start (Docker)

The fastest way to run the optimizer is via Docker. Ensure Docker Desktop is running.

1. **Build the image:**
   ```bash
   docker build -t last-mile-api .
   
```
2. **Run the container:**
   ```bash
   docker run -p 8000:8000 last-mile-api
   
```
3. **Access the API Documentation:**
   Open `http://127.0.0.1:8000/docs` in your browser to use the interactive Swagger UI.

## Local Development (Poetry)

1. **Install dependencies:**
   ```bash
   poetry install
   
```
2. **Activate the environment:**
   ```bash
   poetry env activate
   ```
3. **Run MLflow tracking server (optional):**
   
```bash
   mlflow ui --backend-store-uri sqlite:///mlflow.db
   ```
4. **Run the FastAPI server:**
   ```bash
   poetry run uvicorn src.api:app --reload
   ```

## API Usage Example

**Endpoint:** `POST /optimize`

**Payload:**
```json
{
  "epsilon_km": 1.5,
  "min_samples": 3,
  "points": [
    {"id": "pkg_01", "lat": -23.550520, "lng": -46.633308},
    {"id": "pkg_02", "lat": -23.552010, "lng": -46.635010},
    {"id": "pkg_03", "lat": -23.548900, "lng": -46.638000}
  ]
}
```

**Response:**
```json
{
  "routes": {
    "courier_0": [
      "pkg_01",
      "pkg_02",
      "pkg_03"
    ]
  },
  "unassigned_noise": []
}
```

## Visualization
Run the visualization script to test the API and generate an interactive `route_map.html` using Folium:
```bash
poetry run python src/visualize.py
```
