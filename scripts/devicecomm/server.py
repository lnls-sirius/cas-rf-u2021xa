#!/usr/bin/python3
import logging
import os
import socket
import re

from manager import ResponseType, VisaManager

logger = logging.getLogger()

SET_TRAC_TIME_REG = re.compile(r"setTracTime (\d+\.?\d*)")


class Comm:
    def __init__(self, unix_socket_path, resource, *args, **kwargs):
        self.unix_socket_path = unix_socket_path
        self.connection = None
        self.welcome_socket = None

        self.manager = VisaManager(resource_str=resource)

    def serve(self):
        try:
            if os.path.exists(self.unix_socket_path):
                logger.warning(
                    "Unix socket {} already exist".format(self.unix_socket_path)
                )
                os.unlink(self.unix_socket_path)

            if self.welcome_socket != None:
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

                # Get
                if command.startswith("get"):
                    if command == "getTracTime":
                        response = self.manager.trac_time
                    elif command == "getTracData":
                        response = self.manager.instr_trac_data()
                    elif command == "getInstrInfo":
                        response = self.manager.instr_info()
                    elif command == "getResource":
                        response = self.manager.resource_str
                    elif command == "getResources":
                        response = self.manager.list_resources()
                    elif command == "getTimeAxis":
                        response = str(self.manager.time_axis)

                # Set
                elif command.startswith("setTracTime"):
                    try:
                        match = SET_TRAC_TIME_REG.search(command)
                        if match:
                            response = self.manager.instr_trac_time(
                                float(match.group(1))
                            )
                        else:
                            response = ResponseType.WRONG_FORMAT_INPUT

                    except IndexError:
                        logger.exception("Command setTracTime")
                        response = ResponseType.WRONG_FORMAT_INPUT

                elif command.startswith("setResource"):
                    try:
                        match = re.search(r"setResource (.*)", command)
                        if hasattr(match, "group"):
                            self.manager.resource_str = match.group(1)
                            response = self.manager.resource_str
                        else:
                            response = ResponseType.WRONG_FORMAT_INPUT

                    except IndexError:
                        logger.exception("Command setResource")
                        response = ResponseType.WRONG_FORMAT_INPUT

                # Query
                elif command.startswith("query"):
                    try:
                        match = re.search(r"query (.*)", command)
                        if hasattr(match, "group"):
                            response = self.manager.instr_query(match.group(1))
                        else:
                            response = ResponseType.WRONG_FORMAT_INPUT
                    except IndexError:
                        logger.exception("Command query")
                        response = ResponseType.WRONG_FORMAT_INPUT

                # Write
                elif command.startswith("write"):
                    try:
                        match = re.search(r"write (.*)", command)
                        if hasattr(match, "group"):
                            response = self.manager.instr_write(match.group(1))
                        else:
                            response = ResponseType.WRONG_FORMAT_INPUT
                    except IndexError:
                        logger.exception("Command write")
                        response = ResponseType.WRONG_FORMAT_INPUT

                # Others
                else:
                    if command == "instrConnect":
                        response = self.manager.instr_connect()
                    elif command == "instrDisconnect":
                        response = self.manager.instr_disconnect()
                    elif command == "instrConfig":
                        response = self.manager.instr_config()

                response = ("{}\r\n".format(str(response).strip("\n"))).encode("utf-8")

                connection.sendall(response)
                logger.debug("Command {} Length {}".format(command, response))
        except:
            logger.exception("Connection exception")
        finally:
            logger.warning("Connection closed")
            connection.close()
