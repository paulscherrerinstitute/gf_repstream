#!/usr/bin/env python
import json
import sys
import time
import zmq

from gf_repstream.protocol import TestMetadata

def main(backend):
    # Socket to talk to server
    context = zmq.Context(io_threads=1)
    if mode.upper() == 'SUB':
        socket = context.socket(zmq.SUB)
        socket.setsockopt_string(zmq.SUBSCRIBE, u"")
    elif mode.upper() == 'PULL':
        socket = context.socket(zmq.PULL)
    else:
        raise RuntimeError(
            "Mode not recognized (SUB or PULL). Halting executing..."
        )
    socket.connect(backend)
    
    # Process 5 updates
    total_recvs = 0
    while True:
        data = socket.recv_multipart()
        metadata = TestMetadata.from_buffer_copy(data[0]).as_dict()
        print(metadata,total_recvs)
        total_recvs += 1

if __name__ == "__main__":
    backend = sys.argv[1]
    mode = sys.argv[2]
    main(backend)
