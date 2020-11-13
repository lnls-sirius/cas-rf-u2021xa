#!/usr/bin/python3
import logging
import struct
import visa
import json

logger = logging.getLogger()


class ResponseType:
    NO_RESPONSE = "NO_RESPONSE"
    WRONG_FORMAT_INPUT = "WRONG_FORMAT_INPUT"
    EXCEPTION = "EXCEPTION"
    OK = "OK"
    INSTR_DISCONNECTED = "INSTR_DISCONNECTED"
    INSTR_NOT_CONFIGURED = "INST_NOT_CONFIGURED"
    USB_ERROR = "USB_ERROR"


class VisaManager:
    def __init__(self, resource):
        self.rm = visa.ResourceManager("@py")
        self.resource_str = resource
        self.instr = None
        self.instr_timeout = 5000
        self.instr_configured = False
        self.update_time_axis = True
        self.time_axis = []
        self.load_config()

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.gain = config["gain"]
                self.freq = config["freq"]
                self.trac_time = config["trac_time"]
                self.trac_time_new = self.trac_time
                logger.info("Loaded '{}' from config.json".format(config))
        except:
            logger.exception(
                "Failed to load from config.json, falling back to defaults"
            )
            self.freq = 500000000
            self.gain = 74.3
            self.trac_time = 0.41
            self.trac_time_new = self.trac_time

    def dump_config(self):
        try:
            config = {"gain": self.gain, "freq": self.freq, "trac_time": self.trac_time}

            with open("config.json", "w+") as f:
                json.dump(config, f)
            logger.info("Update config.json")
        except:
            logger.exception("Failed to dump config")

    def list_resources(self):
        return str(list(self.rm.list_resources()))

    def instr_connect(self):
        try:
            logger.info(self.resource_str)
            self.instr = self.rm.open_resource(self.resource_str)
            self.instr.timeout = self.instr_timeout
            logger.debug("Isntr {} connected".format(self.resource_str))
            return str(self.instr)

        except Exception as e:
            logger.exception("instr_connect error")
            return ResponseType.EXCEPTION + " {}".format(e)

    def instr_disconnect(self):
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

    def instr_config(self):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        try:
            self.instr.write("*RST")  # Reset configuration
            self.instr.write(":TRIG:SOUR EXT")
            self.instr.write(":INIT:CONT OFF")
            self.instr.write(":TRIG:DEL:AUTO OFF")
            self.instr.write(":TRAC:STAT ON")
            self.instr.write(":AVER:STAT OFF")
            self.instr.write(":SENS:TRAC:TIME {}".format(self.trac_time_new))
            self.instr.write(":SENS:FREQ {}".format(self.freq))
            self.instr.write(":CORR:GAIN2:STAT ON")
            self.instr.write(":CORR:LOSS2:STAT OFF")
            self.instr.write(":CORR:GAIN2 {}".format(self.gain))
            self.instr.write(":TRAC:UNIT W")
            self.instr.write("*CLS")  # Clear errors
            try:
                logger.debug(self.instr.query(":SYST:ERR?"))
            except:
                pass
            self.trac_time = self.trac_time_new
            logger.debug("SENS:TRAC:TIME set to {} seconds".format(self.trac_time))

            self.update_time_axis = True
            self.instr_configured = True

            return ResponseType.OK
        except:
            logger.exception("Instr Config")
            self.instr_configured = False
            return ResponseType.EXCEPTION

    def instr_trac_time(self, trac_time):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        if trac_time > 2:
            logger.warning('Trac time "{}" cannot be larger then "2"'.format(trac_time))
            trac_time = 2
        elif trac_time < 0:
            logger.warning('Trac time "{}" cannot be less then "0"'.format(trac_time))
            trac_time = 0.0001

        try:
            self.trac_time_new = trac_time
            self.instr.write(":SENS:TRAC:TIME {}".format(self.trac_time_new))
            self.update_time_axis = True
            self.trac_time = self.trac_time_new
            logger.info("SENS:TRAC:TIME set to {} seconds".format(self.trac_time))

        except:
            logger.exception("Exception: Update TRAC:TIME.")
            self.instr_configured = False
            return ResponseType.EXCEPTION

        self.dump_config()

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
                self.gain = float(param.split(" ")[1])
                self.dump_config()
            return param + " " + str(self.instr.write(param))
        except:
            logger.exception("Instr write {}.".format(param))
            return ResponseType.EXCEPTION

    def instr_trac_data(self):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        if not self.instr_configured:
            return ResponseType.INSTR_NOT_CONFIGURED

        try:
            self.instr.write(":INIT")  # Initialize measures
            self.instr.write(":TRAC:DATA? LRES")  # Get 240 data points
            data = self.instr.read_raw()
            if chr(data[0]) == "#":
                x = int(chr(data[1]))
                y = int(data[2 : 2 + x])

                d_bytes = data[2 + x : -1]

                res = [
                    struct.unpack(">f", d_bytes[4 * i : 4 * i + 4])[0]
                    for i in range(int(y / 4))
                ]
                if self.update_time_axis or len(self.time_axis) != len(res):
                    time_step = self.trac_time / len(res)
                    self.time_axis = [time_step * i for i in range(len(res))]
                    self.update_time_axis = False
                    logger.info(
                        "Time axis updated? trac_time={} {} {}".format(
                            self.trac_time, self.time_axis[0], self.time_axis[-1]
                        )
                    )
            else:
                res = ResponseType.EXCEPTION
                logger.error("Wrong format response.")
            return str(res)
        except:
            logger.exception("Instr trac data.")
            return ResponseType.EXCEPTION
