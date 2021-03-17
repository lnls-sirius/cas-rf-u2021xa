#!/usr/bin/python3
import logging
import socket
import os

from devicecomm.consts import ResponseType
from devicecom.command_handler import CommandHandler

logger = logging.getLogger(__name__)


class Comm:
    def __init__(self, unix_socket_path, resource, *args, **kwargs):
        self.unix_socket_path = unix_socket_path
        self.connection = None
        self.welcome_socket = None

        self.command_handler: CommandHandler = CommandHandler(resource=resource)

    def serve(self):
        try:
            if os.path.exists(self.unix_socket_path):
                logger.warning(
                    "Unix socket {} already exist".format(self.unix_socket_path)
                )
                os.unlink(self.unix_socket_path)

            if self.welcome_socket is None:
                logger.warning("Welcome socket already istantiated")

            self.welcome_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.welcome_socket.bind(self.unix_socket_path)

            logger.info("Unix socket created at {}".format(self.unix_socket_path))
            self.welcome_socket.listen(1)

            while True:
                logger.info("Unix welcome socket listening")
                connection, client_address = self.welcome_socket.accept()
                logger.info("Client {} connected".format(client_address))

                connection.settimeout(30)

                self.handle_connection(connection)
        except:
            logger.exception("Comm exception")
        finally:
            self.welcome_socket.close()
            os.remove(self.unix_socket_path)
            logger.info("Comm server shutdown")
            self.welcome_socket = None

    def handle_connection(self, connection):
        try:
            while True:
                command = connection.recv(1024).decode("utf-8")
                response = ResponseType.NO_RESPONSE

                if not command:
                    break

                response = self.command_handler(command)

                response = ("{}\r\n".format(str(response).strip("\n"))).encode("utf-8")

                connection.sendall(response)
                logger.debug("Command {} Length {}".format(command, response))
        except:
            logger.exception("Connection exception")
        finally:
            logger.warning("Connection closed")
            connection.close()
