import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime
import sys

# Get location and sublocation from command line arguments
if len(sys.argv) < 3:
    print("Usage: python visualization.py <location> <sublocation>")
    sys.exit(1)

location = sys.argv[1]
sublocation = sys.argv[2]

# Define which data types are available for each location
station_config = {
    'biebrza': {'mscichy': ['hydro1', 'hydro2', 'meteo'],
                'szorce': ['hydro1', 'hydro2', 'meteo'],
                'zajki': ['hydro1', 'hydro2', 'meteo']},
    'beka': {'puck': ['hydro1', 'hydro2'],
            'wejherowo': ['meteo']},
    'swinoujscie': {'main': ['hydro1', 'hydro2', 'meteo']}
}

# Get the previous month's year and month
today = datetime.today()
first_day_this_month = datetime(today.year, today.month, 1)
last_day_prev_month = first_day_this_month - pd.Timedelta(days=1)
year = last_day_prev_month.year
month = last_day_prev_month.month

# Update file paths to include sublocation
base_filename = f'aggregated/aggregated_{location}_{sublocation}'
available_types = station_config.get(location, {}).get(sublocation, [])

# Load available data files
df_hydro1 = None
df_hydro2 = None
df_meteo = None

if 'hydro1' in available_types:
    try:
        df_hydro1 = pd.read_csv(f'{base_filename}_hydro1_{year}_{month:02d}.csv')
        df_hydro1['stan_wody_data_pomiaru'] = pd.to_datetime(df_hydro1['stan_wody_data_pomiaru'], errors='coerce')
    except FileNotFoundError:
        print(f"Hydro1 data file not found for {location}/{sublocation}")

if 'hydro2' in available_types:
    try:
        df_hydro2 = pd.read_csv(f'{base_filename}_hydro2_{year}_{month:02d}.csv')
    except FileNotFoundError:
        print(f"Hydro2 data file not found for {location}/{sublocation}")

if 'meteo' in available_types:
    try:
        df_meteo = pd.read_csv(f'{base_filename}_meteo_{year}_{month:02d}.csv')
        df_meteo['temperatura_gruntu_data'] = pd.to_datetime(df_meteo['temperatura_gruntu_data'], errors='coerce')
        df_meteo['wiatr_kierunek_data'] = pd.to_datetime(df_meteo['wiatr_kierunek_data'], errors='coerce')
        df_meteo['opad_10min_data'] = pd.to_datetime(df_meteo['opad_10min_data'], errors='coerce')
    except FileNotFoundError:
        print(f"Meteo data file not found for {location}/{sublocation}")

if not any([df_hydro1 is not None, df_meteo is not None]):
    print(f"No data files found for {location}/{sublocation}. Skipping visualization.")
    sys.exit(0)

# Create a folder for figures
os.makedirs('figures', exist_ok=True)

# Function to set x-axis properties for all plots
def set_monthly_xaxis(ax, year, month):
    # Get last day of the month
    next_month = pd.Timestamp(year=year, month=month, day=1) + pd.DateOffset(months=1)
    last_day = (next_month - pd.Timedelta(days=1)).day
    
    # Set x-axis limits to cover the full month
    ax.set_xlim(
        pd.Timestamp(year=year, month=month, day=1),
        pd.Timestamp(year=year, month=month, day=last_day, hour=23, minute=59)
    )
    
    # Set major ticks for each day
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d"))  # Show only day number
    ax.tick_params(axis='x', rotation=45, labelsize=12)
    
    # If it's the bottom subplot, add month-year label
    if ax.is_last_row():
        ax.set_xlabel(f'Dni ({year}-{month:02d})', fontsize=13)
    else:
        ax.set_xlabel('')

# Determine how many subplots we need based on available data
plot_configs = []
if df_meteo is not None:
    plot_configs.append(('wind', 'Prędkość i kierunek wiatru'))
if df_hydro1 is not None:
    plot_configs.append(('water', 'Poziom wody'))
if df_meteo is not None:
    plot_configs.append(('temp_rain', 'Temperatura i Opady'))

n_plots = len(plot_configs)
if n_plots == 0:
    print("No data to visualize")
    sys.exit(0)

# Create figure with appropriate number of subplots
fig, axes = plt.subplots(n_plots, 1, figsize=(16, 8*n_plots))
if n_plots == 1:
    axes = [axes]  # Make it iterable

# Create plots based on available data
for (plot_type, title), ax in zip(plot_configs, axes):
    if plot_type == 'wind' and df_meteo is not None:
        sns.lineplot(data=df_meteo, x='wiatr_kierunek_data', y='wiatr_srednia_predkosc', 
                    label='Prędkość wiatru', ax=ax)
        ax.quiver(
            df_meteo['wiatr_kierunek_data'], df_meteo['wiatr_srednia_predkosc'],
            df_meteo['wiatr_kierunek'].apply(lambda x: np.cos(np.deg2rad(x))),
            df_meteo['wiatr_kierunek'].apply(lambda x: np.sin(np.deg2rad(x))),
            scale=50, width=0.005, color='r'
        )
        ax.set_title(title, fontsize=16)
        ax.set_xlabel('Data', fontsize=13)
        ax.set_ylabel('Prędkość wiatru (km/h)', fontsize=13)
        
    elif plot_type == 'water' and df_hydro1 is not None:
        sns.lineplot(data=df_hydro1, x='stan_wody_data_pomiaru', y='stan_wody', 
                    label='Poziom wody', color='blue', ax=ax)
        ax.axhline(y=580, color='red', linestyle='--', linewidth=4, label='Poziom alarmowy')
        ax.axhline(y=560, color='yellow', linestyle='--', linewidth=4, label='Poziom ostrzegawczy')
        ax.set_title(title, fontsize=16)
        ax.set_xlabel('Data', fontsize=13)
        ax.set_ylabel('Poziom wody (cm)', fontsize=13)
        
    elif plot_type == 'temp_rain' and df_meteo is not None:
        ax.set_title(title, fontsize=16)
        ax.bar(df_meteo['opad_10min_data'], df_meteo['opad_10min'], 
               label='Opady', color='blue', alpha=0.6)
        ax.set_xlabel('Data', fontsize=13)
        ax.set_ylabel('Opady (mm)', fontsize=13, color='blue')
        ax.tick_params(axis='y', labelcolor='blue')
        
        ax2 = ax.twinx()
        sns.lineplot(data=df_meteo, x='temperatura_gruntu_data', y='temperatura_gruntu',
                    label='Temperatura gruntu', color='orange', ax=ax2)
        ax2.set_ylabel('Temperatura (°C)', fontsize=13, color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')
        
    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.tick_params(axis='x', rotation=45, labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    ax.legend(fontsize=12)
    set_monthly_xaxis(ax, year, month)

fig.suptitle(f'Dane pogodowe za {year}-{month:02d}\n{location.title()} - {sublocation.title()}', 
            fontsize=20, weight='bold')
fig.tight_layout(pad=3.08)
fig.subplots_adjust(top=0.95, bottom=0.07)

# Save the combined figure with location and sublocation in filename
fig.savefig(f'figures/weather_data_{location}_{sublocation}_{year}_{month:02d}.png')
plt.close()
