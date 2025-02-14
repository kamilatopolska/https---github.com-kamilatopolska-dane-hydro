import requests
import logging
import csv
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Adresy endpointów API
API_URLS = {
    "hydro1": "http://danepubliczne.imgw.pl/api/data/hydro/",
    "hydro2": "http://danepubliczne.imgw.pl/api/data/hydro2/",
    "meteo": "http://danepubliczne.imgw.pl/api/data/meteo/"
}

# Identyfikatory stacji
STATION_IDS = {
    "hydro1": "153140010",
    "hydro2": "153140010",
    "meteo": "353140200"
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

def zapisz_do_csv(dane, station_id, prefix):
    """
    Zapisuje dane (słownik) do pliku CSV.
    Nazwa pliku zawiera identyfikator stacji oraz aktualną datę i godzinę.
    """
    if dane is None:
        logging.warning("Brak danych do zapisania.")
        return

    # Ustala nazwę pliku z aktualną datą i godziną
    teraz = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nazwa_pliku = f"{prefix}_stacja_{station_id}_{teraz}.csv"

    try:
        with open(nazwa_pliku, mode='w', encoding='utf-8', newline='') as csvfile:
            # Ustala nagłówki kolumn na podstawie kluczy słownika
            fieldnames = list(dane.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(dane)
        logging.info(f"Dane zapisane do pliku: {nazwa_pliku}")
    except Exception as e:
        logging.error(f"Błąd podczas zapisu do pliku CSV: {e}")

def zadanie():
    """
    Główna funkcja: pobiera dane, filtruje rekordy dla wybranych stacji i zapisuje je do CSV.
    """
    logging.info("Rozpoczynam pobieranie i zapis danych...")

    # Pobierz i zapisz dane dla hydro1
    dane_hydro1 = pobierz_dane(API_URLS["hydro1"])
    stacja_dane_hydro1 = filtruj_dane(dane_hydro1, STATION_IDS["hydro1"], "id_stacji")
    zapisz_do_csv(stacja_dane_hydro1, STATION_IDS["hydro1"], "hydro1")

    # Pobierz i zapisz dane dla hydro2
    dane_hydro2 = pobierz_dane(API_URLS["hydro2"])
    stacja_dane_hydro2 = filtruj_dane(dane_hydro2, STATION_IDS["hydro2"], "kod_stacji")
    zapisz_do_csv(stacja_dane_hydro2, STATION_IDS["hydro2"], "hydro2")

    # Pobierz i zapisz dane dla meteo
    dane_meteo = pobierz_dane(API_URLS["meteo"])
    stacja_dane_meteo = filtruj_dane(dane_meteo, STATION_IDS["meteo"], "kod_stacji")
    zapisz_do_csv(stacja_dane_meteo, STATION_IDS["meteo"], "meteo")

if __name__ == '__main__':
    # Jednorazowe uruchomienia zadania
    zadanie()
