import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random

POPULATION_SIZE = 50
MUTATION_RATE = 0.2
GENES_RANGE = (-50, 50)
GENERATIONS = 100


def target_function(x1, x2):
    return (x1 - 2) ** 4 + (x1 - 2 * x2) ** 2


def generate_population(size, gene_range):
    population = []
    for _ in range(size):
        x1 = random.uniform(*gene_range)
        x2 = random.uniform(*gene_range)
        population.append((x1, x2))
    return population


def evaluate_population(population):
    return [(individual, target_function(*individual)) for individual in population]


def select_best(population, fitness, num_best):
    sorted_population = sorted(zip(population, fitness), key=lambda x: x[1])
    return [ind for ind, fit in sorted_population[:num_best]]


def crossover(parent1, parent2):
    child1 = (parent1[0], parent2[1])
    child2 = (parent2[0], parent1[1])
    return child1, child2


def mutate(individual, mutation_rate, gene_range):
    x1, x2 = individual
    if random.random() < mutation_rate:
        x1 = random.uniform(*gene_range)
    if random.random() < mutation_rate:
        x2 = random.uniform(*gene_range)
    return x1, x2


def create_new_population(population, mutation_rate, gene_range, elite_selection):
    new_population = []
    fitness_values = [target_function(*ind) for ind in population]

    # Используем элитарный отбор, если включена модификация
    if elite_selection:
        best_individuals = select_best(population, fitness_values, len(population) // 2)
    else:
        best_individuals = population  # Если модификация отключена, используем всю популяцию

    while len(new_population) < len(population):
        parent1, parent2 = random.sample(best_individuals, 2)
        child1, child2 = crossover(parent1, parent2)
        new_population.append(mutate(child1, mutation_rate, gene_range))
        new_population.append(mutate(child2, mutation_rate, gene_range))

    return new_population[:len(population)]


def run_genetic_algorithm():
    try:
        mutation_rate = float(mutation_rate_entry.get()) / 100
        population_size = int(population_size_entry.get())
        generations = int(generations_entry.get())
        min_gene_value = float(min_gene_value_entry.get())
        max_gene_value = float(max_gene_value_entry.get())

        gene_range = (min_gene_value, max_gene_value)
        elite_selection = elite_selection_var.get()

        population = generate_population(population_size, gene_range)

        for row in tree.get_children():
            tree.delete(row)
        result_text.delete(1.0, tk.END)

        best_solution = None
        best_value = float("inf")

        for generation in range(generations):
            evaluated_population = evaluate_population(population)
            population, fitness_values = zip(*evaluated_population)

            current_best = min(evaluated_population, key=lambda x: x[1])
            if current_best[1] < best_value:
                best_solution, best_value = current_best

            for i, (ind, fit) in enumerate(evaluated_population):
                x1, x2 = ind
                tree.insert("", "end", values=(i + 1, f"{fit:.2f}", f"{x1:.2f}", f"{x2:.2f}"))

            population = create_new_population(population, mutation_rate, gene_range, elite_selection)

        best_x1, best_x2 = best_solution
        result_text.insert(tk.END,
                           f"Лучшее решение:\nX[1] = {best_x1:.6f}\nX[2] = {best_x2:.6f}\nЗначение функции: {best_value:.6f}")

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные значения.")


root = tk.Tk()
root.title("Генетический алгоритм")

parameters_frame = tk.LabelFrame(root, text="Параметры", padx=10, pady=10)
parameters_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

tk.Label(parameters_frame, text="Функция:").grid(row=0, column=0, sticky="w")
function_entry = tk.Entry(parameters_frame, width=25)
function_entry.insert(0, "(x1 - 2)**4 + (x1 - 2 * x2)**2")
function_entry.grid(row=0, column=1)

tk.Label(parameters_frame, text="Вероятность мутации, %:").grid(row=1, column=0, sticky="w")
mutation_rate_entry = tk.Entry(parameters_frame, width=5)
mutation_rate_entry.insert(0, "20")
mutation_rate_entry.grid(row=1, column=1, sticky="w")

tk.Label(parameters_frame, text="Количество хромосом:").grid(row=2, column=0, sticky="w")
population_size_entry = tk.Entry(parameters_frame, width=5)
population_size_entry.insert(0, "50")
population_size_entry.grid(row=2, column=1, sticky="w")

tk.Label(parameters_frame, text="Минимальное значение гена:").grid(row=3, column=0, sticky="w")
min_gene_value_entry = tk.Entry(parameters_frame, width=5)
min_gene_value_entry.insert(0, "-50")
min_gene_value_entry.grid(row=3, column=1, sticky="w")

tk.Label(parameters_frame, text="Максимальное значение гена:").grid(row=4, column=0, sticky="w")
max_gene_value_entry = tk.Entry(parameters_frame, width=5)
max_gene_value_entry.insert(0, "50")
max_gene_value_entry.grid(row=4, column=1, sticky="w")

elite_selection_var = tk.BooleanVar(value=True)
elite_selection_checkbox = tk.Checkbutton(parameters_frame, text="Использовать элитарный отбор", variable=elite_selection_var)
elite_selection_checkbox.grid(row=5, column=0, columnspan=2, sticky="w")

control_frame = tk.LabelFrame(root, text="Управление", padx=10, pady=10)
control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n")

tk.Label(control_frame, text="Количество поколений:").grid(row=0, column=0, sticky="w")
generations_entry = tk.Entry(control_frame, width=5)
generations_entry.insert(0, "100")
generations_entry.grid(row=0, column=1, sticky="w")

calculate_button = tk.Button(control_frame, text="Рассчитать", command=run_genetic_algorithm)
calculate_button.grid(row=1, column=0, columnspan=2, pady=10)

results_frame = tk.LabelFrame(root, text="Результаты", padx=10, pady=10)
results_frame.grid(row=2, column=0, padx=10, pady=10, sticky="n")

result_text = tk.Text(results_frame, width=30, height=5)
result_text.grid(row=0, column=0)

population_frame = tk.LabelFrame(root, text="Хромосомы данного поколения", padx=10, pady=10)
population_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="n")

tree = ttk.Treeview(population_frame, columns=("Номер", "Результат", "Ген 1", "Ген 2"), show="headings")
tree.heading("Номер", text="Номер")
tree.heading("Результат", text="Результат")
tree.heading("Ген 1", text="Ген 1")
tree.heading("Ген 2", text="Ген 2")

scrollbar = ttk.Scrollbar(population_frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")
tree.pack(expand=True, fill="both")

root.mainloop()
