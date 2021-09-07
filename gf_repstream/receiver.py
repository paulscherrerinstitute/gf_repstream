#!/usr/bin/env python
import logging
import zmq

from gf_repstream.protocol import TestMetadata

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

    def _decode_metadata(self, metadata):
        source = metadata.get("source")
        if source == 0:
            metadata['source'] = 'gigafrost'
        return metadata

    def _stop(self):
        self.join()

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

        while not self._sentinel.is_set():
            # receives the data
            data = zmq_socket.recv_multipart()
            # binary metadata converted            
            metadata = self._decode_metadata(TestMetadata.from_buffer_copy(data[0]).as_dict())

            # basic verification of the metadata
            dtype = metadata.get("type")
            shape = metadata.get("shape")
            source = metadata.get("source")
            image_frame = metadata.get("frame")
            if dtype is None or shape is None or source != "gigafrost":
                logger.error(
                    "Cannot find 'type' and/or 'shape' and/or 'source' in received metadata"
                )
                raise RuntimeError("Metadata problem...")

            for idx, stream in enumerate(self._streamer_tuples):
                if image_frame % stream[1] == 0:
                    stream[0].append(data)
                    logger.debug(
                        f"Receiver added image: {image_frame} to queue {idx}."
                    )
        logger.debug(f"End signal received... finishing receiver thread...")
        self._stop()
        
