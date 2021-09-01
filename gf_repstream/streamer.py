import logging
from collections import deque
from datetime import datetime
import time
import numpy as np
import zmq
import json

logger = logging.getLogger(__name__)


class Streamer:
    def __init__(self, name, deque, send_every_nth=1, idle_time=1):
        """Initialize a gigafrost streamer.

        Args:
            queue: queue shared among receiver/sender threads.
            send_every_nth: 
        """
        self._name = name
        self._deque = deque
        self._send_every_nth = send_every_nth
        self._idle_time = idle_time
        self._last_frame = -1
        self._counter = 1

    def start(self, io_threads, connection_mode, address):
        """Start the streamer loop.

        Args:
            io_threads (int): The size of the zmq thread pool to handle I/O operations.
            connection_mode (str): Use either 'connect' or 'bind' zmq_socket methods.
            address (str): The address string, e.g. 'tcp://127.0.0.1:9001'.

        Raises:
            RuntimeError: Unknown connection mode.
        """

        logger.debug(f'GF_repstream.Streamer with: io_threads {io_threads}, connection_mode {connection_mode} and address {address}')

        zmq_context = zmq.Context(io_threads=io_threads)
        zmq_socket = zmq_context.socket(zmq.PUB)  # pylint: disable=E1101

        if connection_mode == "connect":
            zmq_socket.connect(address)
        elif connection_mode == "bind":
            zmq_socket.bind(address)
        else:
            raise RuntimeError("Unknown connection mode {connection_mode}")

        while True:
            if len(self._deque) != 0:
                # peek without removing the data from the queue
                data = self._deque[-1]
                # gets the image_frame
                image_frame = json.loads(data[0].decode()).get('frame')
                # verifies if it's repeated
                # print(f'{self._name}, {self._last_frame},', image_frame)
                if self._last_frame != image_frame:
                    self._counter += 1
                    # print(f'{self._name}, {self._counter}, {self._send_every_nth} ', self._counter%self._send_every_nth == 0)
                    if self._counter%self._send_every_nth == 0:
                        self._last_frame = image_frame
                        self._counter = 1
                        logger.debug(f'Streamer got image: {image_frame}')
                        # print(f'{self._name} streamer send out image: {image_frame}')
                        zmq_socket.send_multipart(data)
                    else:
                        time.sleep(0.5)
            else:
                # nothing to stream
                time.sleep(self._idle_time)



