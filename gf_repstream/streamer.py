#!/usr/bin/env python
import json
import logging
import time
import zmq
import sys

logger = logging.getLogger(__name__)


class Streamer:
    def __init__(self, name, deque, sentinel, port, zmq_mode, mode_metadata, idle_time=1):
        """Initialize a gigafrost streamer.

        Args:
            name: name of the streamer
            deque: shared deque that data will be fetched from
            sentinel: Flag object to halt execution.
            idle_time: idle time to wait when the queue is empty
        """
        self._name = name
        self._deque = deque
        self._idle_time = idle_time
        self._last_sent_frame = -1
        self._counter = 0
        self._sentinel = sentinel
        self._port = port
        self._zmq_mode = zmq_mode
        self._mode_metadata = mode_metadata

    def start(self, io_threads, address):
        """Start the streamer loop.

        Args:
            io_threads (int): The size of the zmq thread pool to handle I/O operations.
            address (str): The address string, e.g. 'tcp://127.0.0.1:9001'.

        """

        logger.debug(
            f"GF_repstream.Streamer with: io_threads {io_threads} and address {address} (zmq mode {self._zmq_mode})"
        )

        # prepares the zmq socket to send out data PUB/SUB (bind)
        zmq_context = zmq.Context(io_threads=io_threads)
        zmq_socket = zmq_context.socket(self._zmq_mode)
        zmq_socket.bind(address)
        zmq_socket.setsockopt(zmq.LINGER, -1)

        while not self._sentinel.is_set():
            if self._deque:
                # peek without removing the data from the queue
                data = self._deque.popleft()
<<<<<<< HEAD
                # metadata = json.loads(data[0].decode())
                # image_frame = metadata['frame']
                self._counter += 1
                # logger.debug(
                #     f"{self._name} streamer send out image: {image_frame} (counter {self._counter}, mode {self._zmq_mode}, port {self._port})"
                # )
=======
>>>>>>> 6f94d0c41e2675dae35e16269345d6da0cfaa9fc
                zmq_socket.send_multipart(data)
            else:
                # nothing to stream
                time.sleep(self._idle_time)
        logger.debug(f"End signal received... finishing streamer thread...")
