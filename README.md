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

---

## Getting Started

### Prerequisites
Before you begin, ensure you have the following installed on your machine:
* **Git** (to download the code)
* **Docker Desktop** (if choosing the Docker method)
* **Python 3.9+** and **Poetry** (if choosing the Local Development method)

### Step 1: Get the Code
Open your terminal and run the following commands to clone the repository and navigate into the project folder:

```bash
git clone https://github.com/gr4b0wski/last_mile_optimizer.git
cd last_mile_optimizer
```

### Step 2: Choose Your Execution Method

#### Option A: Quick Start (Docker - Recommended)
The fastest way to run the optimizer without worrying about local dependencies. Ensure Docker Desktop is running in the background.

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

#### Option B: Local Development (Poetry)
Ideal if you want to modify the code, run experiments, or view the MLflow dashboard.

1. **Install all dependencies:**
   ```bash
   poetry install
   ```
2. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```
3. **Run the MLflow tracking server:**
   ```bash
   mlflow ui --backend-store-uri sqlite:///mlflow.db
   ```
   *Note: The MLflow dashboard is now running at `http://127.0.0.1:5000`. This terminal is now blocked.*
4. **Run the FastAPI server (Open a NEW terminal tab):**
   Open a second terminal window, navigate back to the project folder (`cd last-mile-optimizer`), and start the API:
   ```bash
   poetry run uvicorn src.api:app --reload
   ```

---

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

You can generate an interactive visual map of the optimized routes using Folium. The command depends on how you are running the project.

### Option A: If using Docker
Since the application is isolated inside a container, you need to execute the script inside it and extract the generated HTML file. Open a **new terminal tab** and run:

1. **Find your running container ID:**
   docker ps

2. **Run the visualization script inside the container** (replace <CONTAINER_ID> with the actual ID from the previous step):
   docker exec -it <CONTAINER_ID> python src/visualize.py

3. **Copy the generated map to your local machine:**
   docker cp <CONTAINER_ID>:/app/route_map.html .

### Option B: If using Poetry
In a **new terminal tab** (while the FastAPI server is running in the first one), execute:
   poetry run python src/visualize.py

**Result:** Both methods will generate a route_map.html file in your root project directory. Double-click it to open the interactive map in any web browser.
