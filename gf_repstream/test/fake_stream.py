#!/usr/bin/env python
import numpy as np
import random
import time
import zmq
import sys
import json
from os import listdir
from os.path import isfile, join
import argparse

from gf_repstream.protocol import TestMetadata


def main():
    parser = argparse.ArgumentParser(description='Fake GF Stream')

    parser.add_argument('-f', '--folder', default="", type=str, help='Destination folder containing the raw files')
    parser.add_argument('-a', '--address', default="tcp://*:9609", type=str,
                        help='Address - format "tcp://<address>:<port>" (default: "tcp://*:9609")')
    parser.add_argument('-m', '--mode', default='push', type=str,
                        help='Communication mode - either push (default) or pub')

    parser.add_argument('-i', '--n-images', default=100, type=int,
                        help='Number of images to be streamed')

    arguments = parser.parse_args()

    folder = arguments.folder
    out_address = arguments.address
    mode = arguments.mode
    n_images = arguments.n_images
    total_images = 1000

    context = zmq.Context()

    if mode.upper() == "PUSH":
        zmq_socket = context.socket(zmq.PUSH)
    elif mode.upper() == "PUB":
        zmq_socket = context.socket(zmq.PUB)
    else:
        raise RuntimeError("Mode not recognized (SUB or PULL). Halting executing...")
    
    zmq_socket.bind(out_address)
    zmq_socket.setsockopt(zmq.LINGER, 1000)
    time.sleep(1)
    if folder == '':
        # Start your result manager and workers before you start your producers
        for num in range(1000):
            data_message = bytearray(random.getrandbits(8) for _ in range(1024))
            # zmq_socket.send_multipart([json.dumps(metadata).encode("utf-8"), data_message])
            zmq_socket.send_multipart(
                [bytes(TestMetadata(num, 1, 0, 0, 760864, 2, 0)), data_message]
            )
            time.sleep(0.01)
        time.sleep(1)
    else:
        counter = 0
        while True:
            try: 
                files = sorted(listdir(folder))
                for index, raw_file in enumerate(files):
                    filename = join(folder, raw_file)
                    if not (raw_file.endswith('.raw') and isfile(filename)):
                        continue

                    with open(filename, mode='rb') as file_handle:
                        time.sleep(.1)
                        send_more = False
                        if index + 1 < len(files):  # Ensure that we don't run out of bounds
                            send_more = raw_file.split('_')[0] == files[index + 1].split('_')[0]
                        if send_more:
                            header = json.loads(file_handle.read().decode())
                            header['image_attributes']['image_number'] = counter
                            header['frame'] = counter
                            # provisory details for std-det-writer header
                            header['output_file'] = "/tmp/output_test.h5"

                            # uint64 is not serializable 
                            # sending int for now
                            header['run_id'] = 0 
                            header['n_images'] = n_images
                            header['i_image'] = counter
                            header['status'] = 0
                            header['detector_name'] = 'Gigafrost'
                            zmq_socket.send_json(header, flags=zmq.SNDMORE)
                            print(f'frame {counter} sent out...')
                            counter += 1
                        else:
                            zmq_socket.send(file_handle.read(), flags=0)
                    # else:
                    #     break
            except KeyboardInterrupt:
                break

    zmq_socket.close()




if __name__ == "__main__":
    main()
