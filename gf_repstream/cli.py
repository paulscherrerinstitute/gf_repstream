import argparse
import logging
import os
import sys
import pkgutil
from functools import partial
from threading import Thread
from collections import deque
from time import time, sleep

from gf_repstream import __version__
from gf_repstream.receiver import Receiver
from gf_repstream.streamer import Streamer
# from gf_repstream.custom_queue import PriorityQueue

Log_Format = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(format=Log_Format, level=logging.ERROR, stream = sys.stdout)
logger = logging.getLogger(__name__)


def main():
    """The gf stream send command line interface.
    This is a tool to receive the incoming gigafrost stream and replicate it
    to external components.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))

    # Prepare argument parser
    parser = argparse.ArgumentParser(
        prog="gf_repstream", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    parser.add_argument(
        "--in-address",
        metavar="PROTOCOL://HOST:PORT",
        type=str,
        default="tcp://xbl-daq-23:9990",
        help="an address string for zmq socket",
    )

    parser.add_argument(
        "--out-address",
        metavar="PROTOCOL://HOST:PORT",
        type=str,
        default="tcp://*:9610",
        help="an address string for zmq socket",
    )

    parser.add_argument(
        "--in-connection-mode",
        type=str,
        choices=["connect", "bind"],
        default="connect",
        help="whether to bind a socket to an address or connect to a remote socket with an address",
    )

    parser.add_argument(
        "--out-connection-mode",
        type=str,
        choices=["connect", "bind"],
        default="bind",
        help="whether to bind a socket to an address or connect to a remote socket with an address",
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
        default=2000,
        help="a number of last received zmq messages to keep in memory",
    )

    args = parser.parse_args()

    q = deque(maxlen=args.buffer_size)

    logger.debug(f'Shared queue {q}')

    # Receiver gets messages via zmq stream
    receiver = Receiver(deque=q)
    # stramer outputs the replicated zmq stream 
    streamer_writer = Streamer(name='writer', deque=q, send_every_nth=1)
    streamer_preview = Streamer(name='preview', deque=q, send_every_nth=5)
    streamer_analysis = Streamer(name='analysis', deque=q, send_every_nth=10)
    

    # receiver
    start_receiver = partial(receiver.start, args.io_threads, args.in_connection_mode, args.in_address)
    r = Thread(target=start_receiver, daemon=True)
    # streamer writer
    start_streamer_writer = partial(streamer_writer.start, args.io_threads, args.out_connection_mode, 'tcp://*:9610')
    s_writer = Thread(target=start_streamer_writer, daemon=True)
    
    # streamer live preview
    start_streamer_preview = partial(streamer_preview.start, args.io_threads, args.out_connection_mode, 'tcp://*:9611')
    s_preview = Thread(target=start_streamer_preview, daemon=True)

    # streamer analysis
    start_streamer_analysis = partial(streamer_analysis.start, args.io_threads, args.out_connection_mode, 'tcp://*:9612')
    s_analysis = Thread(target=start_streamer_analysis, daemon=True)

    # Main application - starting receiver and streamers
    r.start()
    s_writer.start()
    s_preview.start()
    s_analysis.start()

    # finishes the application
    r.join()
    s_writer.join()
    s_preview.join()
    s_analysis.join()

if __name__ == "__main__":
    main()