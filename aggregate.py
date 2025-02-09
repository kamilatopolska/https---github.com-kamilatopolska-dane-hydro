import os
import pandas as pd
from datetime import datetime

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
        if len(parts) < 3:
            return False
        date_part = parts[2]  # oczekujemy formatu YYYY-MM-DD
        file_date = datetime.strptime(date_part, '%Y-%m-%d')
        return file_date.year == year and file_date.month == month
    except Exception as e:
        return False

files_to_aggregate = [os.path.join(folder, f) for f in csv_files if file_in_previous_month(f)]

if not files_to_aggregate:
    print("Nie znaleziono plików CSV dla poprzedniego miesiąca.")
    exit(0)

# Wczytanie i połączenie danych
df_list = [pd.read_csv(file) for file in files_to_aggregate]
df_aggregated = pd.concat(df_list, ignore_index=True)

# Zapisanie zbiorczego pliku
output_filename = f'aggregated_{year}_{month:02d}.csv'
df_aggregated.to_csv(output_filename, index=False)
print(f"Zbiorczy plik CSV zapisany jako {output_filename}")
