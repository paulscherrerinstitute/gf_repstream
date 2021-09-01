import logging
from collections import deque
from datetime import datetime

import numpy as np
import zmq
import json

logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self, deque):
        """Initialize a gigafrost receiver.

        Args:
            deque (double ended queue): Queue of received zmq packets
        """
        self._deque = deque

    def start(self, io_threads, connection_mode, address):
        """Start the receiver loop.

        Args:
            io_threads (int): The size of the zmq thread pool to handle I/O operations.
            connection_mode (str): Use either 'connect' or 'bind' zmq_socket methods.
            address (str): The address string, e.g. 'tcp://127.0.0.1:9001'.

        Raises:
            RuntimeError: Unknown connection mode.
            RuntimeError: Unknown metadata format.
        """
        logger.debug(f'GF_repstream.Receiver class with: io_threads {io_threads}, connection_mode {connection_mode} and address {address}')

        zmq_context = zmq.Context(io_threads=io_threads)
        zmq_socket = zmq_context.socket(zmq.SUB)  # pylint: disable=E1101
        zmq_socket.setsockopt_string(zmq.SUBSCRIBE, u"")  # pylint: disable=E1101

        if connection_mode == "connect":
            zmq_socket.connect(address)
        elif connection_mode == "bind":
            zmq_socket.bind(address)
        else:
            raise RuntimeError("Unknown connection mode {connection_mode}")

        while True:
            # receives the data
            data = zmq_socket.recv_multipart()
            # json metadata
            metadata = json.loads(data[0].decode())
            # basic verification of the metadata
            dtype = metadata.get("type")
            shape = metadata.get("shape")
            source = metadata.get("source")
            # print(dtype,shape)
            if dtype is None or shape is None or source != 'gigafrost':
                logger.error("Cannot find 'type' and/or 'shape' and/or 'source' in received metadata")
                raise RuntimeError("Metadata problem...")
            # appends the received message to the global Deque
            self._deque.append(data)
            # print(f'Deque size after appending: {len(self._deque)}')
            logger.debug(f'Deque size after appending: {len(self._deque)}')
                
