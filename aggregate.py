import os
import pandas as pd
from datetime import datetime
import subprocess

# Folder, w którym zapisywane są CSV
folder = 'data'

# Ustalenie poprzedniego miesiąca
today = datetime.today()
first_day_this_month = datetime(today.year, today.month, 1)
last_day_prev_month = first_day_this_month - pd.Timedelta(days=1)
year = last_day_prev_month.year
month = last_day_prev_month.month

# Lista plików CSV w folderze
csv_files = [f for f in os.listdir(folder) if f.endswith('.csv')]

def file_in_previous_month(filename):
    try:
        # Rozdziel nazwę pliku po znaku '_' i pobierz trzeci element
        parts = filename.split('_')
        if len(parts) < 4:
            return False
        date_part = parts[3]  # oczekujemy formatu YYYY-MM-DD
        file_date = datetime.strptime(date_part, '%Y-%m-%d')
        return file_date.year == year and file_date.month == month
    except Exception as e:
        return False

# Filtruj pliki dla każdego źródła
files_to_aggregate_hydro1 = [os.path.join(folder, f) for f in csv_files if (f.startswith('hydro1') or f.startswith('stacja')) and file_in_previous_month(f)]
files_to_aggregate_hydro2 = [os.path.join(folder, f) for f in csv_files if f.startswith('hydro2') and file_in_previous_month(f)]
files_to_aggregate_meteo = [os.path.join(folder, f) for f in csv_files if f.startswith('meteo') and file_in_previous_month(f)]

def aggregate_files(files_to_aggregate, output_filename):
    if not files_to_aggregate:
        print(f"Nie znaleziono plików CSV dla poprzedniego miesiąca dla {output_filename}.")
        return

    # Wczytanie i połączenie danych
    df_list = [pd.read_csv(file) for file in files_to_aggregate]
    df_aggregated = pd.concat(df_list, ignore_index=True)

    # Zapisanie zbiorczego pliku
    df_aggregated.to_csv(output_filename, index=False)
    print(f"Zbiorczy plik CSV zapisany jako {output_filename}")

# Agreguj pliki dla każdego źródła
os.makedirs('aggregated', exist_ok=True)
aggregate_files(files_to_aggregate_hydro1, f'aggregated/aggregated_hydro1_{year}_{month:02d}.csv')
aggregate_files(files_to_aggregate_hydro2, f'aggregated/aggregated_hydro2_{year}_{month:02d}.csv')
aggregate_files(files_to_aggregate_meteo, f'aggregated/aggregated_meteo_{year}_{month:02d}.csv')

# Run the visualization script
subprocess.run(["python", "visualization.py"], check=True)
