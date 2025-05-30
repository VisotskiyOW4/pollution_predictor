import pandas as pd
import numpy as np

# Кількість рядків
num_rows = 1000

# Дати — починаємо з 2010 року по місяцях
dates = pd.date_range(start='2010-01', periods=num_rows, freq='M')

# Генерація випадкових, але правдоподібних значень
temperature = np.random.normal(loc=10, scale=5, size=num_rows)  # середня t=10°C, +-5°C
ph = np.random.normal(loc=7, scale=0.3, size=num_rows)          # pH ~7
nitrogen = np.abs(np.random.normal(loc=0.5, scale=0.2, size=num_rows))  # mg/L
flow_speed = np.abs(np.random.normal(loc=1.0, scale=0.3, size=num_rows))  # m/s

# Формуємо pollution_level як залежність від факторів
pollution_level = (
    0.3 * (temperature / 20) +
    0.4 * (nitrogen / 1.0) +
    0.2 * (1 - (flow_speed / 2.0)) +
    np.random.normal(loc=0, scale=0.05, size=num_rows)  # шум
)
pollution_level = np.clip(pollution_level, 0, 1)  # обмежуємо 0–1

# Створюємо DataFrame
df = pd.DataFrame({
    'date': dates,
    'temperature': temperature,
    'ph': ph,
    'nitrogen': nitrogen,
    'flow_speed': flow_speed,
    'pollution_level': pollution_level
})

# Зберігаємо у CSV
df.to_csv('synthetic_water_data.csv', index=False)

print(" Файл згенеровано!")
