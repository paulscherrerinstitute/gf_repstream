#!/usr/bin/env python
import argparse
import logging
import os
import zmq
import sys
import json
from pathlib import Path
from collections import deque
from functools import partial
from threading import Thread, Event
from time import sleep

# from gf_repstream import __version__
from receiver import Receiver
from streamer import Streamer


class SRepeater(object):
    """ The multithreaded stream repeater object class that receives
    an incoming stream and multiplexes it into multiple outputs with
    different characteristics.
    """

    def __init__(
            self,
            in_address="tcp://xbl-daq-23:9990",
            in_zmq_mode='PULL',
            io_threads=1,
            buffer_size=5000,
            n_output_streams=None,
            send_output_mode=None,
            send_output_param=None,
            mode_metadata='gf',
            config_file=None,
            logger=None):
        """[summary]

        Args:
            in_address (str, optional): Incoming ZMQ address. Defaults to "tcp://xbl-daq-23:9990".
            in_zmq_mode (int, optional): Incoming ZMQ mode. Defaults to PULL.
            io_threads (int, optional): ZMQ IO threads. Defaults to 1.
            buffer_size (int, optional): ZMQ buffer size. Defaults to 5000.
            n_output_streams (int, optional): Number of output streams. Defaults to None.
            send_output_mode (list, optional): List containing the ZMQ mode of the generated output streams. Defaults to None.
            send_output_param (list, optional): List containing the output streams configuration parameter. Defaults to None.
            mode_metadata (str, optional): [description]. Defaults to 'gf'.
            config_file (str, optional): Path to the config file. Defaults to None.
            logger (obj, optional): Logging class. Defaults to None.

        Raises:
            RuntimeError: The object can't go on if the configuration file is not defined.
        """
        self._in_address = in_address
        self._in_zmq_mode = in_zmq_mode
        self._io_threads = io_threads
        self._buffer_size = buffer_size
        self._n_output_streams = n_output_streams
        self._send_output_mode = send_output_mode
        self._send_output_param = send_output_param
        self._stream_ports = []
        self._zmq_modes = []
        self._stream_names = []
        self._mode_metadata = mode_metadata
        self._config_file = config_file
        # not part of config
        self._logger = logger
        self._exit_event = Event()
        self._list_threads = []

        # load config file
        if self._config_file is not None:
            self.load_config()
        else:
            raise RuntimeError('Failed to load the config file.')

    def __iter__(self):
        """Dictionary description of the streamer object class

        Yields:
            Prepares a list of the internal variables of the streamer object with name and value
        """
        ignore_list = ['_exit_event', '_logger', '_list_threads']
        # first start by grabbing the Class items
        iters = dict((x, y)
                     for x, y in self.__dict__.items() if (x[:2] != '__'))
        # then update the class items with the instance items
        iters.update(self.__dict__)
        # now 'yield' through the items
        for x, y in iters.items():
            if x not in ignore_list:
                yield x, y

    def get_config(self):
        """Gets the configuration of the streamer object.

        Returns:
            dict: dictionary containing the configuration of the streamer object class.
        """
        return dict(self)

    def load_config(self):
        """Loads a configuration based on the config file defined.
        If configures the incoming stream parameters (address and mode) and
        prepares the configuration for the outgoing output streams (addresses, modes, and output modes)

        Raises:
            RuntimeError: Zmq mode not recognized (PUSH or PUB).
            RuntimeError: Streamer object config file with problems.
        """
        # loads config
        with open(self._config_file) as f:
            # FIXME: static default file shipped with conda package
            # needs to be imported using pkg_resources
            # for now, full path to the local file
            json_config = json.load(f)
            self._send_output_param = []
            self._send_output_mode = []
            self._stream_names = []
            self._zmq_modes = []
            self._send_output_mode = []
            try:
                # prepares the input stream parameters
                self._in_address = json_config['in-stream']['address']
                self._in_zmq_mode = json_config['in-stream']['zmq_mode']
                for i in json_config['out-streams']:
                    out_dict = json_config['out-streams'][i]
                    self._stream_names.append(i)
                    self._send_output_param.append(
                        out_dict['send_output_param'])
                    self._send_output_mode.append(out_dict['send_output_mode'])
                    if out_dict['zmq_mode'].upper() == 'PUSH':
                        self._zmq_modes.append(zmq.PUSH)
                    elif out_dict['zmq_mode'].upper() == 'PUB':
                        self._zmq_modes.append(zmq.PUB)
                    else:
                        raise RuntimeError(
                            "Zmq mode not recognized (PUSH or PUB).")
                    self._stream_ports.append(out_dict['port'])
            except Exception as e:
                raise RuntimeError("Gf_repstream config file with problems.")
            self._n_output_streams = len(json_config['out-streams'])
        return

    def set_config_file(self, path_config_file):
        """Sets a new configuration file path.

        Args:
            path_config_file (str): Path to the configuration file that will be stored.
        """
        self._config_file = path_config_file
        self.load_config()
        return

    def start(self):
        """Starts the threaded receiver and streamers based on the configuration file previously provided.


        Raises:
            RuntimeError: When number of output paramers and streamers are not correct.
        """
        if self._exit_event.is_set():
            self._exit_event.clear()
        q_list = []
        streamer_list = []
        receiver_tuples = []
        if self._n_output_streams == 0:
            raise RuntimeError(
                "Number of output streams must be greater than zero. Halting execution of gf_repstream."
            )
        if self._n_output_streams != len(
                self._send_output_param) != len(self._send_output_mode):
            raise RuntimeError(
                "Problem with the number of output streams, modes and parameters. They must be identical."
            )

        for i in range(self._n_output_streams):
            # deque for each output stream
            q_list.append(deque(maxlen=self._buffer_size))
            # stramer outputs the replicated zmq stream
            streamer_list.append(
                Streamer(
                    name=self._stream_names[i],
                    deque=q_list[-1],
                    sentinel=self._exit_event,
                    port=self._stream_ports[i],
                    zmq_mode=self._zmq_modes[i],
                    mode_metadata=self._mode_metadata
                )
            )
            receiver_tuples.append(
                (q_list[-1], (self._send_output_mode[i], self._send_output_param[i])))

        # Receiver object with the streamer and their queues
        receiver = Receiver(tuples_list=receiver_tuples,
                            sentinel=self._exit_event,
                            mode=self._mode_metadata,
                            zmq_mode=self._in_zmq_mode)

        # Prepares receiver thread
        start_receiver = partial(
            receiver.start,
            self._io_threads,
            self._in_address)
        r = Thread(target=start_receiver, daemon=True)

        self._list_threads = []
        for i in range(self._n_output_streams):
            start_streamer_thread = partial(
                streamer_list[i].start, self._io_threads, "tcp://*:" +
                str(self._stream_ports[i])
            )
            self._list_threads.append(
                Thread(
                    target=start_streamer_thread,
                    daemon=True))

        # Main application - starting receiver and streamers
        r.start()
        for i in range(self._n_output_streams):
            self._list_threads[i].start()

        return

    def stop(self):
        """ Signal that stops the receiver and streamer threads.
        """
        self._exit_event.set()
        return
