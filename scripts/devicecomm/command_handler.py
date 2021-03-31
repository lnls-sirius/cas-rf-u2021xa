import re

from devicecomm.consts import ResponseType
from devicecomm.manager import VisaManager
from devicecomm.log import get_logger

logger = get_logger(__name__)

SET_TRAC_TIME_REG = re.compile(r"setTracTime (\d+\.?\d*)")


class CommandHandler:
    def __init__(self, resource: str):
        self.manager = VisaManager(resource_str=resource)

    def handle_get(self, command: str):
        response = ""
        if command == "getTracTime":
            response = self.manager.config.trac_time
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

        return response

    def handle_set(self, command: str):
        response = ""
        if command.startswith("setTracTime"):
            match = SET_TRAC_TIME_REG.search(command)
            if match:
                response = self.manager.instr_trac_time(float(match.group(1)))
            else:
                response = ResponseType.WRONG_FORMAT_INPUT

        elif command.startswith("setResource"):
            match = re.search(r"setResource (.*)", command)
            if hasattr(match, "group"):
                self.manager.resource_str = match.group(1)  # type: ignore
                response = self.manager.resource_str
            else:
                response = ResponseType.WRONG_FORMAT_INPUT

        return response

    def handle_query(self, command: str):
        response = ""
        match = re.search(r"query (.*)", command)
        if hasattr(match, "group"):
            response = self.manager.instr_query(match.group(1))  # type: ignore
        else:
            response = ResponseType.WRONG_FORMAT_INPUT
        return response

    def handle_write(self, command: str):
        response = ""
        match = re.search(r"write (.*)", command)
        if hasattr(match, "group"):
            response = self.manager.instr_write(match.group(1))  # type: ignore
        else:
            response = ResponseType.WRONG_FORMAT_INPUT
        return response

    def handle_others(self, command: str):
        response = ""
        if command == "instrConnect":
            response = self.manager.instr_connect()
        elif command == "instrDisconnect":
            response = self.manager.instr_disconnect()
        elif command == "instrConfig":
            response = self.manager.instr_config()
        return response

    def handle(self, command: str):
        response = ""

        response = self.manager.instr_connect()
        if response != ResponseType.OK:
            return response

        response = (
            ResponseType.OK
            if self.manager.instr_configured
            else self.manager.instr_config()
        )
        if response != ResponseType.OK:
            return response

        try:

            if command.startswith("get"):
                response = self.handle_get(command)

            elif command.startswith("set"):
                logger.info(f"command '{command}'")
                response = self.handle_set(command)

            elif command.startswith("query"):
                response = self.handle_query(command)

            elif command.startswith("write"):
                logger.info(f"command '{command}'")
                response = self.handle_write(command)

            else:
                response = self.handle_others(command)

        except IndexError:
            logger.exception(f"command '{command}'")
            response = ResponseType.WRONG_FORMAT_INPUT

        return response
