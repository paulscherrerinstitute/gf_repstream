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

from gf_repstream import __version__
from gf_repstream.receiver import Receiver
from gf_repstream.streamer import Streamer

Log_Format = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(
    format=Log_Format, filename="gf_repstream.log", filemode="w", level=logging.DEBUG
)

logger = logging.getLogger(__name__)

exit_event = Event()


def main():
    """The gf stream send command line interface.
    This is a tool to receive the incoming gigafrost stream and replicate it
    to external components.
    """

    # Prepare argument parser
    parser = argparse.ArgumentParser(
        prog="gf_repstream", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--in-address",
        metavar="PROTOCOL://HOST:PORT",
        type=str,
        default="tcp://xbl-daq-23:9990",
        help="an address string for zmq socket",
    )

    parser.add_argument(
        "--in-zmq-mode",
        type=str,
        default="PULL",
        help="Input stream zmq mode (SUB or PULL)",
    )

    parser.add_argument(
        "--out-init-port",
        type=int,
        default="9610",
        help="the initial port for the output streams (increased by 1 for every other stream)",
    )

    parser.add_argument(
        "--io-threads",
        type=int,
        default=1,
        help="the size of the zmq thread pool to handle I/O operations",
    )

    parser.add_argument(
        "--buffer-size",
        type=int,
        default=100,
        help="a number of last received zmq messages to keep in memory",
    )

    parser.add_argument(
        "--n-output-streams",
        type=int,
        default=0,
        help="number of output streams to be generated",
    )

    parser.add_argument(
        "--send-every-nth",
        nargs="+",
        type=int,
        help="list containing the frequency of each output stream to be generated",
    )

    parser.add_argument(
        '--mode-metadata', 
        default='gf', 
        type=str,
        help='Incoming header data.'
    )

    parser.add_argument(
        "--config-file",
        type=str,
        default=None,
        help="A gf_repstream config file"
    )

    args = parser.parse_args()

    zmq_modes = []
    stream_ports = []
    stream_names= []

    # config file has priority over the cli commands
    if args.config_file is not None and Path(args.config_file).exists() :
        with open(args.config_file) as f:
            json_config = json.load(f)
            args.send_every_nth = []
            try:
                # prepares the input stream parameters
                args.in_address = json_config['in-stream']['address']
                args.in_zmq_mode = json_config['in-stream']['zmq_mode']
                for i in json_config['out-streams']:
                    out_dict = json_config['out-streams'][i]
                    stream_names.append(i)
                    args.send_every_nth.append(out_dict['send_every_nth'])
                    if out_dict['zmq_mode'].upper() == 'PUSH':
                        zmq_modes.append(zmq.PUSH)
                    elif out_dict['zmq_mode'].upper() == 'PUB':
                        zmq_modes.append(zmq.PUB)
                    else:
                        raise RuntimeError("Zmq mode not recognized (PUSH or PUB).")
                    stream_ports.append(out_dict['port'])
            except Exception as e:
                raise RuntimeError("Gf_repstream config file with problems.")
            args.n_output_streams = len(json_config['out-streams'])

    q_list = []
    streamer_list = []
    receiver_tuples = []

    if args.n_output_streams == 0:
        raise RuntimeError(
            "Number of output streams must be greater than zero. Halting execution of gf_repstream."
        )
    if args.n_output_streams != len(args.send_every_nth):
        raise RuntimeError(
            "Number of output streams must be identical to the length of the send_every_nth list. Halting execution of gf_repstream."
        )

    # default for zmq_modes (1st push, else pub)
    if zmq_modes:
        for i in range(args.n_output_streams):
            mode = zmq.PUB
            if i == 0:
                mode = zmq.PUSH
            zmq_modes.append(mode)

    # ports definition
    if stream_ports:
        for i in range(args.n_output_streams):
            stream_ports.append(args.out_init_port + i)

    if stream_names:
        for i in range(args.n_output_streams):
            stream_names.append(f"output_{i}_{zmq_modes[i]}")

    for i in range(args.n_output_streams):
        # deque for each output stream
        q_list.append(deque(maxlen=args.buffer_size))
        # stramer outputs the replicated zmq stream
        streamer_list.append(
            Streamer(
                name=stream_names[i],
                deque=q_list[-1], 
                sentinel=exit_event, 
                port=stream_ports[i],
                zmq_mode=zmq_modes[i],
                mode_metadata=args.mode_metadata
            )
        )
        receiver_tuples.append((q_list[-1], args.send_every_nth[i]))

    # Receiver object with the streamer and their queues
    receiver = Receiver(tuples_list=receiver_tuples, 
                        sentinel=exit_event, 
                        mode=args.mode_metadata,
                        zmq_mode=args.in_zmq_mode)

    # Prepares receiver thread
    start_receiver = partial(receiver.start, args.io_threads, args.in_address)
    r = Thread(target=start_receiver, daemon=True)

    list_threads = []
    init_port = args.out_init_port
    for i in range(args.n_output_streams):
        start_streamer_thread = partial(
            streamer_list[i].start, args.io_threads, "tcp://*:" + str(stream_ports[i])
        )
        list_threads.append(Thread(target=start_streamer_thread, daemon=True))

    # Main application - starting receiver and streamers
    r.start()
    for i in range(args.n_output_streams):
        list_threads[i].start()

    while not exit_event.is_set():
        try:
            sleep(0.1)
        except KeyboardInterrupt:
            logger.debug("^C pressed... halting execution of gf_repstream")
            exit_event.set()

    sleep(1)
    logger.debug("CLI finishing...")


if __name__ == "__main__":
    main()
