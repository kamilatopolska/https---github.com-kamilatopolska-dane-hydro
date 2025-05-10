import requests
import logging
import csv
import os
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Adresy endpointów API
API_URLS = {
    "hydro1": "http://danepubliczne.imgw.pl/api/data/hydro/",
    "hydro2": "http://danepubliczne.imgw.pl/api/data/hydro2/",
    "meteo": "http://danepubliczne.imgw.pl/api/data/meteo/"
}

# Grupowanie identyfikatorów stacji według lokalizacji
LOCATIONS = {
    "biebrza": {
        "mscichy": {
            "hydro1": "153220100",
            "hydro2": "153220100",
            "meteo": "253220130"
        },
        "szorce": {
            "hydro1": "153220100",
            "hydro2": "153220100",
            "meteo": "253220160"
        },
        "zajki": {
            "hydro1": "153220130",
            "hydro2": "153220130",
            "meteo": "253220210"
        }
    },
    "beka": {
        "puck": {
            "hydro1": "154180090",
            "hydro2": "154180090"
        },
        "wejherowo": {
            "meteo": "254180050"
        }
    },
    "swinoujscie": {
        "main": {
            "hydro1": "153140010",
            "hydro2": "153140010",
            "meteo": "353140200"
        }
    }
}

def pobierz_dane(api_url):
    """
    Pobiera dane z API i zwraca je jako listę słowników.
    """
    try:
        response = requests.get(api_url)
        logging.info(f"Status code: {response.status_code}")
        response.raise_for_status()  # Upewnij się, że odpowiedź ma status 200 OK
        dane = response.json()
        logging.info("Dane pobrane pomyślnie.")
        return dane
    except requests.RequestException as e:
        logging.error(f"Błąd pobierania danych: {e}")
        return None

def filtruj_dane(dane, station_id, key):
    """
    Filtruje listę rekordów i zwraca rekord odpowiadający podanemu identyfikatorowi stacji.
    Jeśli rekord nie zostanie znaleziony, zwraca None.
    """
    if dane is None:
        return None

    for rekord in dane:
        if rekord.get(key) == station_id:
            return rekord

    logging.warning(f"Nie znaleziono danych dla stacji {station_id}.")
    return None

def zapisz_do_csv(dane, station_id, prefix, location, substation):
    """
    Zapisuje dane (słownik) do pliku CSV.
    Nazwa pliku zawiera lokalizację, podstację, identyfikator stacji oraz aktualną datę i godzinę.
    """
    if dane is None:
        logging.warning("Brak danych do zapisania.")
        return

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Ustala nazwę pliku z aktualną datą i godziną
    teraz = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nazwa_pliku = os.path.join('data', f"{location}_{substation}_{prefix}_stacja_{station_id}_{teraz}.csv")

    try:
        with open(nazwa_pliku, mode='w', encoding='utf-8', newline='') as csvfile:
            fieldnames = list(dane.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(dane)
        logging.info(f"Dane zapisane do pliku: {nazwa_pliku}")
    except Exception as e:
        logging.error(f"Błąd podczas zapisu do pliku CSV: {e}")

def pobierz_dane_dla_stacji(location_name, substation_name, station_config):
    """
    Pobiera dane dla podanej lokalizacji i podstacji, a następnie zapisuje je do plików CSV.
    """
    for data_type, station_id in station_config.items():
        dane = pobierz_dane(API_URLS[data_type])
        key = "id_stacji" if data_type == "hydro1" else "kod_stacji"
        stacja_dane = filtruj_dane(dane, station_id, key)
        zapisz_do_csv(stacja_dane, station_id, data_type, location_name, substation_name)

def zadanie():
    """
    Główna funkcja: iteruje przez lokalizacje i podstacje, pobiera dane i zapisuje je do CSV.
    """
    logging.info("Rozpoczynam pobieranie i zapis danych...")
    
    for location_name, substations in LOCATIONS.items():
        for substation_name, station_config in substations.items():
            logging.info(f"Pobieranie danych dla lokalizacji {location_name} - {substation_name}")
            pobierz_dane_dla_stacji(location_name, substation_name, station_config)

if __name__ == '__main__':
    # Jednorazowe uruchomienia zadania
    zadanie()
