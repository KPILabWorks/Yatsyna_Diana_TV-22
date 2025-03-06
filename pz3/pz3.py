#https://youtu.be/zR2bI2iTPgM
import pandas as pd
import featuretools as ft
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

data = pd.read_csv('per-capita-energy-use.csv')

print(data.head())

# новий унікальний індекс, об'єднуючи "Entity" і "Year"
data['index'] = data['Entity'] + "_" + data['Year'].astype(str)

data = pd.get_dummies(data, columns=["Entity", "Code"])

# EntitySet для Featuretools
es = ft.EntitySet(id="energy_data")

#додавання таблиці (DataFrame) в EntitySet з іменем "energy_consumption" і унікальним індексом
es = es.add_dataframe(dataframe=data, 
                      dataframe_name="energy_consumption", 
                      index="index", 
                      time_index="Year")

start_time = time.time()

# автоматичне створення ознак за допомогою deep feature synthesis
feature_matrix, feature_defs = ft.dfs(entityset=es, target_dataframe_name="energy_consumption")

end_time = time.time()
print(f"Час виконання для створення ознак: {end_time - start_time} секунд")

# середнє, максимальне, мінімальне значення
mean_values = feature_matrix.mean(axis=0)
max_values = feature_matrix.max(axis=0)
min_values = feature_matrix.min(axis=0)

print("\nСтатистичні ознаки:")
print("Середнє значення для кожної ознаки:")
print(mean_values)
print("\nМаксимальне значення для кожної ознаки:")
print(max_values)
print("\nМінімальне значення для кожної ознаки:")
print(min_values)

#розділення на тренувальні та тестові дані
X_train, X_test, y_train, y_test = train_test_split(feature_matrix, data["Primary energy consumption per capita (kWh/person)"], test_size=0.2)

model = RandomForestRegressor()

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
print(f"Середньоквадратична помилка: {mse}")
