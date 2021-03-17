##!/usr/bin/env python3
import pyvisa
import typing
import struct
from devicecomm.log import get_logger

logger = get_logger(__name__)


def get_resource_idn(rm: pyvisa.ResourceManager, resource):
    idn = None
    try:
        logger.info(f"Trying to open resource {resource}")
        with rm.open_resource(resource) as unknown_resource:
            idn = unknown_resource.query("*IDN?")
            logger.info(f"*IDN? {idn}")
    except:
        logger.exception(f"Failed to open resource {resource}")
    return idn


def close_resources():
    logger.debug("Force closing pyvisa-py USB resources")
    rm = pyvisa.ResourceManager("@py")
    resources = rm.list_resources()
    for resource in resources:
        if "USB" not in resource:
            logger.debug(f"Skip resource {resource}")
            continue
        get_resource_idn(rm, resource)
    rm.close()


def list_nivisa_resources():
    resources = []
    logger.debug("Listing NI-VISA available resources")
    rm = pyvisa.ResourceManager()
    for resource in rm.list_resources():
        if "USB" not in resource:
            logger.debug(f"Skip resource {resource}")
            continue
        logger.info(f"Available USB device {resource}")
        idn = get_resource_idn(rm, resource)
        resources.append((resource, idn))
    return resources


def check_resource_erros(resource: pyvisa.Resource):
    res = resource.query("SYST:ERR?")
    logger.debug(f"Resource {resource} SYST:ERR? {res}")
    return "No error" in res


def send_command_list_resource(resource: pyvisa.Resource, command):
    """ Receives a list with [action, cmd], handle accordingly """
    action, cmd = command
    if action == "write":
        logger.warn(f"Failed, {action} not supported")
        pass
    elif action == "read":
        logger.warn(f"Failed, {action} not supported")
        pass
    elif action == "query":
        logger.warn(f"Failed, {action} not supported")
        pass
    else:
        logger.warning(f"Unsupported command type {command}")


def send_commands_to_resource(resource: pyvisa.Resource, commands: typing.List):
    for command in commands:
        if type(command) == str:
            res = resource.write(command)
            logger.debug(f"write {command}, response {res}")
        elif type(command) == list:
            send_command_list_resource(resource, command)
        else:
            logger.warning(f"Unsupported command type {command}")


def configure_resource(
    resource: pyvisa.Resource,
    trac_time_new=0.41,
    freq="500000000Hz",
    gain=74.3,
    unit="DBM",
):
    commands = [
        "*CLS",  # Clear errors
        "*RST",  # Reset configuration
        ":TRIG:SOUR EXT",
        ":INIT:CONT OFF",
        ":TRIG:DEL:AUTO OFF",
        ":TRAC:STAT ON",
        ":AVER:STAT OFF",
        f":SENS:TRAC:TIME {trac_time_new}",
        f":SENS:FREQ {freq}",
        ":CORR:GAIN2:STAT ON",
        ":CORR:LOSS2:STAT OFF",
        f":CORR:GAIN2 {gain}",
        f":TRAC:UNIT {unit}",
        "*CLS",  # Clear errors
    ]
    send_commands_to_resource(resource, commands)


def read_waveform(resource: pyvisa.Resource) -> typing.List:
    res = None
    resource.write(":INIT")  # Initialize measures
    resource.write(":TRAC:DATA? LRES")  # Get 240 data points
    data = resource.read_raw()

    if data[0] != ord("#"):
        raise Exception("Wrong format response.")

    x = int(chr(data[1]))
    y = int(data[2 : 2 + x])

    d_bytes = data[2 + x : -1]

    res = [
        struct.unpack(">f", d_bytes[4 * i : 4 * i + 4])[0] for i in range(int(y / 4))
    ]
    return res


if __name__ == "__main__":
    close_resources()
    list_nivisa_resources()
