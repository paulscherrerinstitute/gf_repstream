import logging
from collections import deque
from datetime import datetime
import time
import numpy as np
import zmq
import json

logger = logging.getLogger(__name__)


class Streamer:
    def __init__(self, name, deque, idle_time=1):
        """Initialize a gigafrost streamer.

        Args:
            queue: queue shared among receiver/sender threads.
            send_every_nth: 
        """
        self._name = name
        self._deque = deque
        self._idle_time = idle_time
        self._last_sent_frame = -1
        self._counter = 1

    def start(self, io_threads, address):
        """Start the streamer loop.

        Args:
            io_threads (int): The size of the zmq thread pool to handle I/O operations.
            address (str): The address string, e.g. 'tcp://127.0.0.1:9001'.

        """

        logger.debug(f'GF_repstream.Streamer with: io_threads {io_threads} and address {address}')

        zmq_context = zmq.Context(io_threads=io_threads)
        zmq_socket = zmq_context.socket(zmq.PUB)  # pylint: disable=E1101
        zmq_socket.bind(address)

        while True:
            if len(self._deque) != 0:
                # peek without removing the data from the queue
                data = self._deque.pop()
                # gets the image_frame
                image_frame = json.loads(data[0].decode()).get('frame')
                # verifies if it's repeated
                if self._last_sent_frame != image_frame:
                    self._counter += 1
                    self._last_sent_frame = image_frame
                    self._counter = 1
                    logger.debug(f'Streamer got image: {image_frame}')
                    print(f'{self._name} streamer send out image: {image_frame} (counter {self._counter})' )
                    zmq_socket.send_multipart(data)
            else:
                # nothing to stream
                time.sleep(self._idle_time)



