# Używamy lekkiej, stabilnej wersji Pythona
FROM python:3.12-slim

# Ustawiamy katalog roboczy wewnątrz kontenera
WORKDIR /app

# Instalacja Poetry
RUN pip install poetry==2.0.0

# Kopiujemy pliki konfiguracyjne środowiska
COPY pyproject.toml poetry.lock ./

# Wyłączamy tworzenie środowiska wirtualnego (w Dockerze to niepotrzebne) i instalujemy pakiety
RUN poetry config virtualenvs.create false && poetry install --no-root

# Kopiujemy resztę kodu
COPY src/ ./src/

# Informujemy, na jakim porcie będzie działać API
EXPOSE 8000

# Komenda uruchamiająca serwer API
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]