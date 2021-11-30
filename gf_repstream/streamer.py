#!/usr/bin/env python
import json
import logging
import time
import zmq
import sys

logger = logging.getLogger(__name__)


class Streamer:
    def __init__(self, name, deque, sentinel, port,
                 zmq_mode, mode_metadata, idle_time=1):
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

    def add_writer_header(self, metadata):
        metadata['image_attributes']['image_number'] = self._counter
        metadata['frame'] = self._counter
        metadata['output_file'] = "/home/dbe/git/sf_daq_buffer/gf/output.h5"
        metadata['run_id'] = 0
        metadata['n_images'] = 10000
        metadata['i_image'] = self._counter
        metadata['status'] = 0
        metadata['detector_name'] = 'Gigafrost'
        return metadata

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
                data = self._deque.popleft()
                # FIXME: adjusts to test the std-det-writer
                if self._name == 'std-det-writer':
                    zmq_socket.send_json(
                        self.add_writer_header(
                            json.loads(
                                data[0].decode())),
                        flags=zmq.SNDMORE)
                    zmq_socket.send(data[1], flags=0)
                else:
                    zmq_socket.send_multipart(data)
                self._counter += 1
            else:
                # nothing to stream
                time.sleep(self._idle_time)
        logger.debug(f"End signal received... finishing streamer thread...")
