import json
import random
import time

import zmq


def fake_stream():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUB)
    zmq_socket.bind("tcp://*:9609")
    time.sleep(3)
    # Start your result manager and workers before you start your producers
    for num in range(1000):
        # metadata = { 'num' : num }
        print(num)
        metadata = {
            "frame": num,
            "source": "gigafrost",
            "shape": [760, 864],
            "htype": ["array-1.0"],
            "type": "uint16",
        }
        data_message = bytearray(random.getrandbits(8) for _ in range(1024))
        zmq_socket.send_multipart([json.dumps(metadata).encode("utf-8"), data_message])
        time.sleep(0.02)

    print("finished")
    zmq_socket.close()


fake_stream()
