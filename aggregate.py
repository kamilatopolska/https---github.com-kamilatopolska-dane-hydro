import os
import pandas as pd
from datetime import datetime
import subprocess

# Folder, w którym zapisywane są CSV
folder = 'data'

# Define locations and their sublocations
LOCATIONS = {
    'biebrza': ['mscichy', 'szorce', 'zajki'],
    'beka': ['puck', 'wejherowo'],
    'swinoujscie': ['main']
}

# Ustalenie poprzedniego miesiąca
today = datetime.today()
first_day_this_month = datetime(today.year, today.month, 1)
last_day_prev_month = first_day_this_month - pd.Timedelta(days=1)
year = last_day_prev_month.year
month = last_day_prev_month.month

def file_in_previous_month(filename):
    try:
        parts = filename.split('_')
        if len(parts) < 4:
            return False
        date_part = parts[-1].split('.')[0]  # Get date part before .csv
        file_date = datetime.strptime(date_part, '%Y-%m-%d_%H-%M-%S')
        return file_date.year == year and file_date.month == month
    except Exception as e:
        return False

def aggregate_files_for_location(location, sublocation):
    # Lista plików CSV w folderze dla danej lokalizacji i sublokalizacji
    csv_files = [f for f in os.listdir(folder) 
                 if f.startswith(f"{location}_{sublocation}") and f.endswith('.csv')]

    # Filtruj pliki dla każdego źródła
    files_to_aggregate_hydro1 = [os.path.join(folder, f) for f in csv_files if 'hydro1' in f and file_in_previous_month(f)]
    files_to_aggregate_hydro2 = [os.path.join(folder, f) for f in csv_files if 'hydro2' in f and file_in_previous_month(f)]
    files_to_aggregate_meteo = [os.path.join(folder, f) for f in csv_files if 'meteo' in f and file_in_previous_month(f)]

    os.makedirs('aggregated', exist_ok=True)

    def aggregate_files(files_to_aggregate, output_filename):
        if not files_to_aggregate:
            print(f"Nie znaleziono plików CSV dla poprzedniego miesiąca dla {output_filename}.")
            return False

        df_list = [pd.read_csv(file) for file in files_to_aggregate]
        df_aggregated = pd.concat(df_list, ignore_index=True)
        df_aggregated.to_csv(output_filename, index=False)
        print(f"Zbiorczy plik CSV zapisany jako {output_filename}")
        return True

    # Agreguj pliki dla każdego źródła
    base_filename = f'aggregated/aggregated_{location}_{sublocation}'
    files_created = []
    
    if aggregate_files(files_to_aggregate_hydro1, f'{base_filename}_hydro1_{year}_{month:02d}.csv'):
        files_created.append('hydro1')
    if aggregate_files(files_to_aggregate_hydro2, f'{base_filename}_hydro2_{year}_{month:02d}.csv'):
        files_created.append('hydro2')
    if aggregate_files(files_to_aggregate_meteo, f'{base_filename}_meteo_{year}_{month:02d}.csv'):
        files_created.append('meteo')

    if files_created:
        # Generate visualization for this location and sublocation
        subprocess.run(["python", "visualization.py", location, sublocation], check=True)

# Aggregate for each location and sublocation
for location, sublocations in LOCATIONS.items():
    for sublocation in sublocations:
        aggregate_files_for_location(location, sublocation)
