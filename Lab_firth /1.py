import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Целевая функция для оптимизации
def objective_function(x):
    x1, x2 = x
    return (x1 - 2) ** 4 + (x1 - 2 * x2) ** 2


# PSO алгоритм
class ParticleSwarmOptimizer:
    def __init__(self, function, num_particles, inertia=0.5, cognitive=1.5, social=1.5, compression_factor_enabled=False):
        self.function = function
        self.num_particles = num_particles
        self.inertia = inertia
        self.cognitive = cognitive
        self.social = social
        self.compression_factor_enabled = compression_factor_enabled  # Состояние коэффициента сжатия
        self.positions = np.random.uniform(-10, 10, (num_particles, 2))
        self.velocities = np.random.uniform(-1, 1, (num_particles, 2))
        self.best_personal_positions = self.positions.copy()
        self.best_personal_scores = np.array([function(pos) for pos in self.positions])
        self.global_best_position = self.best_personal_positions[self.best_personal_scores.argmin()]
        self.global_best_score = self.best_personal_scores.min()

    def step(self):
        for i in range(self.num_particles):
            r1, r2 = np.random.rand(2)
            # Учитываем коэффициент сжатия, если он включен
            velocity_update = (self.inertia * self.velocities[i]
                               + self.cognitive * r1 * (self.best_personal_positions[i] - self.positions[i])
                               + self.social * r2 * (self.global_best_position - self.positions[i]))

            if self.compression_factor_enabled:
                # Модификация коэффициента сжатия (если включен)
                velocity_update *= 0.9  # Пример изменения сжатия скорости на 10%

            self.velocities[i] = velocity_update
            self.positions[i] += self.velocities[i]

            score = self.function(self.positions[i])
            if score < self.best_personal_scores[i]:
                self.best_personal_scores[i] = score
                self.best_personal_positions[i] = self.positions[i]

            if score < self.global_best_score:
                self.global_best_score = score
                self.global_best_position = self.positions[i]


# Запуск PSO и обновление графика
def run_pso():
    num_iterations = int(iterations_entry.get())
    num_particles = int(particles_entry.get())
    inertia = float(inertia_entry.get())
    cognitive = float(cognitive_entry.get())
    social = float(social_entry.get())

    compression_enabled = compression_var.get()  # Получаем состояние кнопки сжатия

    optimizer = ParticleSwarmOptimizer(objective_function, num_particles, inertia, cognitive, social, compression_enabled)

    for _ in range(num_iterations):
        optimizer.step()
        plot_particles(optimizer.positions)
        root.update_idletasks()

    best_x1, best_x2 = optimizer.global_best_position
    best_score = optimizer.global_best_score
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END,
                       f"Лучшее найденное положение:\nX1 = {best_x1}\nX2 = {best_x2}\nЗначение функции: {best_score}")


# Обновление графика
def plot_particles(positions):
    ax.scatter(positions[:, 0], positions[:, 1], color='blue')  # добавление точек на график
    ax.set_xlim(-50, 50)  # Диапазон по оси X
    ax.set_ylim(-50, 50)  # Диапазон по оси Y
    ax.set_title("Распределение частиц")
    ax.set_xlabel("X1")
    ax.set_ylabel("X2")
    canvas.draw()

# def plot_particles(positions):
#     ax.cla()  # Очищаем график перед добавлением новых точек
#     ax.scatter(positions[:, 0], positions[:, 1], color='blue')  # Добавление точек на график
#     ax.set_xlim(-50, 50)  # Диапазон по оси X
#     ax.set_ylim(-50, 50)  # Диапазон по оси Y
#     ax.set_title("Распределение частиц")
#     ax.set_xlabel("X1")
#     ax.set_ylabel("X2")
#     canvas.draw()
# Настройка интерфейса
root = tk.Tk()
root.title("Роевой интеллект")

# Параметры
parameters_frame = tk.LabelFrame(root, text="Параметры", padx=10, pady=10)
parameters_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

tk.Label(parameters_frame, text="Коэф. текущей скорости:").grid(row=1, column=0, sticky="w")
inertia_entry = tk.Entry(parameters_frame, width=5)
inertia_entry.insert(0, "0.5")
inertia_entry.grid(row=1, column=1, sticky="w")

tk.Label(parameters_frame, text="Коэф. собственного лучшего значения:").grid(row=2, column=0, sticky="w")
cognitive_entry = tk.Entry(parameters_frame, width=5)
cognitive_entry.insert(0, "1.5")
cognitive_entry.grid(row=2, column=1, sticky="w")

tk.Label(parameters_frame, text="Коэф. глобального лучшего значения:").grid(row=3, column=0, sticky="w")
social_entry = tk.Entry(parameters_frame, width=5)
social_entry.insert(0, "1.5")
social_entry.grid(row=3, column=1, sticky="w")

tk.Label(parameters_frame, text="Количество частиц:").grid(row=4, column=0, sticky="w")
particles_entry = tk.Entry(parameters_frame, width=5)
particles_entry.insert(0, "30")
particles_entry.grid(row=4, column=1, sticky="w")

# Управление
control_frame = tk.LabelFrame(root, text="Управление", padx=10, pady=10)
control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n")

tk.Label(control_frame, text="Количество итераций:").grid(row=0, column=0, sticky="w")
iterations_entry = tk.Entry(control_frame, width=5)
iterations_entry.insert(0, "50")
iterations_entry.grid(row=0, column=1, sticky="w")

calculate_button = tk.Button(control_frame, text="Рассчитать", command=run_pso)
calculate_button.grid(row=1, column=0, columnspan=2, pady=10)

compression_var = tk.BooleanVar()
compression_button = tk.Checkbutton(control_frame, text="Модификация коэффициента сжатия", variable=compression_var)
compression_button.grid(row=2, column=0, columnspan=2)


results_frame = tk.LabelFrame(root, text="Результаты", padx=10, pady=10)
results_frame.grid(row=2, column=0, padx=10, pady=10, sticky="n")

result_text = tk.Text(results_frame, width=30, height=5)
result_text.grid(row=0, column=0)


fig, ax = plt.subplots(figsize=(4, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=1, rowspan=3, padx=10, pady=10)

root.mainloop()
