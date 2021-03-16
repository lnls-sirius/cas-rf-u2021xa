#!/usr/bin/env python
import pyvisa as visa
import time
import argparse
import typing
import logging

from devicecomm.utility import (
    close_resources,
    get_resource_idn,
    list_nivisa_resources,
    send_commands_to_resource,
    read_waveform,
    configure_resource,
)

import logging
import logging.handlers

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def connect(
    resource_name: str, timeout: int
) -> typing.Tuple[visa.ResourceManager, visa.Resource]:
    visa.log_to_screen()
    rm = visa.ResourceManager()
    resources = rm.list_resources()
    if not resource_name in resources:
        raise Exception(f"Resource {resource_name} not available in {resources}")

    instr = rm.open_resource(resource_name)
    instr.timeout = 5000
    print(f"Connected to {instr}, timeout {instr.timeout}")
    return rm, instr


def query_error(instr: visa.Resource):
    try:
        print(":SYST:ERR?", instr.query(":SYST:ERR?"))
    except:
        print("Failed to get :SYST:ERR?")
        pass


# print(instr.query(':SYST:ERR?'))
# print(instr.query('STAT:DEV:COND?')) # Device status
# print(instr.query('STAT:DEV?'))
# print("---------------------")
# print("*IDN?", instr.query("*IDN?"))
# print(":TRIG:SOUR?", instr.query(":TRIG:SOUR?"))
# print(":INIT:CONT?", instr.query(":INIT:CONT?"))
# print(":AVER:STAT?", instr.query(":AVER:STAT?"))
# print(instr.query("*ESR?"))
# print("---------------------\n\n")

# print("---------------------")
# print(":CORR:GAIN2?", instr.query(":CORR:GAIN2?"))
# print(":CORR:GAIN2:STAT?", instr.query(":CORR:GAIN2:STAT?"))
# print(":CORR:LOSS2?", instr.query(":CORR:LOSS2?"))
# print(":CORR:LOSS2:STAT?", instr.query(":CORR:LOSS2:STAT?"))
# print(":SENS:DET:FUNC?", instr.query(":SENS:DET:FUNC?"))
# rint("---------------------\n\n")
# exit(0)
# rint("---------------------")
# rint(":TRAC:STAT OFF", instr.write(":TRAC:STAT OFF"))
# print(":AVER:STAT ON", instr.write(":AVER:STAT ON"))
# rint(":INIT", instr.write(":INIT"))
# rint(":FETC?", instr.write(":FETC?"))
# print("---------------------\n\n")

# print('AVER?', instr.query('AVER?'))
# print('READ?', instr.query('READ?'))
# exit(0)
# while True:
#    continue
#    #print('INIT', instr.write('INIT'))
#    #print('FETC?', instr.query('FETC?'))
#
#    time.sleep(1.)


# print(':CORR:GAIN2',instr.write(':CORR:GAIN2 2'))
# print(':CORR:LOSS2',instr.write(':CORR:LOSS2 -2'))

# print(':CORR:GAIN2?',instr.query(':CORR:GAIN2?'))
# print(':CORR:LOSS2?',instr.query(':CORR:LOSS2?'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--resource_name", "-n", default="USB0::0x2A8D::0x7F18::MY57380004::INSTR"
    )
    parser.add_argument("--timeout", "-t", default=5000, type=int)
    args = parser.parse_args()

    timeout = None if args.timeout < 0 else args.timeout

    rm, instr = connect(resource_name=args.resource_name, timeout=timeout)

    while True:
        # Check for isses, clear if needed
        try:
            data = read_waveform(instr)
            print(data)
        except:
            logger.exception("Failed to read")
            logger.info(f"Trying to clear device {rm.last_status}")
            try:
                configure_resource(resource=instr)
            except:
                logger.exception(f"OMG!! failed to clear")

        time.sleep(2)

    instr.close()
    rm.close()
