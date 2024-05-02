from random import randint
import numpy as np
import queue
import time

def save_queue(data_queue, filename):
    with open(filename, 'wb') as f:
        data_list = list(data_queue.queue)
        np.save(f, data_list)
        
max_queue_size = 4     
data_queue = queue.Queue(maxsize=max_queue_size)


while True:
    num_parts = 4
    current_state = randint(1,10)
    desired_state = randint(1,10)
    environment_state = randint(1,10)
    initial_data = np.zeros(2 * num_parts + 4)
    initial_data[0] = current_state
    initial_data[1] = desired_state
    initial_data[2] = num_parts
    initial_data[3] = environment_state
    data_queue.put(initial_data)
    save_queue(data_queue, 'data_queue.npy')
    if data_queue.qsize() == max_queue_size:
        data_queue.get()
    time.sleep(2)
    


print(data_queue.queue)

save_queue(data_queue, 'data_queue.npy')
