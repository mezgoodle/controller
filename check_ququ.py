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
    def __init__(self, file_prefix, num_files):
        super().__init__()
        self.file_prefix = file_prefix
        self.num_files = num_files
        self.last_modified_times = [
            os.path.getmtime(f"{self.file_prefix}{i+1}.npy")
            for i in range(num_files)
        ]
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Queue Visualization")
        self.showFullScreen()  # Відображення на повний екран

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.layout = QVBoxLayout(self.centralWidget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Створення кнопки
        self.button = QPushButton("Зробити ітерацію", self)
        self.button.setGeometry(50, 50, 200, 50)

        # Прикріплення обробника події до кнопки
        self.button.clicked.connect(self.openForm)

        self.layout.addWidget(self.button)

        # Створення вкладок для кожного файлу
        for i in range(self.num_files):
            file_name = f"{self.file_prefix}{i+1}.npy"
            tab = QWidget()
            self.tabs.addTab(tab, f"Координатор {i+1}")
            self.initTab(tab, file_name)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_file_changes)
        self.timer.start(1000)  # Час у мілісекундах

    def initTab(self, tab, filename):
        layout = QVBoxLayout()
        tableWidget = QTableWidget()
        tableWidget.setRowCount(5)
        tableWidget.setVerticalHeaderLabels(
            [
                "current_states",
                "desired_states",
                "input_x",
                "previous_setpoints",
                "environment_state",
            ]
        )
        layout.addWidget(tableWidget)
        tab.setLayout(layout)

        self.load_queue(tableWidget, filename)

    def load_queue(self, tableWidget, filename):
        with open(filename, "rb") as f:
            data_list = np.load(f, allow_pickle=True)
            tableWidget.setColumnCount(
                len(data_list[0])
            )  # Fixing the issue here
            for current_column_count, data in enumerate(data_list):
                num_parts = int(data[-2])
                current_states = data[:num_parts]
                desired_states = data[num_parts : 2 * num_parts]
                input_x = data[2 * num_parts : 3 * num_parts]
                previous_setpoints = data[3 * num_parts : 4 * num_parts]
                environment_state = data[-1]
                tableWidget.setItem(
                    0,
                    current_column_count,
                    QTableWidgetItem(str(current_states)),
                )
                tableWidget.setItem(
                    1,
                    current_column_count,
                    QTableWidgetItem(str(desired_states)),
                )
                tableWidget.setItem(
                    2, current_column_count, QTableWidgetItem(str(input_x))
                )
                tableWidget.setItem(
                    3,
                    current_column_count,
                    QTableWidgetItem(str(previous_setpoints)),
                )
                tableWidget.setItem(
                    4,
                    current_column_count,
                    QTableWidgetItem(str(environment_state)),
                )

        # Встановлення політики розміру
        tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def check_file_changes(self):
        for i in range(self.num_files):
            current_modified_time = os.path.getmtime(
                f"{self.file_prefix}{i+1}.npy"
            )
            if current_modified_time != self.last_modified_times[i]:
                self.last_modified_times[i] = current_modified_time
                tableWidget = (
                    self.tabs.widget(i).layout().itemAt(0).widget()
                )  # Fixing the issue here
                self.load_queue(tableWidget, f"{self.file_prefix}{i+1}.npy")

    def openForm(self):
        # Створення та відображення форми
        self.form = FormDialog(self)
        self.form.show()


class FormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Форма введення даних")
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout()

        # Додавання елементів форми (наприклад, текстового поля та кнопки)
        self.label = QLabel("Введіть стан навколишнього середовища:", self)
        layout.addWidget(self.label)

        self.line_edit = QLineEdit(self)
        layout.addWidget(self.line_edit)

        self.submit_button = QPushButton("Підтвердити", self)
        print(self.line_edit.text())
        self.submit_button.clicked.connect(self.submitForm)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def submitForm(self):
        # Отримання даних з поля введення
        entered_text = self.line_edit.text()
        print("Введені дані:", entered_text)

        # Закриття форми
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    ex = QueueVisualization(
        "data_queue", 4
    )  # Замініть 4 на кількість файлів, які вам потрібно відобразити
    ex.show()
    sys.exit(app.exec_())
