from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class GanttChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gantt Chart")
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Gantt Chart Widget Placeholder")
        self.layout.addWidget(self.label)
