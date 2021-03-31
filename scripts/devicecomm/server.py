#!/usr/bin/python3
import queue

from devicecomm.consts import ResponseType
from devicecomm.command_handler import CommandHandler
from devicecomm.log import get_logger
from devicecomm.socket import CommLink

logger = get_logger(__name__)

in_queue: queue.Queue = queue.Queue(maxsize=10)
out_queue: queue.Queue = queue.Queue(maxsize=10)


def clear_queue(q: queue.Queue):
    try:
        while q.get(block=False):
            pass
    except queue.Empty:
        logger.info(f"Queue {q} has been cleared")


class CommandListener:
    def __init__(self, resource: str):
        self.command_handler: CommandHandler = CommandHandler(resource=resource)

    def __str__(self):
        return "CommandListener()"

    def serve(self):
        while True:
            command = in_queue.get(block=True, timeout=None)
            # logger.info(f"{self}: in {in_queue.qsize()} -1")

            raw_response = (
                str(self.command_handler.handle(command))
                .replace("\r", "")
                .replace("\n", "")
            )

            response = f"{command} {raw_response}\r\n"
            try:
                out_queue.put(response, block=False)
                # logger.info(f"{self}: out {out_queue.qsize()} +1")
            except queue.Full:
                logger.exception(
                    f"Output queue {out_queue} is full, we should not reach this point. That means the output comm is not working properly. Output queue will reset."
                )
                clear_queue(out_queue)


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
            in_queue.put(command, block=False)
            # logger.info(f"{self}: in {in_queue.qsize()} +1")
            self.comm.send(f"{ResponseType.OK}\r\n")
        except queue.Full:
            logger.fatal(
                f"{self}: Failed to send command {command}. input queue is full, propably the device is not responding. The queue {in_queue} will be reset."
            )
            clear_queue(in_queue)
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
                    # logger.info(f"{self}: {out_queue.qsize()} -1")
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
