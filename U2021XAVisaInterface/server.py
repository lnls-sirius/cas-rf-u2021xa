import logging
import os
import socket
import visa
import struct
import re
import usb

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
        self.time_axis = []

    def list_resources(self):
        return str(list(self.rm.list_resources()))

    def instr_connect(self):
        try:
            logger.info(self.resource_str)
            self.instr = self.rm.open_resource(self.resource_str)
            self.instr.timeout = self.instr_timeout

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
            self.instr.write('*RST')
            self.instr.write('TRIG:SOUR EXT')
            self.instr.write('INIT:CONT OFF')
            self.instr.write('TRAC:STAT ON')
            self.instr.write('AVER:STAT OFF')
            self.instr.write('SENS:TRAC:TIME {}'.format(self.trac_time_new))
            self.trac_time = self.trac_time_new
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
            return str(self.instr.write(param))
        except:
            logger.exception('Instr write')
            return ResponseType.EXCEPTION


    def instr_trac_data(self):
        if not self.instr:
            return ResponseType.INSTR_DISCONNECTED

        if not self.instr_configured:
            return ResponseType.INSTR_NOT_CONFIGURED

        try:
            self.instr.write('INIT')
            self.instr.write('TRAC:DATA? MRES')
            data = self.instr.read_raw()
            char_data = []
            if chr(data[0]) == '#':
                x = int(chr(data[1]))
                y = int(data[2:2+x])

                d_bytes = data[2+x:-1]

                res = [struct.unpack('>f', d_bytes[4*i:4*i+4])[0] for i in range(int(y/4))]
                if len(res) != len(self.time_axis):
                    self.time_axis = [self.trac_time * i for i in range(len(res))]
            else:
                res = ResponseType.EXCEPTION
                logger.error('Wrong format response')
            return str(res)
        except:
            logger.exception('Instr trac data')
            return ResponseType.EXCEPTION


class Comm():
    def __init__(self, unix_socket_path, resource, *args, **kwargs):
        self.unix_socket_path = unix_socket_path
        self.connection = None
        self.welcome_socket = None

        self.manager = VisaManager(resource=resource, trac_time=0.41)

    def serve(self):
        try:
            if os.path.exists(self.unix_socket_path):
                logger.warning('Unix socket {} already exist'.format(self.unix_socket_path))
                os.unlink(self.unix_socket_path)

            if self.welcome_socket != None:
                logger.warning('Welcome socket already istantiated')

            self.welcome_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.welcome_socket.bind(self.unix_socket_path)

            logger.info('Unix socket created at {}'.format(self.unix_socket_path))
            self.welcome_socket.listen(1)

            while True:
                logger.info('Unix welcome socket listening')
                connection, client_address = self.welcome_socket.accept()
                logger.info('Client {} connected'.format(client_address))

                connection.settimeout(30)

                self.handle_connection(connection)
        except:
            logger.exception('Comm exception')
        finally:
            self.welcome_socket.close()
            os.remove(self.unix_socket_path)
            logger.info('Comm server shutdown')
            self.welcome_socket = None

    def handle_connection(self, connection):
        try:
            while True:
                command = connection.recv(1024).decode('utf-8')
                response = ResponseType.NO_RESPONSE

                if not command:
                    break

                # Get
                if command.startswith('get'):
                    if command == 'getTracTime':
                        response = self.manager.trac_time
                    elif command == 'getTracData':
                        response = self.manager.instr_trac_data()
                    elif command == 'getInstrInfo':
                        response = self.manager.instr_info()
                    elif command == 'getResource':
                        response =  self.manager.resource_str
                    elif command == 'getResources':
                        response =  self.manager.list_resources()
                    elif command == 'getTimeAxis':
                        response =  str(self.manager.time_axis)

                # Set
                elif command.startswith('setTracTime'):
                    try:
                        match = re.search(r'setTracTime (\d+?\.?\d*)', command)
                        if hasattr(match, 'group'):
                            self.manager.trac_time_new = float(match.group(1))
                            response = self.manager.trac_time_new
                            response = self.manager.instr_config()
                        else:
                            response = ResponseType.WRONG_FORMAT_INPUT

                    except IndexError:
                        logger.exception('Command setTracTime')
                        response = ResponseType.WRONG_FORMAT_INPUT

                elif command.startswith('setResource'):
                    try:
                        match = re.search(r'setResource (.*)', command)
                        if hasattr(match, 'group'):
                            self.manager.resource_str = match.group(1)
                            response = self.manager.resource_str
                        else:
                            response = ResponseType.WRONG_FORMAT_INPUT

                    except IndexError:
                        logger.exception('Command setResource')
                        response = ResponseType.WRONG_FORMAT_INPUT

                # Query
                elif command.startswith('query'):
                    try:
                        match = re.search(r'query (.*)', command)
                        if hasattr(match, 'group'):
                            response = self.manager.instr_query(match.group(1))
                        else:
                            response = ResponseType.WRONG_FORMAT_INPUT
                    except IndexError:
                        logger.exception('Command query')
                        response = ResponseType.WRONG_FORMAT_INPUT

                # Write
                elif command.startswith('write'):
                    try:
                        match = re.search(r'write (.*)', command)
                        if hasattr(match, 'group'):
                            response = self.manager.instr_write(match.group(1))
                        else:
                            response = ResponseType.WRONG_FORMAT_INPUT
                    except IndexError:
                        logger.exception('Command write')
                        response = ResponseType.WRONG_FORMAT_INPUT

                # Others
                else:
                    if command == 'instrConnect':
                        response = self.manager.instr_connect()
                    elif command == 'instrDisconnect':
                        response = self.manager.instr_disconnect()
                    elif command == 'instrConfig':
                        response = self.manager.instr_config()

                connection.sendall('{}\r\n'.format(response).encode('utf-8'))
                logger.debug('Command {} Length {}'.format(command, response))
        except:
            logger.exception('Connection exception')
        finally:
            logger.warning('Connection closed')
            connection.close()

