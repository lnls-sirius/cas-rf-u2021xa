#!/usr/bin/env python
import argparse
import logging

from devicecomm.utility import list_nivisa_resources, close_resources
from devicecomm.server import Comm
from devicecomm.log import get_logger, set_level_global

logger = get_logger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Keysight U2020 X-Series USB Peak and Average Power Sensors\n Unix socket Visa interface",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--resource", dest="resource", help="Visa Resource")
    parser.add_argument(
        "--unix-socket-path",
        dest="unix_socket_path",
        help="UNIX socket address.",
        default="./unix-socket",
    )
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--list-resources", action="store_true", dest="list_resources")
    args = parser.parse_args()

    if args.debug:
        set_level_global(logging.DEBUG)

    if args.list_resources:

        close_resources()
        list_nivisa_resources()
        exit(0)

    resource = args.resource
    if not resource:
        logger.warning("Device argument is empty, trying to find a suitable resource")
        for res, idn in list_nivisa_resources():
            if "U2021XA" in idn:
                logger.info(f"Using resource {res}, idn {idn}")
                resource = res
                break

    if not resource:
        logger.error("Could not find any available device")
        exit(-1)

    comm = Comm(args.unix_socket_path, resource)
    comm.serve()
