import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit, QMessageBox, QHBoxLayout, QSpinBox
from PyQt5.QtCore import Qt
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class GraphApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.G = nx.DiGraph()
        self.use_knn = False  
        self.K = 2  
    
    def initUI(self):
        layout = QVBoxLayout()
        
        self.label_edges = QLabel("Введите ребра графа (узел1, узел2, вес):")
        layout.addWidget(self.label_edges)
        
        self.text_edges = QTextEdit()
        self.text_edges.setPlainText("a, b, 3\na, c, 5\nb, c, 2\nc, a, 4\nc, b, 8\nd, a, 1\nc, d, 7\nb, e, 3\ne, c, 4")
        layout.addWidget(self.text_edges)
        
        self.btn_create = QPushButton("Создать граф")
        self.btn_create.clicked.connect(self.build_graph_from_input)
        layout.addWidget(self.btn_create)
        
        self.canvas = FigureCanvas(plt.figure())
        layout.addWidget(self.canvas)
        
        controls_layout = QHBoxLayout()
        self.label_start = QLabel("Начальный узел:")
        controls_layout.addWidget(self.label_start)
        
        self.entry_start = QLineEdit("a")
        controls_layout.addWidget(self.entry_start)
        
        self.btn_run = QPushButton("Выполнить алгоритм")
        self.btn_run.clicked.connect(self.run_algorithm)
        controls_layout.addWidget(self.btn_run)
        
        self.btn_toggle_knn = QPushButton("Использовать k-NN")
        self.btn_toggle_knn.clicked.connect(self.toggle_knn)
        controls_layout.addWidget(self.btn_toggle_knn)
        
        self.spin_k = QSpinBox()
        self.spin_k.setMinimum(1)
        self.spin_k.setValue(2)
        self.spin_k.valueChanged.connect(self.update_k)
        controls_layout.addWidget(QLabel("K:"))
        controls_layout.addWidget(self.spin_k)
        
        layout.addLayout(controls_layout)
        
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        layout.addWidget(self.text_result)
        
        self.setLayout(layout)
        self.setWindowTitle("Алгоритм ближайшего соседа / k-NN")
        self.resize(800, 600)
    
    def build_graph_from_input(self):
        self.G.clear()
        input_text = self.text_edges.toPlainText().strip()
        if not input_text:
            QMessageBox.critical(self, "Ошибка", "Пожалуйста, введите данные для графа.")
            return
        
        lines = input_text.split('\n')
        edges = []
        for line in lines:
            parts = line.split(',')
            if len(parts) != 3:
                QMessageBox.critical(self, "Ошибка", f"Неверный формат строки: {line}")
                return
            u, v = parts[0].strip(), parts[1].strip()
            try:
                weight = float(parts[2].strip())
            except ValueError:
                QMessageBox.critical(self, "Ошибка", f"Неверный вес в строке: {line}")
                return
            edges.append((u, v, weight))
        
        self.G.add_weighted_edges_from(edges)
        QMessageBox.information(self, "Успех", "Граф успешно создан!")
        self.draw_graph()
    
    def draw_graph(self, path_edges=None):
        fig, ax = plt.subplots()
        pos = nx.spring_layout(self.G)
        nx.draw(self.G, pos, ax=ax, with_labels=True, node_color='lightblue', edge_color='gray')
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, ax=ax)
        
        if path_edges:
            nx.draw_networkx_edges(self.G, pos, ax=ax, edgelist=path_edges, edge_color='red', width=2)
        
        self.canvas.figure = fig
        self.canvas.draw()

    def heuristic(self, node, visited):
        remaining = set(self.G.nodes) - visited
        if not remaining:
            return 0  

        total = 0
        count = 0

        for n in remaining:
            weights = [self.G[n][u]['weight'] for u in remaining if self.G.has_edge(n, u)]
            if weights:  
                total += min(weights)
                count += 1

        return total / count if count > 0 else float('inf') 

    
    def knn_algorithm(self, start_node):
        visited = {start_node}
        path = [start_node]
        total_distance = 0
        v = start_node

        while len(visited) < len(self.G.nodes):
            neighbors = sorted(
                [(u, self.G[v][u]['weight']) for u in self.G.neighbors(v) if u not in visited],
                key=lambda x: x[1]
            )

            if not neighbors:
                break

            candidates = [(u, d, self.heuristic(u, visited)) for u, d in neighbors[:self.K]]
            candidates.sort(key=lambda x: x[2])  

            chosen_node = candidates[0][0] 

            path.append(chosen_node)
            visited.add(chosen_node)
            total_distance += self.G[v][chosen_node]['weight']
            v = chosen_node

        if len(visited) == len(self.G.nodes) and self.G.has_edge(v, start_node):
            total_distance += self.G[v][start_node]['weight']
            path.append(start_node)

        return path, total_distance
    
    def nearest_neighbor(self, start_node):
        visited = {start_node}
        path = [start_node]
        total_distance = 0
        v = start_node
        
        while len(visited) < len(self.G.nodes):
            neighbors = [
                (u, self.G[v][u]['weight']) for u in self.G.neighbors(v) if u not in visited
            ]
            
            if not neighbors:
                break
            
            
            chosen_node, min_weight = min(neighbors, key=lambda x: x[1])
            
            path.append(chosen_node)
            visited.add(chosen_node)
            total_distance += min_weight
            v = chosen_node
       
        if len(visited) == len(self.G.nodes) and self.G.has_edge(v, start_node):
            total_distance += self.G[v][start_node]['weight']
            path.append(start_node)
        
        return path, total_distance
    
    def run_algorithm(self):
        if not self.G.nodes:
            QMessageBox.critical(self, "Ошибка", "Граф не создан.")
            return
        
        start_node = self.entry_start.text().strip()
        if start_node not in self.G.nodes:
            QMessageBox.critical(self, "Ошибка", "Введите корректный начальный узел.")
            return
        
        if self.use_knn:
            path, distance = self.knn_algorithm(start_node)
        else:
            path, distance = self.nearest_neighbor(start_node)
        
        result_message = f"Путь: {' -> '.join(path)}, Общая длина: {distance}"
        self.text_result.setPlainText(result_message)
        self.draw_graph(list(zip(path[:-1], path[1:])) if len(path) > 1 else None)
    
    def toggle_knn(self):
        self.use_knn = not self.use_knn
        self.btn_toggle_knn.setText("Выкл knn" if self.use_knn else "Вкл knn")
    
    def update_k(self, value):
        self.K = value
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GraphApp()
    window.show()
    sys.exit(app.exec_())