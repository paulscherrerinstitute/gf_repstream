#!/usr/bin/env python
import json
import sys
import time
import zmq
import argparse
from gf_repstream.protocol import TestMetadata


def main():

    parser = argparse.ArgumentParser(description='Consumer GF Stream')

    parser.add_argument('-a', '--address', default="tcp://localhost:9610", type=str,
                        help='Address - format "tcp://<address>:<port>" (default: "tcp://localhost:9999")')
    parser.add_argument('-m', '--mode', default='pull', type=str,
                        help='Communication mode - either push (default) or pub')
    parser.add_argument('-f', '--format', default='file', type=str,
                        help='Incoming header data.')

    arguments = parser.parse_args()

    in_address = arguments.address
    mode = arguments.mode
    header = arguments.format 

    # Socket to talk to server
    context = zmq.Context(io_threads=1)
    if mode.upper() == "SUB":
        socket = context.socket(zmq.SUB)
        socket.setsockopt_string(zmq.SUBSCRIBE, u"")
    elif mode.upper() == "PULL":
        socket = context.socket(zmq.PULL)
    else:
        raise RuntimeError("Mode not recognized (SUB or PULL). Halting executing...")
    socket.connect(in_address)

    total_recvs = 0
    
    try:
        while True:
            if header == 'file':
                data = socket.recv_multipart()
                metadata = json.loads(data[0].decode())
                print(metadata)
                total_recvs += 1
                print("total recvs", total_recvs)
            else:
                data = socket.recv_multipart()
                metadata = TestMetadata.from_buffer_copy(data[0]).as_dict()
                print(metadata, total_recvs)
                total_recvs += 1
                print("total recvs", total_recvs)
    except KeyboardInterrupt:
        pass
        

if __name__ == "__main__":
    main()
