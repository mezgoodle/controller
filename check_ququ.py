import json
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
    def __init__(self, filename, config):
        super().__init__()
        self.filename = filename
        self.last_modified_time = os.path.getmtime(filename)
        self.simul = self.QueueSimulation(filename, config)
        self.simul.simulate()
        self.wathced_index = self.simul.get_watched_index()
        self.initUI()

    def initUI(self):

        self.setWindowTitle(
            f"Queue Visualization for controller {self.wathced_index}"
        )
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
        self.form_tab = self.FormTab(self.simul, self.filename)
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
        def __init__(self, simul_object, filename):
            super().__init__()
            self.layout = QVBoxLayout()
            self.simul = simul_object
            self.filename = filename

            # Додавання елементів форми (приклад)
            self.desired_state_label = QLabel("Бажаний стан:")
            self.desired_state = QLineEdit()
            self.other_coordinators_label = QLabel(
                "Стан інших координаторів(через кому):"
            )
            self.other_coordinators = QLineEdit()
            self.environment_state_label = QLabel(
                "Стан навколишнього середовища"
            )
            self.environment_state = QLineEdit()
            self.button_save = QPushButton("Зберегти")

            self.layout.addWidget(self.desired_state_label)
            self.layout.addWidget(self.desired_state)
            self.layout.addWidget(self.other_coordinators_label)
            self.layout.addWidget(self.other_coordinators)
            self.layout.addWidget(self.environment_state_label)
            self.layout.addWidget(self.environment_state)
            self.layout.addWidget(self.button_save)

            self.setLayout(self.layout)

            # Додавання обробників подій (за потреби)
            self.button_save.clicked.connect(self.make_a_step)

        def make_a_step(self):
            last_current_state = None
            with open(self.filename, "rb") as f:
                data_list = np.load(f, allow_pickle=True)
                last_current_state = data_list[-1][0]
            # Обробка збереження даних з форми
            desired_state = self.desired_state.text()
            environment_state = self.environment_state.text()
            other_coordinators = self.other_coordinators.text()
            # ... checks
            self.simul.simulate(
                current_state=last_current_state,
                desired_state=int(desired_state),
                environment_state=int(environment_state),
                other_states=list(map(int, other_coordinators.split(","))),
            )

    class QueueSimulation:
        def save_queue(self, data_queue):
            with open(self.filename, "wb") as f:
                data_list = list(data_queue.queue)
                np.save(f, data_list)

        @staticmethod
        def read_config(filename):
            with open(filename, "r") as f:
                config = json.load(f)
            return config

        def __init__(self, filename, config):
            config_data = self.read_config(config)
            self.max_queue_size = config_data["num_parts"]
            self.filename = filename
            self.watched_index = randint(0, self.max_queue_size - 1) + 1
            self.data_queue = queue.Queue(maxsize=self.max_queue_size)

        def get_watched_index(self):
            return self.watched_index

        def simulate(
            self,
            current_state=0,
            desired_state=0,
            environment_state=0,
            other_states=[],
        ):
            # while True:
            if current_state:
                current_state = (
                    sum(other_states) + current_state + environment_state
                ) / (len(other_states) + 2) + desired_state
            num_parts = self.max_queue_size
            current_state = current_state or randint(1, 10)
            desired_state = desired_state or randint(1, 10)
            environment_state = environment_state or randint(1, 10)
            initial_data = np.zeros(2 * num_parts + self.max_queue_size)
            initial_data[0] = current_state
            initial_data[1] = desired_state
            initial_data[2] = num_parts
            initial_data[3] = environment_state
            self.data_queue.put(initial_data)
            self.save_queue(self.data_queue)
            if self.data_queue.qsize() == self.max_queue_size:
                self.data_queue.get()
            # time.sleep(2)


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    data_filename = "data_queue.npy"

    # Показати форму введення тексту
    input_form = InputForm()
    if input_form.exec_() == QDialog.Accepted:
        config = input_form.filename
        ex = QueueVisualization(data_filename, config)
        # Запустити головне вікно
        ex.show()
        sys.exit(app.exec_())
