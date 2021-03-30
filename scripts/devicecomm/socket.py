import socket
import os

from devicecomm.log import get_logger

logger = get_logger(__name__)


class CommLink:
    def __init__(self, unix_socket_path: str):
        self.unix_socket_path: str = unix_socket_path
        self.welcome_socket: socket.socket = None
        self.connection: socket.socket = None

    def client_connected(self) -> bool:
        return self.connection is not None

    def __str__(self):
        return f"CommLink({self.unix_socket_path})"

    def close(self):
        if self.welcome_socket:
            self.welcome_socket.close()
        self.reset_unix_socket_path()
        logger.info(f"{self}: Comm server shutdown")

    def reset_unix_socket_path(self):
        if os.path.exists(self.unix_socket_path):
            logger.warning(f"{self}: Unix socket {self.unix_socket_path} already exist")
            os.unlink(self.unix_socket_path)

    def create_welcome_socket(self):
        self.reset_unix_socket_path()
        self.welcome_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.welcome_socket.bind(self.unix_socket_path)
        self.welcome_socket.listen(0)
        logger.info(f"{self}: Unix socket created at {self.unix_socket_path}")

    def listen_to_client(self):
        if not self.welcome_socket:
            self.create_welcome_socket()

        if self.connection:
            return

        logger.info(f"{self}: Unix welcome socket listening")
        self.connection, client_address = self.welcome_socket.accept()
        self.connection.settimeout(30)
        logger.info(f"{self}: Client {client_address} connected")

    def recv(self) -> str:
        return (
            self.connection.recv(1024)
            .decode("utf-8")
            .replace("\r", "")
            .replace("\n", "")
        )

    def send(self, message: str):
        return self.connection.sendall(message.encode("utf-8"))

    def drop_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
