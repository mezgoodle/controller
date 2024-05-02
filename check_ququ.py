import os
import sys

import numpy as np
import qdarkstyle
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class QueueVisualization(QMainWindow):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.last_modified_time = os.path.getmtime(filename)
        self.initUI()

    def initUI(self):

        self.setWindowTitle("Queue Visualization")
        self.resize(800, 300)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.layout = QVBoxLayout(self.centralWidget)
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(5)
        self.tableWidget.setVerticalHeaderLabels(
            [
                "real_states",
                "desired_states",
                "input_x",
                "setpoints",
                "environment_state",
            ]
        )
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_file_changes)
        self.timer.start(1000)  # Час у мілісекундах
        self.load_queue()

    def load_queue(self):
        with open(self.filename, "rb") as f:
            data_list = np.load(f, allow_pickle=True)
            self.tableWidget.setColumnCount(len(data_list))
            for current_column_count, data in enumerate(data_list):
                num_parts = int(data[2])
                real_states = data[0]
                desired_states = data[1]
                input_x = data[num_parts : 2 * num_parts]
                setpoints = data[2 * num_parts : 3 * num_parts]
                environment_state = data[3]
                self.tableWidget.setItem(
                    0, current_column_count, QTableWidgetItem(str(real_states))
                )
                self.tableWidget.setItem(
                    1,
                    current_column_count,
                    QTableWidgetItem(str(desired_states)),
                )
                self.tableWidget.setItem(
                    2, current_column_count, QTableWidgetItem(str(input_x))
                )
                self.tableWidget.setItem(
                    3, current_column_count, QTableWidgetItem(str(setpoints))
                )
                self.tableWidget.setItem(
                    4,
                    current_column_count,
                    QTableWidgetItem(str(environment_state)),
                )

        # Встановлюємо політику розміру
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def check_file_changes(self):
        current_modified_time = os.path.getmtime(self.filename)
        if current_modified_time != self.last_modified_time:
            self.last_modified_time = current_modified_time
            self.load_queue()


class FormTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Додавання елементів форми (приклад)
        self.label_name = QLabel("Ім'я:")
        self.input_name = QLineEdit()
        self.label_age = QLabel("Вік:")
        self.input_age = QLineEdit()
        self.button_save = QPushButton("Зберегти")

        self.layout.addWidget(self.label_name)
        self.layout.addWidget(self.input_name)
        self.layout.addWidget(self.label_age)
        self.layout.addWidget(self.input_age)
        self.layout.addWidget(self.button_save)

        self.setLayout(self.layout)

        # Додавання обробників подій (за потреби)
        self.button_save.clicked.connect(self.save_data)

    def save_data(self):
        # Обробка збереження даних з форми
        name = self.input_name.text()
        age = self.input_age.text()
        # ... (збереження даних)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    ex = QueueVisualization("data_queue.npy")
    ex.show()
    sys.exit(app.exec_())
