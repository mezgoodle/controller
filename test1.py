import os

import numpy as np


class QueueVisualization:
    def __init__(self, master, filename):
        self.master = master
        self.filename = filename
        self.last_modified_time = None

        self.load_queue_and_display()

        # Перевіряємо зміни у файлі кожну секунду
        self.check_file_changes()

    def load_queue_and_display(self):
        # Завантажуємо чергу з файлу та відображаємо її в таблиці
        with open(self.filename, "rb") as f:
            data_list = np.load(f, allow_pickle=True)

            # Проходимося по кожному елементу черги та відображаємо їх
            for idx, data in enumerate(data_list):
                num_parts = int(data[-2])
                current_states = data[:num_parts]
                desired_states = data[num_parts : 2 * num_parts]
                input_x = data[2 * num_parts : 3 * num_parts]
                previous_setpoints = data[3 * num_parts : 4 * num_parts]
                environment_state = data[-1]
                print(
                    current_states,
                    desired_states,
                    input_x,
                    previous_setpoints,
                    environment_state,
                )
                # self.tree.insert(
                #     "",
                #     "end",
                #     text=str(idx + 1),
                #     values=(
                #         current_states,
                #         desired_states,
                #         input_x,
                #         previous_setpoints,
                #         environment_state,
                #     ),
                # )

    def check_file_changes(self):
        import time

        time.sleep(1)
        # Перевіряємо зміни у файлі. Якщо файл змінився, оновлюємо відображення даних
        current_modified_time = os.path.getmtime(self.filename)
        if current_modified_time != self.last_modified_time:
            self.last_modified_time = current_modified_time
            self.load_queue_and_display()

        # Перевіряємо зміни у файлі кожну секунду
        for i in range(10):
            self.check_file_changes()


q = QueueVisualization("config.json", "test_data.npy")
