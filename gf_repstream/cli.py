import argparse
import logging
import os
import sys
import pkgutil
from functools import partial
from threading import Thread
from time import time, sleep

from gf_repstream import __version__
from gf_repstream.receiver import Receiver

Log_Format = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(format=Log_Format, level=logging.ERROR, stream = sys.stdout)
logger = logging.getLogger(__name__)


def main():
    """The gf stream send command line interface.
    This is a tool to receive the incoming gigafrost stream and replicate it
    to external components.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))

    # Discover external components 
    components_path = os.path.join(base_path, "components")
    available_apps = []
    for module_info in pkgutil.iter_modules([components_path]):
        available_apps.append(module_info.name)

    # Prepare argument parser
    parser = argparse.ArgumentParser(
        prog="gf_repstream", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    parser.add_argument(
        "--address",
        metavar="PROTOCOL://HOST:PORT",
        type=str,
        default="tcp://xbl-daq-23:9990",
        help="an address string for zmq socket",
    )

    parser.add_argument(
        "--connection-mode",
        type=str,
        choices=["connect", "bind"],
        default="connect",
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
        default=1,
        help="a number of last received zmq messages to keep in memory",
    )

    args = parser.parse_args()

    # Receiver gets messages via zmq stream
    receiver = Receiver(on_receive=None, buffer_size=args.buffer_size)

    # Start receiver in a separate thread
    # start_receiver = partial(receiver.start, args.io_threads, args.connection_mode, args.address)
    # t = Thread(target=start_receiver, daemon=True)
    # t.start()

    # Main application
    receiver.start(args.io_threads, args.connection_mode, args.address)
    # while True:
    #     try:
    #         sleep(1)
    #         logger.info('1')
    #     except KeyboardInterrupt:
    #         logger.info('^C received, shutting down server')

    t.join()

if __name__ == "__main__":
    main()