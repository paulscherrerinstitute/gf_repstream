#!/usr/bin/env python
import logging
import json
import zmq

from gf_repstream.protocol import GFHeader

logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self, tuples_list, sentinel, mode, zmq_mode):
        """Initialize a gigafrost receiver.

        Args:
            tuples_list: List of touples containing an Streamer class object and the send_every_nth parameter of this class.
            sentinel: Flag object to halt execution.

        """
        self._streamer_tuples = tuples_list
        self._sentinel = sentinel
        self._mode = mode
        self._zmq_mode = zmq_mode
        # FIXME: correct gigafrost frame size
        self._frame_block = 200

    def _decode_metadata(self, metadata):
        source = metadata.get("source")
        if source == 0:
            metadata["source"] = "gigafrost"
        return metadata

    def start(self, io_threads, address):
        """Start the receiver loop.

        Args:
            io_threads (int): The size of the zmq thread pool to handle I/O operations.
            address (str): The address string, e.g. 'tcp://127.0.0.1:9001'.

        Raises:
            RuntimeError: Unknown metadata format.
        """
        logger.debug(
            f"GF_repstream.Receiver class with: io_threads {io_threads} and address {address} (zmq mode {self._zmq_mode})"
        )

        # prepares the zmq socket to receive data
        zmq_context = zmq.Context(io_threads=io_threads)
        if self._zmq_mode.upper() == "SUB":
            zmq_socket = zmq_context.socket(zmq.SUB)
            zmq_socket.setsockopt_string(zmq.SUBSCRIBE, u"")
        elif self._zmq_mode.upper() == "PULL":
            zmq_socket = zmq_context.socket(zmq.PULL)
        else: 
            raise RuntimeError("Receiver input zmq mode not recognized (SUB/PULL).")



        zmq_socket.connect(address)
        zmq_socket.setsockopt(zmq.LINGER, -1)

        while not self._sentinel.is_set():
            # receives the data
            data = zmq_socket.recv_multipart()
            # binary metadata converted
            try:
                metadata = json.loads(data[0].decode())
            except:
                raise RuntimeError("Problem decoding the Metadata...")

<<<<<<< HEAD
            for idx, stream in enumerate(self._streamer_tuples):
                # stream output mode
                stream_mode = stream[1][0]
                # stream output param
                stream_param = stream[1][1]
                if stream_mode == "send_every_nth":
                    if image_frame % stream_param == 0:
                        stream[0].append(data)
                elif stream_mode == "strides":
                    if send_flag:
                        stride_counter = +1
                        stream[0].append(data)
                        if stride_counter == stream_param:
                            send_flag = False
                            stride_counter = 0
                    else:
                        if image_frame % stream_param == 0:
                            send_flag = True
                            stride_counter = 1
                            stream[0].append(data)
                elif stream_mode == "send_every_nth_frame":
                    if send_flag:
                        frame_counter += 1
                        stream[0].append(data)
                        if frame_counter == self._frame_block:
                            send_flag = False
                            frame_counter = 0
                    else:
                        if image_frame % stream_param == 0:
                            send_flag = True
                            frame_counter = 1
                            stream[0].append(data)

=======
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
                    if stream[1] == 1:
                         print(f"adding {image_frame} to queue {idx}")
                    logger.debug(f"Receiver added image: {image_frame} to queue {idx}.")
>>>>>>> 6f94d0c41e2675dae35e16269345d6da0cfaa9fc
        logger.debug(f"End signal received... finishing receiver thread...")

