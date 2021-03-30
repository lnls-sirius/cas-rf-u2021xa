#!/usr/bin/python3
import queue

from devicecomm.consts import ResponseType
from devicecomm.command_handler import CommandHandler
from devicecomm.log import get_logger
from devicecomm.socket import CommLink

logger = get_logger(__name__)

in_queue = queue.Queue(maxsize=50)
out_queue = queue.Queue()


class CommandListener:
    def __init__(self, resource: str):
        self.resourece: str = resource
        self.command_handler: CommandHandler = CommandHandler(resource=resource)

    def __str__(self):
        return f"CommandListener({self.resource})"

    def serve(self):
        while True:
            command = in_queue.get(block=True, timeout=None)

            raw_response = (
                str(self.command_handler.handle(command))
                .replace("\r", "")
                .replace("\n", "")
            )

            response = f"{command} {raw_response}\r\n"
            try:
                out_queue.put(response)
            except queue.Full:
                logger.exception(
                    "Queue full, we should not reach this point. That means the output comm is not working properly"
                )


class InComm:
    def __init__(self, unix_socket_path: str):
        self.comm: CommLink = CommLink(unix_socket_path)

    def __str__(self):
        return f"InComm({self.comm})"

    def serve(self):
        self.comm.create_welcome_socket()
        while True:
            try:
                self.comm.listen_to_client()

                command = self.comm.recv()

                self.handle_command(command)
            except:
                logger.exception(f"{self}: Comm exception")
                self.comm.drop_connection()

    def handle_command(self, command: str):
        if not command:
            raise Exception("Empty command, client disconnected")

        logger.debug(f"{self}: Command {command}")
        try:
            in_queue.put(command)
            self.comm.send(f"{ResponseType.OK}\r\n")
        except queue.Full:
            logger.fatal(
                f"{self}: Failed to send command {command}. input queue is full, propably the device is not responding"
            )
            self.comm.send(f"{ResponseType.QUEUE_FULL}\r\n")


class OutComm:
    def __init__(self, unix_socket_path: str):
        self.comm: CommLink = CommLink(unix_socket_path)
        self.resend: bool = False

    def __str__(self):
        return f"OutComm({self.comm})"

    def serve(self):
        self.comm.create_welcome_socket()
        response = ""
        while True:
            try:
                self.comm.listen_to_client()

                if not self.resend:
                    response = out_queue.get(block=True, timeout=None)
                else:
                    self.resend = False
                    logger.warning(f"{self}: Resending response")

                self.comm.send(response)
                logger.debug(f"{self}: response={response}")

            except BrokenPipeError:
                logger.warning(f"{self}: Connection closed, resend flag set")
                self.resend = True
                self.comm.drop_connection()
            except:
                logger.exception(f"{self}: Connection exception")
                self.comm.drop_connection()
