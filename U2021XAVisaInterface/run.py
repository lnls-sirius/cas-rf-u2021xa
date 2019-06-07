#!/usr/bin/python3
import argparse
import logging

from server import Comm

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s [%(levelname)s] %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger()

    parser = argparse.ArgumentParser(description='Keysight U2020 X-Series USB Peak and Average Power Sensors\n Unix socket Visa interface',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--resource', required=True, dest='resource', help='Visa Resource')
    parser.add_argument('--unix-socket-path', dest='unix_socket_path', help='UNIX socket address.', default='./unix-socket')
    args = parser.parse_args()

    comm = Comm(args.unix_socket_path, args.resource)
    comm.serve()

