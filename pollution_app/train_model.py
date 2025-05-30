import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import joblib

# Завантаження CSV
df = pd.read_csv("synthetic_realistic_data.csv")

# Вибір ознак і цільової змінної
X = df[['temperature', 'ph', 'nitrogen', 'flow_speed']].values
y = df['pollution_level'].values

# Масштабування
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Побудова нейромережі
model = Sequential([
    Dense(32, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Навчання
model.fit(X_train, y_train, epochs=150, batch_size=16, validation_data=(X_test, y_test))

# Збереження
model.save('predictor_model.h5')
joblib.dump(scaler, 'scaler.save')

# Тестова оцінка
loss, mae = model.evaluate(X_test, y_test)
print(f"Test loss: {loss:.4f}, MAE: {mae:.4f}")
