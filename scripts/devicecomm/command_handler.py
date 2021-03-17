import logging
import re

from devicecomm.consts import ResponseType
from devicecomm.manager import VisaManager

logger = logging.getLogger(__name__)
SET_TRAC_TIME_REG = re.compile(r"setTracTime (\d+\.?\d*)")


class CommandHandler:
    def __init__(self, resource: str):
        self.manager = VisaManager(resource_str=resource)

    def handle_get(self, command: str):
        response = ""
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
                self.manager.resource_str = match.group(1)
                response = self.manager.resource_str
            else:
                response = ResponseType.WRONG_FORMAT_INPUT

        return response

    def handle_query(self, command: str):
        response = ""
        match = re.search(r"query (.*)", command)
        if hasattr(match, "group"):
            response = self.manager.instr_query(match.group(1))
        else:
            response = ResponseType.WRONG_FORMAT_INPUT
        return response

    def handle_write(self, command: str):
        response = ""
        match = re.search(r"write (.*)", command)
        if hasattr(match, "group"):
            response = self.manager.instr_write(match.group(1))
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
        try:
            if command.startswith("get"):
                response = self.handle_get(command)

            elif command.startswith("set"):
                response = self.handle_set(command)

            elif command.startswith("query"):
                response = self.handle_query(command)

            elif command.startswith("write"):
                response = self.hande_write(command)

            else:
                response = self.handle_others(command)

        except IndexError:
            logger.exception(f"Command {command}")
            response = ResponseType.WRONG_FORMAT_INPUT

        return response