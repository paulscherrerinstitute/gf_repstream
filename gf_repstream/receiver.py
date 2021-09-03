import json
import logging

import zmq

logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self, tuples_list, sentinel):
        """Initialize a gigafrost receiver.

        Args:
            tuples_list: List of touples containing an Streamer class object and the send_every_nth parameter of this class.
            sentinel: Flag object to halt execution.

        """
        self._streamer_tuples = tuples_list
        self._sentinel = sentinel

    def start(self, io_threads, address):
        """Start the receiver loop.

        Args:
            io_threads (int): The size of the zmq thread pool to handle I/O operations.
            address (str): The address string, e.g. 'tcp://127.0.0.1:9001'.

        Raises:
            RuntimeError: Unknown metadata format.
        """
        logger.debug(
            f"GF_repstream.Receiver class with: io_threads {io_threads} and address {address}"
        )

        # prepares the zmq socket to receive data
        zmq_context = zmq.Context(io_threads=io_threads)
        zmq_socket = zmq_context.socket(zmq.SUB)
        zmq_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        zmq_socket.connect(address)

        while self._sentinel is not None:
            # receives the data
            data = zmq_socket.recv_multipart()
            # json metadata
            metadata = json.loads(data[0].decode())
            # basic verification of the metadata
            dtype = metadata.get("type")
            shape = metadata.get("shape")
            source = metadata.get("source")
            image_id = metadata.get("frame")
            if dtype is None or shape is None or source != "gigafrost":
                logger.error(
                    "Cannot find 'type' and/or 'shape' and/or 'source' in received metadata"
                )
                raise RuntimeError("Metadata problem...")

            for stream in self._streamer_tuples:
                if image_id % stream[1] == 0:
                    stream[0].appendleft(data)

        logger.debug(f"End signal received... finishing receiver thread...")
