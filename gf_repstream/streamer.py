#!/usr/bin/env python
import json
import logging
import time
import zmq
import sys

from utils import valid_writer_config

_logger = logging.getLogger("RestStreamRepeater")


class Streamer:
    def __init__(
        self,
        name,
        deque,
        sentinel,
        port,
        zmq_mode,
        zmq_context,
        writer_config,
        idle_time=1,
    ):
        """Initialize a streamer thread.

        Args:
            name: name of the streamer thread
            deque: shared deque from which the data will be fetched.
            sentinel: Flag object to halt execution.
            port: Port that will be used for this thread's stream
            zmq_mode: Zmq socket mode of this thread's stream (PUB, PULL)
            zmq_context: Zmq context
            writer_config: Dictionary that contains the writer configuration parameters.
            idle_time: idle time to wait when the queue is empty
        """
        self._name = name
        self._deque = deque
        self._idle_time = idle_time
        self._last_sent_frame = -1
        self._counter = 0
        self._alive = False
        self._sentinel = sentinel
        self._port = port
        self._zmq_mode = zmq_mode
        self._zmq_context = zmq_context
        self._writer_config = writer_config
        _logger.debug(
            f"RepStream.Streamer at port {self._port} (zmq mode {self._zmq_mode})"
        )

    

    def add_writer_header(self, metadata):
        """
        Method to add the metadata header into the stream. 
        Note: This is a workaround for the usage of the std-det-writer
        without the writer_agent component from the std-daq.
        The header information is defined via the repeater stream rest api 
        interface.
        """
        metadata["image_attributes"]["image_number"] = self._counter
        metadata["frame"] = self._counter
        metadata["output_file"] = self._writer_config["output_file"]
        metadata["run_id"] = self._writer_config["run_id"]
        metadata["n_images"] = self._writer_config["n_images"]
        metadata["i_image"] = self._counter
        metadata["status"] = 0
        metadata["detector_name"] = self._writer_config["detector_name"]
        return metadata

    def start(self):
        """
        Start the streamer loop.
        """

        address = "tcp://*:"+(str(self._port))
        _logger.debug(
            f"RepStream.Streamer {self._name} starting to stream at {address}... "
        )

        
        
        # prepares the zmq socket to send out data PUB/SUB (bind)
        self._sentinel.clear()
        # zmq_context = zmq.Context(io_threads=self._io_threads)
        # zmq_context = 
        zmq_socket = self._zmq_context.socket(self._zmq_mode)
        zmq_socket.setsockopt(zmq.LINGER, -1)
        try:
            zmq_socket.bind(address)
        except zmq.error.ZMQError:
            _logger.debug(f"RepStream.Streamer socket can't bind to address ({address}).")
            pass

        while not self._sentinel.is_set():
            if self._deque:
                data = self._deque.popleft()
                # FIXME: adjusts to test the std-det-writer
                if self._name == "std-det-writer":
                    zmq_socket.send_json(
                        self.add_writer_header(json.loads(data[0].decode())),
                        flags=zmq.SNDMORE,
                    )
                    zmq_socket.send(data[1], flags=0)
                else:
                    zmq_socket.send_multipart(data)
                self._counter += 1
            else:
                # nothing to stream
                time.sleep(self._idle_time)
        zmq_socket.close()
        _logger.debug(f"RepStream.Streamer {self._name} closing thread...")
