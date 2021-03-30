#!/usr/bin/env python
import argparse
import logging
import threading

from devicecomm.utility import list_nivisa_resources, close_resources
from devicecomm.server import InComm, OutComm, CommandListener
from devicecomm.log import get_logger, set_level_global

logger = get_logger(__name__)


def lauch_threads(resource: str, in_socket_path: str, out_socket_path: str):

    in_comm = InComm(in_socket_path)
    out_comm = OutComm(out_socket_path)
    cmd_dispatcher = CommandListener(resource)

    t_in_comm = threading.Thread(daemon=False, target=in_comm.serve)
    t_out_comm = threading.Thread(daemon=False, target=out_comm.serve)
    t_cmd_dispatcher = threading.Thread(daemon=False, target=cmd_dispatcher.serve)

    t_in_comm.start()
    t_out_comm.start()
    t_cmd_dispatcher.start()

    t_in_comm.join()
    t_out_comm.join()
    t_cmd_dispatcher.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Keysight U2020 X-Series USB Peak and Average Power Sensors\n Unix socket Visa interface",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--resource", dest="resource", help="Visa Resource")
    parser.add_argument(
        "--in-socket-path",
        dest="in_socket_path",
        help="UNIX socket address.",
        default="./in-socket",
    )
    parser.add_argument(
        "--out-socket-path",
        dest="out_socket_path",
        help="UNIX socket address.",
        default="./out-socket",
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

    lauch_threads(
        resource=resource,
        in_socket_path=args.in_socket_path,
        out_socket_path=args.out_socket_path,
    )
