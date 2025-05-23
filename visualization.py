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

# Get the previous month's year and month
today = datetime.today()
first_day_this_month = datetime(today.year, today.month, 1)
last_day_prev_month = first_day_this_month - pd.Timedelta(days=1)
year = last_day_prev_month.year
month = last_day_prev_month.month

# Update file paths to include sublocation
base_filename = f'aggregated/aggregated_{location}_{sublocation}'
try:
    df_hydro1 = pd.read_csv(f'{base_filename}_hydro1_{year}_{month:02d}.csv')
    df_hydro2 = pd.read_csv(f'{base_filename}_hydro2_{year}_{month:02d}.csv')
    df_meteo = pd.read_csv(f'{base_filename}_meteo_{year}_{month:02d}.csv')
except FileNotFoundError as e:
    print(f"Some data files not found for {location}/{sublocation}. Skipping visualization.")
    sys.exit(0)

# Convert date columns to datetime
df_hydro1['stan_wody_data_pomiaru'] = pd.to_datetime(df_hydro1['stan_wody_data_pomiaru'], errors='coerce')
df_meteo['temperatura_gruntu_data'] = pd.to_datetime(df_meteo['temperatura_gruntu_data'], errors='coerce')
df_meteo['wiatr_kierunek_data'] = pd.to_datetime(df_meteo['wiatr_kierunek_data'], errors='coerce')
df_meteo['opad_10min_data'] = pd.to_datetime(df_meteo['opad_10min_data'], errors='coerce')

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

# Create a single figure with three subplots stacked vertically
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 24))

# Plot 1: Wind Speed and Direction Over Time
sns.lineplot(data=df_meteo, x='wiatr_kierunek_data', y='wiatr_srednia_predkosc', label='Prędkość wiatru', ax=ax1)
ax1.quiver(
    df_meteo['wiatr_kierunek_data'], df_meteo['wiatr_srednia_predkosc'],
    df_meteo['wiatr_kierunek'].apply(lambda x: np.cos(np.deg2rad(x))),
    df_meteo['wiatr_kierunek'].apply(lambda x: np.sin(np.deg2rad(x))),
    scale=50, width=0.005, color='r'
)
ax1.set_title('Prędkość i kierunek wiatru', fontsize=16)
ax1.set_xlabel('Data', fontsize=13)
ax1.set_ylabel('Prędkość wiatru (km/h)', fontsize=13)
ax1.legend(fontsize=12)
ax1.grid(True)
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax1.tick_params(axis='x', rotation=45, labelsize=12)
ax1.tick_params(axis='y', labelsize=12)

# Plot 2: Water Level Over Time
sns.lineplot(data=df_hydro1, x='stan_wody_data_pomiaru', y='stan_wody', label='Poziom wody', color='blue', ax=ax2)
ax2.axhline(y=580, color='red', linestyle='--', linewidth=4, label='Poziom alarmowy')
ax2.axhline(y=560, color='yellow', linestyle='--', linewidth=4, label='Poziom ostrzegawczy')
ax2.set_title('Poziom wody', fontsize=16)
ax2.set_xlabel('Data', fontsize=13)
ax2.set_ylabel('Poziom wody (cm)', fontsize=13)
ax2.legend(fontsize=12)
ax2.grid(True)
ax2.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax2.tick_params(axis='x', rotation=45, labelsize=12)
ax2.tick_params(axis='y', labelsize=12)

# Plot 3: Temperature and Precipitation Changes Over Time
ax3.set_title('Temperatura i Opady', fontsize=16)
ax3.bar(df_meteo['opad_10min_data'], df_meteo['opad_10min'], label='Opady', color='blue', alpha=0.6)
ax3.set_xlabel('Data', fontsize=13)
ax3.set_ylabel('Opady (mm)', fontsize=13, color='blue')
ax3.tick_params(axis='y', labelcolor='blue')
ax3.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax3.tick_params(axis='x', rotation=45, labelsize=12)
ax3.tick_params(axis='y', labelsize=12)
ax3.grid(True)

ax4 = ax3.twinx()
sns.lineplot(data=df_meteo, x='temperatura_gruntu_data', y='temperatura_gruntu', label='Temperatura gruntu', color='orange', ax=ax4)
ax4.set_ylabel('Temperatura (°C)', fontsize=13, color='orange')
ax4.tick_params(axis='y', labelcolor='orange')
ax4.tick_params(axis='y', labelsize=12)

# Apply x-axis settings to all plots
set_monthly_xaxis(ax1, year, month)
set_monthly_xaxis(ax2, year, month)
set_monthly_xaxis(ax3, year, month)

fig.suptitle(f'Dane pogodowe za {year}-{month:02d}\n{location.title()} - {sublocation.title()}', 
            fontsize=20, weight='bold')
fig.tight_layout(pad=3.08)
fig.subplots_adjust(top=0.95, bottom=0.07)

# Save the combined figure with location and sublocation in filename
fig.savefig(f'figures/weather_data_{location}_{sublocation}_{year}_{month:02d}.png')
plt.close()
