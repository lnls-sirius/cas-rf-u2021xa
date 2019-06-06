import logging

logger = logging.getLogger()

class Comm():
    def __init__(self, unix_socket_path='', *args, **kwargs):
        self.unix_socket_path = unix_socket_path

    def serve(self):
        pass

    def handle(self, command):
        pass

