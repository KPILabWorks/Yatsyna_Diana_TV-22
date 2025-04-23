#Відео-захист: https://youtu.be/S1it4YB164c
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('Amplitudes.csv')

df = df.dropna()

def get_time_of_day(time_sec):
    if time_sec < 40:
        return 'Ранок'
    elif time_sec < 80:
        return 'Обід'
    elif time_sec < 120:
        return 'Вечір'

df['Time of Day'] = df['Time (s)'].apply(get_time_of_day)

# Аналіз пікових значень для кожного періоду дня
def analyze_peak(df):
    peak_analysis = {}
    time_of_days = df['Time of Day'].unique()

    for time_of_day in time_of_days:
        subset = df[df['Time of Day'] == time_of_day]
        max_noise_time = subset.loc[subset['Sound pressure level (dB)'].idxmax(), 'Time (s)']
        max_noise_level = subset['Sound pressure level (dB)'].max()
        
        min_noise_time = subset.loc[subset['Sound pressure level (dB)'].idxmin(), 'Time (s)']
        min_noise_level = subset['Sound pressure level (dB)'].min()

        max_noise_source = 'Основне джерело шуму' if max_noise_level > -60 else 'Незначне джерело шуму'
        
        min_noise_source = 'Основне джерело шуму відсутнє' if min_noise_level > -60 else 'Шум низької інтенсивності'
        
        peak_analysis[time_of_day] = {
            'Max Noise Level (dB)': max_noise_level,
            'Max Noise Time (s)': max_noise_time,
            'Max Noise Source': max_noise_source,
            'Min Noise Level (dB)': min_noise_level,
            'Min Noise Time (s)': min_noise_time,
            'Min Noise Source': min_noise_source
        }
    
    return peak_analysis

# Отримуємо аналіз пікових даних
peak_analysis = analyze_peak(df)

for time_of_day, analysis in peak_analysis.items():
    print(f"Період дня: {time_of_day}")
    print(f"  Максимальний рівень шуму: {analysis['Max Noise Level (dB)']} дБ на часі {analysis['Max Noise Time (s)']} секунд")
    print(f"    Джерело: {analysis['Max Noise Source']}")
    print(f"  Мінімальний рівень шуму: {analysis['Min Noise Level (dB)']} дБ на часі {analysis['Min Noise Time (s)']} секунд")
    print(f"    Джерело: {analysis['Min Noise Source']}")
    print("-" * 50)

plt.figure(figsize=(10, 6))
plt.plot(df['Time (s)'], df['Sound pressure level (dB)'], marker='o', color='b', label="Рівень шуму")
plt.title('Рівень шуму в кімнаті по часу')
plt.xlabel('Час (с)')
plt.ylabel('Рівень шуму (дБ)')
plt.grid(True)

colors = {'Ранок': 'r', 'Обід': 'g', 'Вечір': 'b', 'Ніч': 'orange'}
for time_of_day, analysis in peak_analysis.items():
    plt.axvline(x=analysis['Max Noise Time (s)'], color=colors[time_of_day], linestyle='--', label=f'{time_of_day} - Макс шум')
    plt.axvline(x=analysis['Min Noise Time (s)'], color=colors[time_of_day], linestyle=':', label=f'{time_of_day} - Мін шум')

plt.legend()
plt.show()
