import logging
from collections import deque
from datetime import datetime

import numpy as np
import zmq
import json

logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self, on_receive=None, buffer_size=1):
        """Initialize a gigafrost receiver.

        Args:
            on_receive (function, optional): Execute function with each received metadata and image
                as input arguments. Defaults to None.
            buffer_size (int, optional): A number of last received zmq messages to keep in memory.
                Defaults to 1.
        """
        self.buffer = deque(maxlen=buffer_size)
        self.state = "polling"
        self.on_receive = on_receive
        print("init receiver")

    def start(self, io_threads, connection_mode, address):
        """Start the receiver loop.

        Args:
            io_threads (int): The size of the zmq thread pool to handle I/O operations.
            connection_mode (str): Use either 'connect' or 'bind' zmq_socket methods.
            address (str): The address string, e.g. 'tcp://127.0.0.1:9001'.

        Raises:
            RuntimeError: Unknown connection mode.
        """
        zmq_context = zmq.Context(io_threads=io_threads)
        zmq_socket = zmq_context.socket(zmq.SUB)  # pylint: disable=E1101
        zmq_socket.setsockopt_string(zmq.SUBSCRIBE, u"")  # pylint: disable=E1101

        if connection_mode == "connect":
            zmq_socket.connect(address)
        elif connection_mode == "bind":
            zmq_socket.bind(address)
        else:
            raise RuntimeError("Unknown connection mode {connection_mode}")

        # poller = zmq.Poller()
        # poller.register(zmq_socket, zmq.POLLIN)

        while True:
            # events = dict(poller.poll(1000))
            # if zmq_socket not in events:
            #     self.state = "polling"
            #     print('zmq socket not in events')
            #     continue

            time_poll = datetime.now()
            # metadata = zmq_socket.recv_json(flags=0)
            metadata = zmq_socket.recv_multipart()
            print(json.loads(metadata[0].decode()))
            # image = zmq_socket.recv(flags=0, copy=False, track=False)
            # metadata["time_poll"] = time_poll
            # metadata["time_recv"] = datetime.now() - time_poll

            # dtype = metadata.get("type")
            # shape = metadata.get("shape")
            # if dtype is None or shape is None:
            #     logger.error("Cannot find 'type' and/or 'shape' in received metadata")
            #     continue

            # image = np.frombuffer(image.buffer, dtype=dtype).reshape(shape)


            self.state = "receiving"

            # if some treatment on the data is necessary
            # if self.on_receive is not None:
            #     self.on_receive(metadata, image)

