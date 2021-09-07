#!/usr/bin/env python
import random
import time
import zmq
import sys
from _ctypes import Structure
from ctypes import c_uint64, c_uint16

from gf_repstream.protocol import TestMetadata

def main(out_address):
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUB)
    zmq_socket.bind(out_address)
    zmq_socket.setsockopt(zmq.LINGER, -1)
    time.sleep(3)
    # Start your result manager and workers before you start your producers
    for num in range(1000):
        data_message = bytearray(random.getrandbits(8) for _ in range(1024))
        # zmq_socket.send_multipart([json.dumps(metadata).encode("utf-8"), data_message])
        zmq_socket.send_multipart([bytes(TestMetadata(num, 1, 0, 0, 760864, 2, 0)), data_message])
        time.sleep(0.01)
    time.sleep(1)
    zmq_socket.close()

if __name__ == "__main__":
    out_address = sys.argv[1]
    main(out_address)
