#!/usr/bin/env python
import json
import sys
import time
import zmq
import argparse
#from gf_repstream.protocol import TestMetadata


def main():

    parser = argparse.ArgumentParser(description='Consumer GF Stream')

    parser.add_argument('-a', '--address', default="tcp://localhost:9610", type=str,
                        help='Address "tcp://<address>:<port>" (default: "tcp://localhost:9999")')
    parser.add_argument('-m', '--mode', default='pull', type=str,
                        help='Communication mode - either pull (default) or sub')
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
            data = socket.recv_multipart()
            metadata = json.loads(data[0].decode())
            total_recvs += 1
            print(metadata['n_images'])
            print(total_recvs, metadata['i_image'])
    except KeyboardInterrupt:
        pass
        

if __name__ == "__main__":
    main()
