#!/usr/bin/python3
import logging
import os
import struct
import visa

logger = logging.getLogger()

class ResponseType():
    NO_RESPONSE = 'NO_RESPONSE'
    WRONG_FORMAT_INPUT = 'WRONG_FORMAT_INPUT'
    EXCEPTION = 'EXCEPTION'
    OK = 'OK'
    INSTR_DISCONNECTED = 'INSTR_DISCONNECTED'
    INSTR_NOT_CONFIGURED = 'INST_NOT_CONFIGURED'
    USB_ERROR = 'USB_ERROR'

class VisaManager():

    def __init__(self, resource, trac_time):
        self.rm = visa.ResourceManager('@py')
        self.resource_str = resource
        self.instr = None
        self.instr_timeout = 5000
        self.instr_configured = False
        self.trac_time = trac_time
        self.trac_time_new = trac_time
        self.update_time_axis = True
        self.time_axis = []

    def list_resources(self):
        return str(list(self.rm.list_resources()))

    def instr_connect(self):
        try:
            logger.info(self.resource_str)
            self.instr = self.rm.open_resource(self.resource_str)
            self.instr.timeout = self.instr_timeout
            logger.debug('Isntr {} connected'.format(self.resource_str))
            return str(self.instr)

        except Exception as e:
            logger.exception('instr_connect error')
            return ResponseType.EXCEPTION + ' {}'.format(e)


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

            logger.exception('instr_disconnect error')
            return ResponseType.EXCEPTION

    def instr_info(self):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        return self.instr

    def instr_config(self):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        try:
            self.instr.write('*RST') # Reset configuration
            self.instr.write(':TRIG:SOUR EXT')
            self.instr.write(':INIT:CONT OFF')
            self.instr.write(':TRIG:DEL:AUTO OFF')
            self.instr.write(':TRAC:STAT ON')
            self.instr.write(':AVER:STAT OFF')
            self.instr.write(':SENS:TRAC:TIME {}'.format(self.trac_time_new))
            self.instr.write(':SENS:FREQ 500000000'.format(self.trac_time_new))
            self.instr.write(':CORR:GAIN2:STAT ON')
            self.instr.write(':CORR:LOSS2:STAT OFF')
            self.instr.write(':CORR:GAIN2 73.3')
            self.instr.write('*CLS') # Clear errors
            try:
                logger.debug(self.instr.query(':SYST:ERR?'))
            except:
                pass
            self.trac_time = self.trac_time_new
            logger.debug('SENS:TRAC:TIME set to {} seconds'.format(self.trac_time_new))

            self.update_time_axis = True
            self.instr_configured = True

            return ResponseType.OK
        except:
            logger.exception('Instr Config')
            self.instr_configured = False
            return ResponseType.EXCEPTION

    def instr_query(self, param):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        if not self.instr_configured:
            return ResponseType.INSTR_NOT_CONFIGURED

        try:
            return str(self.instr.query(param))
        except:
            logger.exception('Instr query')
            return ResponseType.EXCEPTION

    def instr_write(self, param):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        if not self.instr_configured:
            return ResponseType.INSTR_NOT_CONFIGURED

        try:
            return param + ' ' + str(self.instr.write(param))
        except:
            logger.exception('Instr write')
            return ResponseType.EXCEPTION


    def instr_trac_data(self):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        if not self.instr_configured:
            return ResponseType.INSTR_NOT_CONFIGURED

        try:
            self.instr.write(':INIT') # Initialize measures
            self.instr.write(':TRAC:DATA? MRES') # Get 1000 data points
            data = self.instr.read_raw()
            char_data = []
            if chr(data[0]) == '#':
                x = int(chr(data[1]))
                y = int(data[2:2+x])

                d_bytes = data[2+x:-1]

                res = [struct.unpack('>f', d_bytes[4*i:4*i+4])[0] for i in range(int(y/4))]
                if self.update_time_axis or len(self.time_axis) != len(res):
                    self.time_axis = [self.trac_time * i for i in range(len(res))]
                    self.update_time_axis = False
                    logger.info('Time axis updated? {} {}'.format(self.time_axis[0], self.time_axis[-1]))
            else:
                res = ResponseType.EXCEPTION
                logger.error('Wrong format response')
            return str(res)
        except:
            logger.exception('Instr trac data')
            return ResponseType.EXCEPTION

    def isntr_aver(self):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        if not self.instr_configured:
            return ResponseType.INSTR_NOT_CONFIGURED

        try:
            self.instr.write(':INIT')
            res = self.instr.query(':FETC?')
            logger.debug('instr_aver {}'.format(res))
            return res
        except:
            logger.exception('Power average error')
