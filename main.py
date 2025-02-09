import requests
import logging
import csv
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Adres endpointu API
API_URL = "http://danepubliczne.imgw.pl/api/data/hydro/"
# Identyfikator stacji, dla której chcemy pobrać dane
STATION_ID = "153140010"

def pobierz_dane():
    """
    Pobiera dane z API (wszystkie stacje) i zwraca je jako listę słowników.
    """
    try:
        response = requests.get(API_URL)
        logging.info(f"Status code: {response.status_code}")
        response.raise_for_status()  # Upewnij się, że odpowiedź ma status 200 OK
        dane = response.json()
        logging.info("Dane pobrane pomyślnie.")
        return dane
    except requests.RequestException as e:
        logging.error(f"Błąd pobierania danych: {e}")
        return None

def filtruj_dane(dane, station_id):
    """
    Filtruje listę rekordów i zwraca rekord odpowiadający podanemu identyfikatorowi stacji.
    Jeśli rekord nie zostanie znaleziony, zwraca None.
    """
    if dane is None:
        return None

    for rekord in dane:
        if rekord.get("id_stacji") == station_id:
            return rekord

    logging.warning(f"Nie znaleziono danych dla stacji {station_id}.")
    return None

def zapisz_do_csv(dane):
    """
    Zapisuje dane (słownik) do pliku CSV.
    Nazwa pliku zawiera identyfikator stacji oraz aktualną datę i godzinę.
    """
    if dane is None:
        logging.warning("Brak danych do zapisania.")
        return

    # Ustala nazwę pliku z aktualną datą i godziną
    teraz = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nazwa_pliku = f"stacja_{STATION_ID}_{teraz}.csv"

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
    Główna funkcja: pobiera dane, filtruje rekord dla wybranej stacji i zapisuje je do CSV.
    """
    logging.info("Rozpoczynam pobieranie i zapis danych...")
    wszystkie_dane = pobierz_dane()
    stacja_dane = filtruj_dane(wszystkie_dane, STATION_ID)
    zapisz_do_csv(stacja_dane)

if __name__ == '__main__':
    # Jednorazowe uruchomienia zadania
    zadanie()
