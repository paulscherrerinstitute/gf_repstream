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

            for idx, stream in enumerate(self._streamer_tuples):
                # stream output mode
                stream_mode = stream[1][0]
                # stream output param
                stream_param = stream[1][1]
                if stream_mode == "send_every_nth":
                    # mode strides: sends 1 frame every nth
                    if image_frame % stream_param == 0:
                        stream[0].append(data)
                elif stream_mode == "strides":
                    # mode strides: sends n frames and skip the next n frames
                    # n = send_output_param
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
                    # mode send_every_nth_frame: sends Y frames every N frames
                    # Y: self._frame_block (defined on the init for now)
                    # N: send_output_param
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

        logger.debug(f"End signal received... finishing receiver thread...")

