import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QSizePolicy
from PyQt5.QtCore import QTimer
from random import randint
import numpy as np
import os
import qdarkstyle

class QueueVisualization(QWidget):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.last_modified_time = os.path.getmtime(filename)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Queue Visualization")

        self.resize(800, 300)
        self.layout = QVBoxLayout()
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(5)
        self.tableWidget.setVerticalHeaderLabels(["current_states", "desired_states", "input_x", "previous_setpoints", "environment_state"])
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_file_changes)
        self.timer.start(1000)  # Час у мілісекундах
        self.load_queue()

    def load_queue(self):
        with open(self.filename, 'rb') as f:
            data_list = np.load(f, allow_pickle=True)
            self.tableWidget.setColumnCount(len(data_list))
            for current_column_count, data in enumerate(data_list):
                num_parts = int(data[-2])
                current_states = data[:num_parts]
                desired_states = data[num_parts : 2*num_parts]
                input_x = data[2*num_parts : 3*num_parts]
                previous_setpoints = data[3*num_parts : 4*num_parts]
                environment_state = data[-1]
                self.tableWidget.setItem(0, current_column_count, QTableWidgetItem(str(current_states)))
                self.tableWidget.setItem(1, current_column_count, QTableWidgetItem(str(desired_states)))
                self.tableWidget.setItem(2, current_column_count, QTableWidgetItem(str(input_x)))
                self.tableWidget.setItem(3, current_column_count, QTableWidgetItem(str(previous_setpoints)))
                self.tableWidget.setItem(4, current_column_count, QTableWidgetItem(str(environment_state)))

        # Встановлюємо політику розміру
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def check_file_changes(self):
        current_modified_time = os.path.getmtime(self.filename) 
        if current_modified_time != self.last_modified_time:
            self.last_modified_time = current_modified_time
            self.load_queue()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    ex = QueueVisualization('data_queue.npy')
    ex.show()
    sys.exit(app.exec_())
