import json
import logging
import time
import zmq

logger = logging.getLogger(__name__)

class Streamer:
    def __init__(self, name, deque, sentinel, idle_time=1):
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
        self._counter = 1
        self._sentinel = sentinel

    def start(self, io_threads, address):
        """Start the streamer loop.

        Args:
            io_threads (int): The size of the zmq thread pool to handle I/O operations.
            address (str): The address string, e.g. 'tcp://127.0.0.1:9001'.

        """

        logger.debug(
            f"GF_repstream.Streamer with: io_threads {io_threads} and address {address}"
        )

        # prepares the zmq socket to send out data PUB/SUB (bind)
        zmq_context = zmq.Context(io_threads=io_threads)
        zmq_socket = zmq_context.socket(zmq.PUB)
        zmq_socket.bind(address)

        while self._sentinel is not None:
            if len(self._deque) != 0:
                # peek without removing the data from the queue
                data = self._deque.pop()
                # gets the image_frame
                image_frame = json.loads(data[0].decode()).get("frame")
                # verifies if it's repeated
                if self._last_sent_frame != image_frame:
                    self._counter += 1
                    self._last_sent_frame = image_frame
                    logger.debug(
                        f"{self._name} streamer send out image: {image_frame} (counter {self._counter})"
                    )
                    zmq_socket.send_multipart(data)
            else:
                # nothing to stream
                time.sleep(self._idle_time)
        logger.debug(f"End signal received... finishing streamer thread...")
