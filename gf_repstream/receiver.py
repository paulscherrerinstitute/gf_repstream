#!/usr/bin/env python
import logging
import json
import zmq
import time

from protocol import GFHeader

_logger = logging.getLogger("RestStreamRepeater")


class Receiver:
    def __init__(self, tuples_list, sentinel, zmq_mode, frame_block):
        """Initialize a gigafrost receiver.

        Args:
            tuples_list: List of touples containing an Streamer class object and the send_every_nth parameter of this class.
            sentinel: Flag object to halt execution.

        """
        _logger.debug(
                f"RepStreamer.Receiver __init__ ..."
            )
        self._streamer_tuples = tuples_list
        self._sentinel = sentinel
        self._zmq_mode = zmq_mode
        self._frame_block = frame_block

    def _decode_metadata(self, metadata):
        source = metadata.get("source")
        if source == 0:
            metadata["source"] = "gigafrost"
        return metadata

    def timePassed(self, oldtime, seconds):

        currenttime = time.time()
        if currenttime - oldtime > seconds:
            return True
        else:
            return False

    def start(self, io_threads, address):
        """Start the receiver loop.

        Args:
            io_threads (int): The size of the zmq thread pool to handle I/O operations.
            address (str): The address string, e.g. 'tcp://127.0.0.1:9001'.

        Raises:
            RuntimeError: Unknown metadata format.
        """
        _logger.debug(
            f"GF_repstream.Receiver start (io_threads {io_threads} and address {address} (zmq mode {self._zmq_mode}))"
        )

        # prepares the zmq socket to receive data
        zmq_context = zmq.Context(io_threads=io_threads)
        if self._zmq_mode.upper() == "SUB":
            zmq_socket = zmq_context.socket(zmq.SUB)
            zmq_socket.setsockopt_string(zmq.SUBSCRIBE, u"")
        elif self._zmq_mode.upper() == "PULL":
            zmq_socket = zmq_context.socket(zmq.PULL)
        else:
            raise RuntimeError(
                "Receiver input zmq mode not recognized (SUB/PULL).")

        zmq_socket.connect(address)
        zmq_socket.setsockopt(zmq.LINGER, -1)
        send_flag = [False for i in range(len(self._streamer_tuples))]
        frame_counter = 0
        stride_counter = 0
        send_every_sec_counter = [0 for i in range(len(self._streamer_tuples))]
        while not self._sentinel.is_set():
            # receives the data
            data = zmq_socket.recv_multipart()
            try:
                metadata = json.loads(data[0].decode())
                image_frame = metadata["frame"]
            except BaseException:
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
                    if send_flag[idx]:
                        stride_counter += 1
                        if stride_counter <= stream_param:
                            stream[0].append(data)
                        elif stride_counter == 2 * stream_param:
                            send_flag[idx] = False
                    else:
                        if image_frame % stream_param == 0:
                            send_flag[idx] = True
                            stride_counter = 1
                            stream[0].append(data)
                elif stream_mode == "send_every_nth_frame":
                    # mode send_every_nth_frame: sends Y frames every N frames
                    # Y: self._frame_block (defined on the init for now)
                    # N: send_output_param
                    if send_flag[idx]:
                        frame_counter += 1
                        stream[0].append(data)
                        if frame_counter == self._frame_block:
                            send_flag[idx] = False
                            frame_counter = 0
                    else:
                        if image_frame % stream_param == 0:
                            send_flag[idx] = True
                            frame_counter = 1
                            stream[0].append(data)
                elif stream_mode == "send_every_sec":
                    # wait for seconds
                    if send_flag[idx]:
                        if self.timePassed(
                                send_every_sec_counter[idx], stream_param):
                            send_flag[idx] = False
                    else:
                        send_every_sec_counter[idx] = time.time()
                        send_flag[idx] = True
                        stream[0].append(data)

        _logger.debug(f"End signal received... finishing receiver thread...")
