import sys
import networkx as nx
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtGui, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

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

        
        if path[0] in self.graph.successors(path[-1]) and len(set(path)) == len(self.graph.nodes):
            total_length += self.graph[path[-1]][path[0]]['weight']
            path.append(path[0])
            is_hamiltonian = True
        else:
            is_hamiltonian = False


        return path, total_length, is_hamiltonian

class TSPVisualizer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.graph = nx.DiGraph()
        self.initUI()
        self.load_example_graph()

    def initUI(self):
        self.setWindowTitle("Метод ближайшего соседа (KNN)")
        self.setGeometry(100, 100, 900, 600)
        self.layout = QtWidgets.QGridLayout()

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas, 0, 1)

        self.list_edges = QtWidgets.QTableWidget()
        self.list_edges.setColumnCount(3)
        self.list_edges.setHorizontalHeaderLabels(["Вершина 1", "Вершина 2", "Длина"])
        self.layout.addWidget(self.list_edges, 0, 2)

        self.add_edge_button = QtWidgets.QPushButton("Добавить ребро")
        self.add_edge_button.clicked.connect(self.add_edge)
        self.layout.addWidget(self.add_edge_button, 1, 2)

        self.start_node_label = QtWidgets.QLabel("Начальная вершина:")
        self.layout.addWidget(self.start_node_label, 2, 2)

        self.start_node_select = QtWidgets.QComboBox()
        self.layout.addWidget(self.start_node_select, 3, 2)

        self.run_button = QtWidgets.QPushButton("Рассчитать путь")
        self.run_button.clicked.connect(self.run_algorithm)
        self.layout.addWidget(self.run_button, 4, 2)

        self.clear_button = QtWidgets.QPushButton("Очистить граф")
        self.clear_button.clicked.connect(self.clear_graph)
        self.layout.addWidget(self.clear_button, 5, 2)

        self.knn_checkbox = QtWidgets.QCheckBox("Использовать KNN")
        self.layout.addWidget(self.knn_checkbox, 6, 2)

        self.k_input = QtWidgets.QSpinBox()
        self.k_input.setMinimum(1)
        self.k_input.setValue(2)
        self.layout.addWidget(self.k_input, 7, 2)

        self.result_path = QtWidgets.QLabel("Полученный путь: ")
        self.layout.addWidget(self.result_path, 8, 2)

        self.setLayout(self.layout)
        self.show()

    def add_edge(self):
        row_position = self.list_edges.rowCount()
        self.list_edges.insertRow(row_position)

    def run_algorithm(self):
        self.graph.clear()
        nodes_set = set()

        for row in range(self.list_edges.rowCount()):
            node1_item = self.list_edges.item(row, 0)
            node2_item = self.list_edges.item(row, 1)
            weight_item = self.list_edges.item(row, 2)

            if node1_item and node2_item and weight_item:
                try:
                    node1 = int(node1_item.text())
                    node2 = int(node2_item.text())
                    weight = int(weight_item.text())
                    self.graph.add_edge(node1, node2, weight=weight)
                    nodes_set.add(node1)
                    nodes_set.add(node2)
                except ValueError:
                    continue

        if len(nodes_set) == 0:
            self.result_path.setText("Ошибка: Граф не содержит рёбер.")
            return

        start_node_text = self.start_node_select.currentText()
        if not start_node_text:
            self.result_path.setText("Ошибка: Выберите начальную вершину.")
            return

        start_node = int(start_node_text)
        use_knn = self.knn_checkbox.isChecked()
        k_value = self.k_input.value()

        solver = NearestNeighborTSP(self.graph, use_knn=use_knn, k=k_value)
        best_path, best_length, is_hamiltonian = solver.find_shortest_path(start_node)

        if is_hamiltonian:
            self.result_path.setText(f"Путь: {best_path}, Длина: {best_length}")
        else:
            self.result_path.setText(f"Путь: {best_path}, Длина: {best_length} (⚠️ Гамильтонов цикл не найден)")

        self.draw_graph(best_path)

    def draw_graph(self, path):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        pos = nx.circular_layout(self.graph)
        nx.draw(self.graph, pos, ax=ax, with_labels=True, node_color='orange', edge_color='blue', node_size=700, font_size=10)

        labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=labels, ax=ax)

        if path:
            path_edges = list(zip(path, path[1:]))
            nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges, edge_color='red', width=2, ax=ax, arrows=True)

        self.canvas.draw()

    def clear_graph(self):
        self.graph.clear()
        self.list_edges.setRowCount(0)
        self.start_node_select.clear()
        self.result_path.setText("Граф очищен.")
        self.draw_graph([])

    def load_example_graph(self):
        example_edges = [(0,1,3),(0,2,5),(1,2,2),(2,0,4),(2,1,8),(3,0,1),(2,3,7),(1,4,3),(4,2,3)]

        for node1, node2, weight in example_edges:
            row_position = self.list_edges.rowCount()
            self.list_edges.insertRow(row_position)
            self.list_edges.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(node1)))
            self.list_edges.setItem(row_position, 1, QtWidgets.QTableWidgetItem(str(node2)))
            self.list_edges.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(weight)))
            self.graph.add_edge(node1, node2, weight=weight)

        nodes = set(sum(([n1, n2] for n1, n2, _ in example_edges), []))
        self.start_node_select.addItems(map(str, sorted(nodes)))
        self.draw_graph([])

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = TSPVisualizer()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
