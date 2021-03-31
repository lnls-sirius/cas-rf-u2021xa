import typing
import pyvisa as visa
from pyvisa.resources.messagebased import MessageBasedResource

from devicecomm.log import get_logger
from devicecomm.consts import ResponseType
from devicecomm.config import ConfigManager
from devicecomm.utility import (
    close_resources,
    configure_resource,
    list_nivisa_resources,
    read_waveform,
)

logger = get_logger(__name__)


class VisaManager:
    def __init__(self, resource_str: str):

        self.resource_str: str = resource_str

        close_resources()
        list_nivisa_resources()

        self.config = ConfigManager()
        self.rm = visa.ResourceManager()

        self.instr: typing.Optional[MessageBasedResource] = None
        self.instr_configured = False
        self.should_update_time_axis = True
        self.time_axis: typing.List[float] = []

        self.load_config()

    def load_config(self):
        self.config.load_config()

    def dump_config(self):
        self.config.dump_config()

    def list_resources(self):
        resouces = []
        for res in self.rm.list_resources():
            if "USB" in res:
                resouces.append(res)
        return str(resouces)

    def instr_connect(self) -> str:
        if self.instr:
            return ResponseType.OK

        try:
            logger.info(f"Connecting to resource {self.resource_str}")
            unknown_resource = self.rm.open_resource(self.resource_str)
            if not isinstance(unknown_resource, MessageBasedResource):
                raise Exception(
                    f"Failed to connect, resource {self.resource_str} must be a message based resource"
                )
            self.instr = unknown_resource
            self.instr.timeout = None  # type: ignore
            logger.debug("Instrument {self.resource_str} connected")
        except:
            logger.exception(f"Failed to connect at {self.resource_str}")
            return ResponseType.EXCEPTION

        return ResponseType.OK

    def instr_disconnect(self):
        logger.info(f"Disconnect status instr {self.instr.last_status}")
        return ResponseType.OK

        try:
            if self.instr:
                self.instr.clear()
                self.instr.close()
                self.instr = None

            return ResponseType.INSTR_DISCONNECTED
        except:
            self.instr = None
            self.instr_configured = False

            logger.exception("instr_disconnect error")
            return ResponseType.EXCEPTION

    def instr_info(self):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        return self.instr

    def instr_config(self) -> str:
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        try:
            configure_resource(
                resource=self.instr,
                trac_time_new=self.config.trac_time_new,
                freq=self.config.freq,
                gain=self.config.gain,
                unit=self.config.unit,
            )
            try:
                logger.debug(self.instr.query(":SYST:ERR?"))
            except:
                pass

            self.config.update_trac_time()
            logger.debug(
                "SENS:TRAC:TIME set to {} seconds".format(self.config.trac_time)
            )

            self.should_update_time_axis = True
            self.instr_configured = True

            return ResponseType.OK
        except:
            logger.exception("Instr Config")
            self.instr_configured = False
            return ResponseType.EXCEPTION

    def instr_trac_time(self, trac_time) -> str:
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        if trac_time > 2:
            logger.warning('Trac time "{}" cannot be larger then "2"'.format(trac_time))
            trac_time = 2
        elif trac_time < 0:
            logger.warning('Trac time "{}" cannot be less then "0"'.format(trac_time))
            trac_time = 0.0001

        try:
            self.config.trac_time_new = trac_time
            self.instr.write(":SENS:TRAC:TIME {}".format(self.config.trac_time_new))
            self.should_update_time_axis = True
            self.config.trac_time = self.config.trac_time_new
            logger.info(
                "SENS:TRAC:TIME set to {} seconds".format(self.config.trac_time)
            )

        except:
            logger.exception("Exception: Update TRAC:TIME.")
            self.instr_configured = False
            return ResponseType.EXCEPTION

        self.dump_config()

        return ResponseType.OK

    def instr_query(self, param):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        if not self.instr_configured:
            return ResponseType.INSTR_NOT_CONFIGURED

        try:
            return str(self.instr.query(param))
        except:
            logger.exception("Exception: Instr query {}.".format(param))
            return ResponseType.EXCEPTION

    def instr_write(self, param):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        if not self.instr_configured:
            return ResponseType.INSTR_NOT_CONFIGURED

        try:
            logger.info("Instrument write '{}'".format(param))

            if param.startswith(":CORR:GAIN2"):
                self.config.gain = float(param.split(" ")[1])
                self.dump_config()

            elif param.startswith(":TRAC:UNIT"):
                self.config.unit = param.split(" ")[1]
                self.dump_config()

            elif param.startswith(":SENS:FREQ"):
                self.config.freq = param.split(" ")[1]
                self.dump_config()

            res = self.instr.write(param)
            logger.info("Intr write status {}".format(res))

            return param + " " + str(self.instr.write(param))
        except:
            logger.exception("Instr write {}.".format(param))
            return ResponseType.EXCEPTION

    def update_time_axis(self, readings):
        time_step = self.config.trac_time / readings
        self.time_axis = [time_step * i for i in range(readings)]
        self.should_update_time_axis = False
        logger.info(
            f"Time axis updated {self.config.trac_time}, trac_time=[{self.time_axis[0]},{self.time_axis[-1]}]"
        )

    def instr_trac_data(self):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        if not self.instr_configured:
            return ResponseType.INSTR_NOT_CONFIGURED

        try:
            values = read_waveform(self.instr)

            if self.should_update_time_axis or len(self.time_axis) != len(values):
                readings = len(values)
                self.update_time_axis(readings)

            return str(values)
        except:
            logger.exception("Instr trac data.")
            return ResponseType.EXCEPTION
