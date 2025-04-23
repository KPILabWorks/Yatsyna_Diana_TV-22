#Відео-захист: https://youtu.be/42IRbT2E_tY
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Тарифи на електроенергію (коп./кВт*год)
c = np.array([1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.8, 1.0,
              1.2, 1.5, 1.8, 2.0, 2.2, 2.5, 2.3, 2.0,
              1.8, 1.6, 1.4, 1.3, 1.1, 1.0, 0.9, 0.8])

# Обмеження на навантаження
L_min = np.full(24, 2)
L_max = np.full(24, 10)

# Загальне споживання
D = 150

# Початкове наближення
x0 = np.full(24, D / 24)

# Цільова функція
def objective(x):
    return np.sum(x * c)

# Обмеження: загальне споживання
constraint = {'type': 'eq', 'fun': lambda x: np.sum(x) - D}
bounds = [(L_min[i], L_max[i]) for i in range(24)]

# Оптимізація
result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=[constraint])
opt_x = result.x
opt_cost = objective(opt_x)

# Евристика
sorted_indices = np.argsort(c)
heuristic_x = np.zeros(24)
remaining = D
for idx in sorted_indices:
    possible = min(L_max[idx], remaining)
    if possible < L_min[idx]:
        continue
    heuristic_x[idx] = possible
    remaining -= possible
    if remaining <= 0:
        break
heuristic_cost = np.sum(heuristic_x * c)

# Вивід результатів у консоль
print("=== Оптимальне навантаження (SciPy.optimize) ===")
for i, val in enumerate(opt_x):
    print(f"Година {i:02d}: {val:.2f} кВт")
print(f"Загальна вартість: {opt_cost:.2f} коп.")

print("\n=== Евристичне навантаження ===")
for i, val in enumerate(heuristic_x):
    print(f"Година {i:02d}: {val:.2f} кВт")
print(f"Загальна вартість: {heuristic_cost:.2f} коп.")

# Візуалізація
hours = np.arange(24)
plt.figure(figsize=(12, 6))
plt.plot(hours, opt_x, label="Оптимальне навантаження (SciPy)", marker='o')
plt.plot(hours, heuristic_x, label="Евристичне навантаження", marker='s')
plt.plot(hours, c, label="Тариф (коп./кВт*год)", color='gray', linestyle='--')
plt.xlabel("Година доби")
plt.ylabel("Навантаження (кВт)")
plt.title("Порівняння: Оптимізація vs Евристика")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
