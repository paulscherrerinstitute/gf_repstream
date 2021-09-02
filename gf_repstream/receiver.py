import logging
from collections import deque
from datetime import datetime

import numpy as np
import zmq
import json

logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self, tuples_list, sentinel):
        """Initialize a gigafrost receiver.

        Args:
            tuples_list: List of touples containing an Streamer class object and the send_every_nth parameter of this class. 

        """
        self._streamer_tuples = tuples_list
        # self._deque_writer = writer_tuple[0]
        # self._writer_send_every_nth = writer_tuple[1]
        # self._deque_preview = preview_tuple[0]
        # self._preview_send_every_nth = preview_tuple[1]
        # self._deque_analysis = analysis_tuple[0]
        # self._analysis_send_every_nth = analysis_tuple[1]
        self._sentinel = sentinel

    # def __str__ (self):
        # return f'Receiver(_deque_writer={self._deque_writer},_writer_send_every_nth={self._writer_send_every_nth},_deque_preview={self._deque_preview},_preview_send_every_nth={self._preview_send_every_nth},_deque_analysis={self._deque_analysis},_analysis_send_every_nth={self._analysis_send_every_nth}' 


    def start(self, io_threads, address):
        """Start the receiver loop.

        Args:
            io_threads (int): The size of the zmq thread pool to handle I/O operations.
            address (str): The address string, e.g. 'tcp://127.0.0.1:9001'.

        Raises:
            RuntimeError: Unknown metadata format.
        """
        logger.debug(f'GF_repstream.Receiver class with: io_threads {io_threads} and address {address}')

        zmq_context = zmq.Context(io_threads=io_threads)
        zmq_socket = zmq_context.socket(zmq.SUB)  # pylint: disable=E1101
        zmq_socket.setsockopt_string(zmq.SUBSCRIBE, u"")  # pylint: disable=E1101
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
            # print(dtype,shape)
            if dtype is None or shape is None or source != 'gigafrost':
                logger.error("Cannot find 'type' and/or 'shape' and/or 'source' in received metadata")
                raise RuntimeError("Metadata problem...")


            for stream in self._streamer_tuples:
                if image_id%stream[1] == 0:
                    stream[0].appendleft(data)
            # appends the received message to the deques
            # if image_id%self._writer_send_every_nth == 0:
            #     # print(f'adding {image_id} to writer')
            #     self._deque_writer.appendleft(data)
            #     logger.debug(f'Writer Deque size after appending: {len(self._deque_writer)}')
            #     # print(f'Writer Deque size after appending: {len(self._deque_writer)}')
            # if image_id%self._preview_send_every_nth == 0:
            #     # print(f'adding {image_id} to preview')
            #     self._deque_preview.appendleft(data)
            #     logger.debug(f'Preview Deque size after appending: {len(self._deque_preview)}')
            #     # print(f'Preview Deque size after appending: {len(self._deque_preview)}')
            # if image_id%self._analysis_send_every_nth == 0:
            #     # print(f'adding {image_id} to analysis')
            #     self._deque_analysis.appendleft(data)
            #     logger.debug(f'Analysis Deque size after appending: {len(self._deque_analysis)}')
                # print(f'Analysis Deque size after appending: {len(self._deque_analysis)}')
            

        logger.debug(f'End signal received... finishing receiver thread...')
        print(f'End signal received... finishing receiver thread...')