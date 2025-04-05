import sys
import random
import math
import time
import networkx as nx
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF, QColor
from PyQt5.QtCore import QPointF
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from PyQt5.QtWidgets import QInputDialog, QTableWidget, QTableWidgetItem


class GraphCanvas(FigureCanvas):
    def __init__(self, figure, parent):
        super().__init__(figure)
        self.setParent(parent)
        self.visualizer = parent
        self.mpl_connect("button_press_event", self.on_click)

    def on_click(self, event):
        if event.xdata is not None and event.ydata is not None:
            self.visualizer.handle_graph_click(event.xdata, event.ydata)


class NearestNeighborTSP:
    def __init__(self, graph, use_knn=False, k=2):
        self.graph = graph
        self.use_knn = use_knn
        self.k = max(1, k)

    def find_shortest_path(self, start):
        if len(self.graph.nodes) == 0:
            return [], 0, False

        path = [start]
        unvisited = set(self.graph.nodes) - {start}
        total_length = 0

        while unvisited:
            current = path[-1]
            neighbors = {node: self.graph[current][node]['weight'] for node in self.graph.successors(current) if node in unvisited}

            if not neighbors:
                break

            if self.use_knn:
                top_k_neighbors = sorted(neighbors.items(), key=lambda x: x[1])[:self.k]
                next_node = min(top_k_neighbors, key=lambda x: x[1])[0]
            else:
                next_node = min(neighbors, key=neighbors.get)

            path.append(next_node)
            unvisited.remove(next_node)
            total_length += neighbors[next_node]

        if path[0] in self.graph.successors(path[-1]):
            total_length += self.graph[path[-1]][path[0]]['weight']
            path.append(path[0])
            is_hamiltonian = len(set(path)) == len(self.graph.nodes)
        else:
            is_hamiltonian = False

        return path, total_length, is_hamiltonian


class SimulatedAnnealingTSP:
    def __init__(self, graph, T_start=1000, T_min=1, alpha=0.995, max_iter=100, mode="standard"):
        self.graph = graph
        self.mode = mode
        if mode == "boltzmann":
            self.T_start = 5000
            self.T_min = 10
            self.alpha = 0.98
            self.max_iter = 30
        else:  # стандартный отжиг
            self.T_start = T_start
            self.T_min = T_min
            self.alpha = alpha
            self.max_iter = max_iter

    def total_distance(self, path):
        dist = 0
        for i in range(len(path) - 1):
            if self.graph.has_edge(path[i], path[i + 1]):
                dist += self.graph[path[i]][path[i + 1]]['weight']
            else:
                return float('inf')
        return dist

    def generate_neighbor(self, path):
        new_path = path[:]
        i, j = sorted(random.sample(range(1, len(path) - 1), 2))
        new_path[i:j+1] = reversed(new_path[i:j+1])
        return new_path

    def acceptance_probability(self, delta, T):
        try:
            if self.mode == "boltzmann":
                # Сглаженная функция Больцмана
                x = max(-700, min(700, delta / T))
                return 1 / (1 + math.exp(x))
            else:
                return math.exp(-delta / T)
        except OverflowError:
            return 0.0

    def find_path(self):
        nodes = list(self.graph.nodes)
        if len(nodes) < 2:
            return nodes, 0, False

        current_path = nodes[:]
        random.shuffle(current_path)
        current_path.append(current_path[0])
        best_path = current_path[:]
        best_cost = self.total_distance(current_path)
        T = self.T_start

        while T > self.T_min:
            for _ in range(self.max_iter):
                new_path = self.generate_neighbor(current_path)
                new_cost = self.total_distance(new_path)

                delta = new_cost - self.total_distance(current_path)
                if delta < 0 or random.random() < self.acceptance_probability(delta, T):
                    current_path = new_path[:]
                    if new_cost < best_cost:
                        best_cost = new_cost
                        best_path = new_path[:]
            T *= self.alpha

        is_hamiltonian = len(set(best_path[:-1])) == len(nodes) and best_path[0] == best_path[-1]
        return best_path, best_cost, is_hamiltonian


class GraphEditor(QtWidgets.QWidget):
    def __init__(self, tsp_app):
        super().__init__()
        self.setWindowTitle("Редактор графа")
        self.resize(500, 500)
        self.nodes = []
        self.edges = []
        self.tsp_app = tsp_app
        self.start_node = None
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        button = QtWidgets.QPushButton("Рассчитать путь")
        button.clicked.connect(self.calculate_path_in_editor)
        layout.addWidget(button)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            pos = event.pos()
            for i, (x, y) in enumerate(self.nodes):
                if (x - pos.x()) ** 2 + (y - pos.y()) ** 2 <= 400:
                    if self.start_node is None:
                        self.start_node = i
                    else:
                        weight, ok = QInputDialog.getInt(self, "Введите вес", "Вес ребра:", min=1)
                        if ok:
                            self.edges.append((self.start_node, i, weight))
                        self.start_node = None
                    self.update()
                    return
            self.nodes.append((pos.x(), pos.y()))
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(0, 180, 0), 2)
        painter.setPen(pen)
        for start, end, weight in self.edges:
            x1, y1 = self.nodes[start]
            x2, y2 = self.nodes[end]
            painter.drawLine(x1, y1, x2, y2)
            self.draw_arrow(painter, x1, y1, x2, y2)
            painter.drawText(int((x1 + x2) / 2), int((y1 + y2) / 2), str(weight))
        painter.setBrush(QBrush(QtCore.Qt.red))
        for i, (x, y) in enumerate(self.nodes):
            painter.drawEllipse(QPointF(x, y), 10, 10)
            painter.drawText(int(x - 10), int(y - 10), str(i))

    def draw_arrow(self, painter, x1, y1, x2, y2):
        arrow_size = 20
        angle = math.atan2(y2 - y1, x2 - x1)
        p1 = QPointF(x2 - arrow_size * math.cos(angle - math.pi / 6), y2 - arrow_size * math.sin(angle - math.pi / 6))
        p2 = QPointF(x2, y2)
        p3 = QPointF(x2 - arrow_size * math.cos(angle + math.pi / 6), y2 - arrow_size * math.sin(angle + math.pi / 6))
        painter.setBrush(QBrush(QtCore.Qt.yellow))
        painter.drawPolygon(QPolygonF([p1, p2, p3]))

    def calculate_path_in_editor(self):
        self.tsp_app.graph.clear()
        self.tsp_app.node_positions = {i: (x, y) for i, (x, y) in enumerate(self.nodes)}
        for i in range(len(self.nodes)):
            self.tsp_app.graph.add_node(i)
        for start, end, weight in self.edges:
            self.tsp_app.graph.add_edge(start, end, weight=weight)
        self.tsp_app.run_algorithm()


class TSPVisualizer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.graph = nx.DiGraph()
        self.node_positions = {}
        self.selected_node = None
        self.initialize_example_graph()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Задача коммивояжера")
        self.setGeometry(100, 100, 1200, 800)
        self.layout = QtWidgets.QGridLayout()

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.ax.axis('off')
        self.canvas = GraphCanvas(self.figure, self)
        self.layout.addWidget(self.canvas, 0, 1, 8, 1)

        self.sa_mode_combo = QtWidgets.QComboBox()
        self.sa_mode_combo.addItem("Метод ближайшего соседа")
        self.sa_mode_combo.addItem("Больцмановский отжиг")
        self.sa_mode_combo.addItem("Отжиг")
        self.layout.addWidget(QtWidgets.QLabel("Алгоритм оптимизации:"), 0, 2)
        self.layout.addWidget(self.sa_mode_combo, 0, 3)

        self.knn_checkbox = QtWidgets.QCheckBox("Использовать KNN")
        self.layout.addWidget(self.knn_checkbox, 1, 2)

        self.k_input = QtWidgets.QSpinBox()
        self.k_input.setMinimum(1)
        self.k_input.setValue(2)
        self.layout.addWidget(self.k_input, 2, 2)

        self.result_path = QtWidgets.QLabel("Полученный путь: ")
        self.layout.addWidget(self.result_path, 3, 2)

        self.time_label = QtWidgets.QLabel("Время выполнения: ")
        self.layout.addWidget(self.time_label, 4, 2)

        self.hamiltonian_label = QtWidgets.QLabel("Статус гамильтонова цикла: ")
        self.layout.addWidget(self.hamiltonian_label, 5, 2)

        self.calculate_button = QtWidgets.QPushButton("Рассчитать путь")
        self.calculate_button.clicked.connect(self.run_algorithm)
        self.layout.addWidget(self.calculate_button, 6, 2)

        self.draw_graph_button = QtWidgets.QPushButton("Рисовать граф")
        self.draw_graph_button.clicked.connect(self.open_graph_editor)
        self.layout.addWidget(self.draw_graph_button, 7, 2)

        self.clear_button = QtWidgets.QPushButton("Очистить граф")
        self.clear_button.clicked.connect(self.clear_graph)
        self.layout.addWidget(self.clear_button, 8, 2)

        self.setLayout(self.layout)
        self.draw_graph([])
        self.show()

    def initialize_example_graph(self):
        self.graph.clear()
        self.node_positions.clear()

        for i in range(25):
            x = random.randint(50, 700)
            y = random.randint(50, 500)
            self.node_positions[i] = (x, y)
            self.graph.add_node(i)

        for i, j in itertools.permutations(self.graph.nodes, 2):
            dist = int(math.hypot(
                self.node_positions[i][0] - self.node_positions[j][0],
                self.node_positions[i][1] - self.node_positions[j][1]
            ))
            self.graph.add_edge(i, j, weight=dist)

    def open_graph_editor(self):
        self.editor = GraphEditor(self)
        self.editor.show()

    def handle_graph_click(self, x, y):
        node_id = len(self.node_positions)
        self.graph.add_node(node_id)
        self.node_positions[node_id] = (x, y)
        self.draw_graph([])

    def draw_graph(self, path, is_hamiltonian=True):
        self.ax.clear()
        nx.draw(self.graph, self.node_positions, ax=self.ax, with_labels=True, node_color='red', edge_color='green',
                node_size=700, font_size=10)

        if path:
            path_edges = list(zip(path, path[1:]))
            nx.draw_networkx_edges(self.graph, self.node_positions, edgelist=path_edges, edge_color='red', width=2, ax=self.ax, arrows=True)

        self.canvas.draw()

    def run_algorithm(self):
        self.result_path.setText("Полученный путь: ")
        self.hamiltonian_label.setText("Статус гамильтонова цикла: ")
        self.time_label.setText("Время выполнения: ")
        self.draw_graph([])

        if len(self.graph.nodes) == 0:
            self.result_path.setText("Ошибка: Граф пуст.")
            self.hamiltonian_label.setText("Статус гамильтонова цикла: Граф пуст.")
            return

        start_node = list(self.graph.nodes)[0]
        use_knn = self.knn_checkbox.isChecked()
        k_value = self.k_input.value()
        sa_mode = self.sa_mode_combo.currentText()

        start_time = time.time()

        if sa_mode == "Больцмановский отжиг":
            solver = SimulatedAnnealingTSP(self.graph, mode="boltzmann")
            best_path, best_length, is_hamiltonian = solver.find_path()
        elif sa_mode == "Отжиг":
            solver = SimulatedAnnealingTSP(self.graph, mode="standard")
            best_path, best_length, is_hamiltonian = solver.find_path()
        else:
            solver = NearestNeighborTSP(self.graph, use_knn=use_knn, k=k_value)
            best_path, best_length, is_hamiltonian = solver.find_shortest_path(start_node)

        elapsed_time = round((time.time() - start_time) * 1000, 2)
        self.time_label.setText(f"Время выполнения: {elapsed_time} мс")

        if is_hamiltonian:
            self.result_path.setText(f"Путь: {best_path}, Длина: {best_length}")
            self.hamiltonian_label.setText("Статус гамильтонова цикла: Гамильтонов цикл найден")
        else:
            self.result_path.setText(f"Путь: {best_path}, Длина: {best_length} (Гамильтонов цикл не найден)")
            self.hamiltonian_label.setText("Статус гамильтонова цикла: Гамильтонов цикл не найден")

        self.draw_graph(best_path, is_hamiltonian)

    def clear_graph(self):
        self.graph.clear()
        self.node_positions.clear()
        self.result_path.setText("Граф очищен.")
        self.hamiltonian_label.setText("Статус гамильтонова цикла: ")
        self.time_label.setText("Время выполнения: ")
        self.draw_graph([])


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = TSPVisualizer()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    import itertools
    main()
