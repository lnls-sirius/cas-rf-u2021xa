#!/usr/bin/env python
import pyvisa as visa
import time
import argparse
import typing

from devicecomm.utility import (
    read_waveform,
    configure_resource,
    get_logger,
    list_nivisa_resources,
    close_resources,
)


logger = get_logger(__name__)


def connect(
    resource_name: str, timeout: int
) -> typing.Tuple[visa.ResourceManager, visa.Resource]:
    visa.log_to_screen()
    rm = visa.ResourceManager()
    resources = rm.list_resources()
    if resource_name not in resources:
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource", "-n")
    parser.add_argument("--timeout", "-t", default=5000, type=int)
    args = parser.parse_args()

    close_resources()
    list_nivisa_resources()

    timeout = None if args.timeout < 0 else args.timeout

    rm, instr = connect(resource_name=args.resource, timeout=timeout)

    while True:
        # Check for isses, clear if needed
        try:
            data = read_waveform(instr)
        except:
            logger.exception("Failed to read")
            logger.info(f"Trying to clear device {rm.last_status}")
            try:
                configure_resource(resource=instr)
            except:
                logger.exception("OMG!! failed to clear")

        time.sleep(2)

    instr.close()
    rm.close()
