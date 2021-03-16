#!/usr/bin/env python
import argparse
import logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Keysight U2020 X-Series USB Peak and Average Power Sensors\n Unix socket Visa interface",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--resource", required=True, dest="resource", help="Visa Resource"
    )
    parser.add_argument(
        "--unix-socket-path",
        dest="unix_socket_path",
        help="UNIX socket address.",
        default="./unix-socket",
    )
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)-15s [%(levelname)s] %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )
    logger = logging.getLogger()

    from devicecomm.server import Comm

    comm = Comm(args.unix_socket_path, args.resource)
    comm.serve()
