import requests
import folium

API_URL = "http://127.0.0.1:8000/optimize"

# Dokładnie te same punkty, które przed chwilą testowałeś
payload = {
    "epsilon_km": 10.0,
    "min_samples": 3,
    "points": [
        {"id": "paczka_01", "lat": -23.550520, "lng": -46.633308},
        {"id": "paczka_02", "lat": -23.552010, "lng": -46.635010},
        {"id": "paczka_03", "lat": -23.548900, "lng": -46.638000},
        {"id": "paczka_04", "lat": -23.561000, "lng": -46.655000},
        {"id": "paczka_05", "lat": -23.563000, "lng": -46.657000}
    ]
}

print("Wysyłam zapytanie do lokalnego API...")
response = requests.post(API_URL, json=payload)
data = response.json()

if "routes" in data and "courier_0" in data["routes"]:
    ordered_ids = data["routes"]["courier_0"]
    print(f"Otrzymana kolejność: {ordered_ids}")

    # Słownik ułatwiający pobranie współrzędnych na podstawie ID
    points_dict = {p["id"]: (p["lat"], p["lng"]) for p in payload["points"]}
    ordered_coords = [points_dict[pid] for pid in ordered_ids]

    # Tworzymy mapę wycentrowaną na pierwszym punkcie z trasy
    m = folium.Map(location=ordered_coords[0], zoom_start=14)

    # Dodajemy punkty na mapę
    for i, (pid, coord) in enumerate(zip(ordered_ids, ordered_coords)):
        folium.Marker(
            location=coord,
            popup=f"Stop {i + 1}: {pid}",
            icon=folium.Icon(color="red" if i == 0 else "blue", icon="info-sign")
        ).add_to(m)

    # Rysujemy czerwoną linię pokazującą trasę przejazdu
    folium.PolyLine(ordered_coords, color="red", weight=3, opacity=0.8).add_to(m)

    # Zapis
    m.save("route_map.html")
    print("Sukces! Wygenerowano plik route_map.html w głównym folderze.")
else:
    print("Błąd lub brak trasy w odpowiedzi z API:", data)