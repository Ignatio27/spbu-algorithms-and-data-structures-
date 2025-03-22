import sys
import networkx as nx
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF, QColor
from PyQt5.QtCore import QPointF
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from PyQt5.QtWidgets import QInputDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout


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


class GraphCanvas(FigureCanvas):
    def __init__(self, figure, parent):
        super().__init__(figure)
        self.setParent(parent)
        self.visualizer = parent
        self.mpl_connect("button_press_event", self.on_click)

    def on_click(self, event):
        if event.xdata is not None and event.ydata is not None:
            self.visualizer.handle_graph_click(event.xdata, event.ydata)


class TSPVisualizer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.graph = nx.DiGraph()
        self.node_positions = {}
        self.selected_node = None

        
        self.initialize_example_graph()

        self.initUI()

    def initialize_example_graph(self):
        self.node_positions = {
            0: (100, 100),
            1: (200, 300),
            2: (400, 200),
            3: (500, 400),
        }

        
        for node, pos in self.node_positions.items():
            self.graph.add_node(node)

        
        self.graph.add_edge(0, 1, weight=10)
        self.graph.add_edge(1, 2, weight=20)
        self.graph.add_edge(2, 3, weight=15)
        self.graph.add_edge(3, 0, weight=25)
        self.graph.add_edge(1, 3, weight=30)

    def initUI(self):
        self.setWindowTitle("Метод ближайшего соседа (KNN)")
        self.setGeometry(100, 100, 1200, 800)
        self.layout = QtWidgets.QGridLayout()

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.ax.axis('off')  # Отключаем оси и метки
        self.canvas = GraphCanvas(self.figure, self)
        self.layout.addWidget(self.canvas, 0, 1, 8, 1)

        self.clear_button = QtWidgets.QPushButton("Очистить граф")
        self.clear_button.clicked.connect(self.clear_graph)
        self.layout.addWidget(self.clear_button, 1, 2)

        self.knn_checkbox = QtWidgets.QCheckBox("Использовать KNN")
        self.layout.addWidget(self.knn_checkbox, 2, 2)

        self.k_input = QtWidgets.QSpinBox()
        self.k_input.setMinimum(1)
        self.k_input.setValue(2)
        self.layout.addWidget(self.k_input, 3, 2)

        self.result_path = QtWidgets.QLabel("Полученный путь: ")
        self.layout.addWidget(self.result_path, 4, 2)

        self.calculate_button = QtWidgets.QPushButton("Рассчитать путь")
        self.calculate_button.clicked.connect(self.run_algorithm)
        self.layout.addWidget(self.calculate_button, 5, 2)

        self.hamiltonian_label = QtWidgets.QLabel("Статус гамильтонова цикла: ")
        self.layout.addWidget(self.hamiltonian_label, 6, 2)

        self.draw_graph_button = QtWidgets.QPushButton("Рисовать граф")
        self.draw_graph_button.clicked.connect(self.open_graph_editor)
        self.layout.addWidget(self.draw_graph_button, 7, 2)

        
        self.adjacency_matrix = QTableWidget()
        self.adjacency_matrix.setRowCount(len(self.graph.nodes))
        self.adjacency_matrix.setColumnCount(len(self.graph.nodes))
        self.update_adjacency_matrix()
        self.layout.addWidget(self.adjacency_matrix, 8, 2)

        
        self.add_edge_button = QtWidgets.QPushButton("Добавить ребро")
        self.add_edge_button.clicked.connect(self.add_edge)
        self.layout.addWidget(self.add_edge_button, 9, 2)

        self.remove_edge_button = QtWidgets.QPushButton("Удалить ребро")
        self.remove_edge_button.clicked.connect(self.remove_edge)
        self.layout.addWidget(self.remove_edge_button, 10, 2)

        self.setLayout(self.layout)

        
        self.draw_graph([])
        self.show()

    def update_adjacency_matrix(self):
        self.adjacency_matrix.clear()
        nodes = sorted(self.graph.nodes)
        self.adjacency_matrix.setRowCount(len(nodes))
        self.adjacency_matrix.setColumnCount(len(nodes))
        self.adjacency_matrix.setHorizontalHeaderLabels([str(node) for node in nodes])
        self.adjacency_matrix.setVerticalHeaderLabels([str(node) for node in nodes])

        for i in nodes:
            for j in nodes:
                if self.graph.has_edge(i, j):
                    weight = self.graph[i][j]['weight']
                    self.adjacency_matrix.setItem(i, j, QTableWidgetItem(str(weight)))
                else:
                    self.adjacency_matrix.setItem(i, j, QTableWidgetItem("0"))

    def add_edge(self):
        start, ok1 = QInputDialog.getInt(self, "Добавить ребро", "Введите начальный узел:", min=0)
        end, ok2 = QInputDialog.getInt(self, "Добавить ребро", "Введите конечный узел:", min=0)
        weight, ok3 = QInputDialog.getInt(self, "Добавить ребро", "Введите вес ребра:", min=1)

        if ok1 and ok2 and ok3:
            self.graph.add_edge(start, end, weight=weight)
            self.update_adjacency_matrix()
            self.draw_graph([])

    def remove_edge(self):
        start, ok1 = QInputDialog.getInt(self, "Удалить ребро", "Введите начальный узел:", min=0)
        end, ok2 = QInputDialog.getInt(self, "Удалить ребро", "Введите конечный узел:", min=0)

        if ok1 and ok2:
            if self.graph.has_edge(start, end):
                self.graph.remove_edge(start, end)
                self.update_adjacency_matrix()
                self.draw_graph([])

    def open_graph_editor(self):
        self.graph_editor = GraphEditor(self)
        self.graph_editor.show()

    def handle_graph_click(self, x, y):
        pass

    def draw_graph(self, path, is_hamiltonian=True):
        self.ax.clear()
        nx.draw(self.graph, self.node_positions, ax=self.ax, with_labels=True, node_color='orange', edge_color='blue',
                node_size=700, font_size=10)

        if path:
            path_edges = list(zip(path, path[1:]))
            nx.draw_networkx_edges(self.graph, self.node_positions, edgelist=path_edges, edge_color='red', width=2, ax=self.ax, arrows=True)
        
        if not is_hamiltonian:
            self.ax.text(0.5, -0.1, "⚠️ Гамильтонов цикл не найден", transform=self.ax.transAxes, fontsize=12,
                         color='red', ha='center', va='center')

        self.canvas.draw()

    def run_algorithm(self):
        self.result_path.setText("Полученный путь: ")
        self.hamiltonian_label.setText("Статус гамильтонова цикла: ")
        self.draw_graph([])  

        if len(self.graph.nodes) == 0:
            self.result_path.setText("Ошибка: Граф пуст.")
            self.hamiltonian_label.setText("Статус гамильтонова цикла: Граф пуст.")
            return

        start_node = list(self.graph.nodes)[0]
        use_knn = self.knn_checkbox.isChecked()
        k_value = self.k_input.value()

        solver = NearestNeighborTSP(self.graph, use_knn=use_knn, k=k_value)
        best_path, best_length, is_hamiltonian = solver.find_shortest_path(start_node)

        if is_hamiltonian:
            self.result_path.setText(f"Путь: {best_path}, Длина: {best_length}")
            self.hamiltonian_label.setText("Статус гамильтонова цикла: ✅ Гамильтонов цикл найден")
        else:
            self.result_path.setText(f"Путь: {best_path}, Длина: {best_length} (⚠️ Гамильтонов цикл не найден)")
            self.hamiltonian_label.setText("Статус гамильтонова цикла: ❌ Гамильтонов цикл не найден")

        
        self.draw_graph(best_path, is_hamiltonian)

    def clear_graph(self):
        self.graph.clear()
        self.node_positions.clear()
        self.result_path.setText("Граф очищен.")
        self.hamiltonian_label.setText("Статус гамильтонова цикла: ")
        self.update_adjacency_matrix()
        self.draw_graph([])


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
        self.layout = QtWidgets.QVBoxLayout()
        
        self.calculate_button = QtWidgets.QPushButton("Рассчитать путь")
        self.calculate_button.clicked.connect(self.calculate_path_in_editor)
        self.layout.addWidget(self.calculate_button)

        self.path_length_label = QtWidgets.QLabel("Длина пути: ")
        self.layout.addWidget(self.path_length_label)

        self.setLayout(self.layout)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            pos = event.pos()
            for i, (x, y) in enumerate(self.nodes):
                if (x - pos.x()) ** 2 + (y - pos.y()) ** 2 <= 400:
                    if self.start_node is None:
                        self.start_node = i
                    else:
                        weight, ok = QtWidgets.QInputDialog.getInt(self, "Введите вес", "Вес ребра:", min=1)
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
        
        pen = QPen(QtCore.Qt.black, 2)
        painter.setPen(pen)
        for start, end, weight in self.edges:
            x1, y1 = self.nodes[start]
            x2, y2 = self.nodes[end]
            painter.drawLine(x1, y1, x2, y2)
            self.draw_arrow(painter, x1, y1, x2, y2)
            painter.drawText(int((x1 + x2) / 2), int((y1 + y2) / 2), str(weight))
        
        painter.setBrush(QBrush(QtCore.Qt.blue))
        for i, (x, y) in enumerate(self.nodes):
            painter.drawEllipse(QPointF(x, y), 10, 10)
            painter.drawText(int(x - 10), int(y - 10), str(i))

    def draw_arrow(self, painter, x1, y1, x2, y2):
        arrow_size = 20
        angle = np.arctan2(y2 - y1, x2 - x1)
        
        line_pen = QPen(QtCore.Qt.black, 2)
        painter.setPen(line_pen)
        painter.drawLine(x1, y1, x2, y2)
        
        p1 = QPointF(x2 - arrow_size * np.cos(angle - np.pi / 6), y2 - arrow_size * np.sin(angle - np.pi / 6))
        p2 = QPointF(x2, y2)
        p3 = QPointF(x2 - arrow_size * np.cos(angle + np.pi / 6), y2 - arrow_size * np.sin(angle + np.pi / 6))
        
        arrow_head = QPolygonF([p1, p2, p3])
        painter.setBrush(QBrush(QtCore.Qt.yellow))
        painter.drawPolygon(arrow_head)

    def get_graph_data(self):
        n = len(self.nodes)
        matrix = np.zeros((n, n))
        for start, end, weight in self.edges:
            matrix[start][end] = weight
        return [str(i) for i in range(n)], matrix

    def calculate_path_in_editor(self):
        node_labels, matrix = self.get_graph_data()
        self.tsp_app.graph.clear()
        self.tsp_app.node_positions = {i: (x, y) for i, (x, y) in enumerate(self.nodes)}

        for i, label in enumerate(node_labels):
            self.tsp_app.graph.add_node(i)

        for start, end, weight in self.edges:
            self.tsp_app.graph.add_edge(start, end, weight=weight)

        start_node = list(self.tsp_app.graph.nodes)[0]
        solver = NearestNeighborTSP(self.tsp_app.graph, use_knn=False, k=2)
        best_path, best_length, is_hamiltonian = solver.find_shortest_path(start_node)

        self.tsp_app.result_path.setText(f"Путь: {best_path}, Длина: {best_length}")
        
        if is_hamiltonian:
            self.tsp_app.hamiltonian_label.setText("Статус гамильтонова цикла: ✅ Гамильтонов цикл найден")
        else:
            self.tsp_app.hamiltonian_label.setText("Статус гамильтонова цикла: ❌ Гамильтонов цикл не найден")

        # Рисуем граф
        self.tsp_app.draw_graph(best_path, is_hamiltonian)


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = TSPVisualizer()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()