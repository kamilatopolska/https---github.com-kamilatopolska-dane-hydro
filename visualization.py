import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import matplotlib.dates as mdates

# Load the aggregated data
df_hydro1 = pd.read_csv('aggregated/aggregated_hydro1_2025_02.csv')
df_hydro2 = pd.read_csv('aggregated/aggregated_hydro2_2025_02.csv')
df_meteo = pd.read_csv('aggregated/aggregated_meteo_2025_02.csv')

# Convert date columns to datetime
df_hydro1['stan_wody_data_pomiaru'] = pd.to_datetime(df_hydro1['stan_wody_data_pomiaru'], errors='coerce')
df_meteo['temperatura_gruntu_data'] = pd.to_datetime(df_meteo['temperatura_gruntu_data'], errors='coerce')
df_meteo['wiatr_kierunek_data'] = pd.to_datetime(df_meteo['wiatr_kierunek_data'], errors='coerce')
df_meteo['opad_10min_data'] = pd.to_datetime(df_meteo['opad_10min_data'], errors='coerce')

# Create a folder for figures
os.makedirs('figures', exist_ok=True)

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

fig.suptitle('Dane pogodowe za luty 2025', fontsize=20, weight='bold')
fig.tight_layout(pad=3.08)
fig.subplots_adjust(top=0.95, bottom=0.07)

# Save the combined figure
fig.savefig('figures/weather_data_february_2025.png')
plt.close()
