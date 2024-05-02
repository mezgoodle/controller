import os
import queue
import sys
import time
from random import randint

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

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

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
        self.tab_widget.addTab(self.tableWidget, "Черга")
        self.form_tab = FormTab()
        self.tab_widget.addTab(self.form_tab, "Форма")

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
        print(f"Name: {name}, Age: {age}")


class InputForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Введіть шлях до файлу")
        self.layout = QVBoxLayout()
        self.label = QLabel("Введіть шлях до файлу:")
        self.input_path = QLineEdit()
        self.button = QPushButton("Продовжити")
        self.error_label = QLabel(
            ""
        )  # Мітка для виведення повідомлення про помилку
        self.error_label.setStyleSheet(
            "color: red;"
        )  # Червоний колір для повідомлення про помилку

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input_path)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.error_label)  # Додаємо мітку для помилки
        self.setLayout(self.layout)

        self.button.clicked.connect(self.check_file)  # Змінюємо обробник події

    def check_file(self):
        file_path = self.input_path.text()
        self.filename = file_path
        if os.path.isfile(file_path):
            self.accept()  # Закриває форму, якщо файл існує
        else:
            self.error_label.setText(
                "Файл не знайдено!"
            )  # Повідомлення про помилку


class QueueSimulation:
    def save_queue(data_queue, filename):
        with open(filename, "wb") as f:
            data_list = list(data_queue.queue)
            np.save(f, data_list)

    def __init__(self):
        self.max_queue_size = 4
        self.data_queue = queue.Queue(maxsize=self.max_queue_size)

    def start_simulation(self, data_queue):
        while True:
            num_parts = 4
            current_state = randint(1, 10)
            desired_state = randint(1, 10)
            environment_state = randint(1, 10)
            initial_data = np.zeros(2 * num_parts + 4)
            initial_data[0] = current_state
            initial_data[1] = desired_state
            initial_data[2] = num_parts
            initial_data[3] = environment_state
            data_queue.put(initial_data)
            self.save_queue(data_queue, "data_queue.npy")
            if data_queue.qsize() == self.max_queue_size:
                data_queue.get()
            time.sleep(2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())

    # Показати форму введення тексту
    input_form = InputForm()
    if input_form.exec_() == QDialog.Accepted:
        text = input_form.filename
        # ... (використати введений текст, наприклад, передати його в QueueVisualization)

        # Запустити головне вікно
        ex = QueueVisualization("data_queue.npy")
        ex.show()
        sys.exit(app.exec_())
