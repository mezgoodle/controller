import json
import queue
import struct
import sys
from abc import ABC, abstractmethod
from random import randint

import numpy as np
from loguru import logger

logger.remove(0)
logger.add("loguru.log", format="{time} | {message} dasdasd")


class Coordinator(ABC):
    def __init__(self, config_file, coordinator_index, filename):
        # Store the filename for data storage
        self.filename = filename
        # Завантаження конфігурації
        with open(config_file) as f:
            config = json.load(f)
        # Зчитуваня розмірності й інші параметри з конфігурації
        self.num_parts = config["num_parts"]
        self.influence_matrix = np.array(config["influence_matrix"])
        self.resource_vector = np.array(config["resource_vector"])
        assert (
            len(self.resource_vector) == self.num_parts
        ), "Розмірності ресурсоємності не співпадають"
        assert self.influence_matrix.shape == (
            self.num_parts,
            self.num_parts,
        ), "Розмірності матриці взаємодії не співпадають"

        logger.info(
            ":".join(
                [f"Coordinator-{coordinator_index}", "Proccess-Initialized"]
            )
        )
        # Індекс координатора
        self.coordinator_index = coordinator_index

        # Ініціалізація черги
        self.data_queue = queue.Queue(maxsize=self.num_parts)

        # Ініціалізація портів (замініть на власну реалізацію)
        self.sensor_port = self._initialize_sensor_port()
        self.environment_port = self._initialize_environment_port()
        self.communication_ports = self._initialize_communication_ports()
        self.regulator_port = self._initialize_regulator_port()

        # Отримання початкових даних
        current_state = self._receive_from_sensor()
        environment_state = self._receive_from_environment_sensor()

        # Створення початкового вектора даних
        initial_data = np.zeros(4 * self.num_parts + 2)
        initial_data[self.coordinator_index] = current_state
        initial_data[-1] = environment_state
        initial_data[-2] = self.num_parts

        # Додавання даних в чергу
        self.data_queue.put(initial_data)

    def _initialize_sensor_port(self) -> int:
        # ... реалізація ініціалізації порту для сенсора
        return randint(1, 3)

    def _initialize_environment_port(self) -> int:
        # ... реалізація ініціалізації порту для сенсора оточуючого середовища
        return randint(1, 3)

    def _initialize_communication_ports(self) -> list[int]:
        # ... реалізація ініціалізації портів для зв'язку з іншими ЛСК
        return [randint(1, 3) for _ in range(randint(1, 10))]

    def _initialize_regulator_port(self) -> int:
        # ... реалізація ініціалізації порту для зв'язку з регулятором
        return randint(1, 3)

    def _receive_from_sensor(self, port_index=0) -> int:
        # ... реалізація отримання даних від сенсора через порт
        return randint(port_index, 3)

    def _receive_from_environment_sensor(self) -> int:
        # ... реалізація отримання даних від сенсора оточуючого середовища через порт
        return randint(1, 3)

    def receive_data(self, data_source_index):
        # Temporary implementation of getting data from another coordinator
        decoded_data = self.temp_get_data()

        # # Отримання даних від іншої ЛСК через порт
        # vector = self._receive_from_communication_port(data_source_index)
        # # Декодування та додавання в чергу
        # # ...
        # # Приклад:
        # decoded_data = self._decode_data(vector)
        if self.data_queue.full():
            # Обробка ситуації, коли черга повна (наприклад, видалення найстарішого елемента)
            self.data_queue.get()

        self.data_queue.put(decoded_data)
        # Append data to the file
        with open(self.filename, "wb") as f:
            data_list = list(self.data_queue.queue)
            np.save(f, data_list)
        with open(self.filename, "rb") as f:
            data_list = np.load(f, allow_pickle=True)
            print(data_list)

    def temp_get_data(self):
        data = np.zeros(4 * self.num_parts + 2)
        data[self.coordinator_index] = int(input("Enter desired state: "))
        data[-1] = int(input("Enter environment state: "))
        data[-2] = self.num_parts
        return data

    def _receive_from_communication_port(self, port_index):
        # ... реалізація отримання даних від іншої ЛСК через порт
        return self._receive_from_sensor(port_index)

    def send_data(self, data):
        # ... кодування та відправка даних іншим ЛСК
        for port in self.communication_ports:
            binary_data = self._encode_data(data)
            self._send_to_communication_port(port, binary_data)

    def _send_to_communication_port(self, port, data):
        # ... реалізація відправки даних іншим ЛСК через порт
        pass

    def send_setpoint(self, setpoint):
        # ... кодування уставки (як раніше)
        vector = self._decode_data(setpoint)
        self._send_to_regulator_port(vector)

    def _send_to_regulator_port(self, data):
        # ... реалізація відправки уставки на регулятор через порт
        pass

    def _encode_data(self, data):
        # Конвертація в бінарний формат з фіксованою точкою (16 біт, Q8.8)
        binary_data = b"".join(struct.pack("<h", int(x * 256)) for x in data)
        return binary_data

    def _decode_data(self, binary_data):
        # Конвертація з бінарного формату з фіксованою точкою (16 біт, Q8.8)
        data = (
            np.array(
                struct.unpack(
                    "<" + "h" * (len(str(binary_data)) // 2), binary_data
                )
            )
            / 256
        )
        return data

    def coordination_function(self):
        # Отримання даних з черги
        data = self.data_queue.get()
        # Обчислення уставки
        # ...
        # Приклад:
        setpoint = self.calculate_setpoint_for_LSC(data)
        # Кодування уставки в бінарний формат
        # ...
        binary_output = self._encode_data(setpoint)
        # Append setpoint to the file
        with open(self.filename, "ab") as f:
            np.save(f, binary_output, allow_pickle=True)
        return binary_output

    @abstractmethod
    def calculate_setpoint_for_LSC(self):
        pass


class Setpoint(Coordinator):
    def calculate_setpoint_for_LSC(self):
        # Отримання даних з черги
        data = self.data_queue.get()
        current_states = data[: self.num_parts]
        desired_states = data[self.num_parts : 2 * self.num_parts]
        input_x = data[2 * self.num_parts : 3 * self.num_parts]
        previous_setpoints = data[3 * self.num_parts : 4 * self.num_parts]
        environment_state = data[-1]

        # Приклади методів координації (з використанням розпакованих даних)

        # 1. Модель системи
        system_model = self._system_model(
            current_states, input_x, environment_state
        )

        # 2. Оцінювання параметрів
        estimated_parameters = self._estimate_parameters(
            system_model, current_states, previous_setpoints
        )

        # 3. Прогнозування параметрів
        predicted_parameters = self._predict_parameters(estimated_parameters)

        # 4. Оптимізація уставки
        optimized_setpoint = self._optimize_setpoint(
            system_model, predicted_parameters, desired_states
        )

        # 5. Критерій оптимальності (перевірка)
        if not self._check_optimality_criteria(
            optimized_setpoint, system_model, desired_states
        ):
            # ... обробка ситуації, коли критерій оптимальності не виконаний
            pass

        return optimized_setpoint

    def _system_model(self, current_states, input_x, environment_state):
        # ... реалізація моделі системи
        return randint(1, 3)

    def _estimate_parameters(
        self, system_model, current_states, previous_setpoints
    ):
        # ... реалізація оцінювання параметрів
        return randint(1, 3)

    def _predict_parameters(self, estimated_parameters):
        # ... реалізація прогнозування параметрів
        return randint(1, 3)

    def _optimize_setpoint(
        self, system_model, predicted_parameters, desired_states
    ):
        # ... реалізація оптимізації уставки
        return randint(1, 3)

    def _check_optimality_criteria(
        self, setpoint, system_model, desired_states
    ):
        # ... реалізація перевірки критерію оптимальності
        return randint(1, 3)


s1 = Setpoint("config.json", 0, "data_queue1.npy")
s2 = Setpoint("config.json", 1, "data_queue2.npy")
s3 = Setpoint("config.json", 2, "data_queue3.npy")
s4 = Setpoint("config.json", 3, "data_queue4.npy")
while True:
    from time import sleep

    print("For the first")
    s1.receive_data(0)
    print("For the second")
    s2.receive_data(0)
    print("For the third")
    s3.receive_data(0)
    print("For the fourth")
    s4.receive_data(0)
    sleep(1)
