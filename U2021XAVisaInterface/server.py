import logging
import os
import socket
import visa
import struct
import re
import usb

logger = logging.getLogger()

NO_RESPONSE = 'NO_RESPONSE'
WRONG_FORMAT = 'WRONG_FORMAT'
EXCEPTION = 'EXCEPTION'
OK = 'OK'
INSTR_DISCONNECTED = 'INSTR_DISCONNECTED'
USB_ERROR = 'USB_ERROR'

class VisaManager():

    def __init__(self, resource, trac_time):
        self.rm = visa.ResourceManager('@py')
        self.resource_str = resource
        self.instr = None
        self.instr_timeout = 5000

        self.trac_time = trac_time

    def list_resources(self):
        return str(list(self.rm.list_resources()))

    def instr_connect(self):
        try:
            self.instr = self.rm.open_resource(self.resource_str)
            self.instr.timeout = self.instr_timeout
            return str(self.instr)

        except usb.core.USBError:
            logger.exception('instr_connect usb error')
            return USB_ERROR
        except:
            logger.exception('instr_connect error')
            return EXCEPTION


    def instr_disconnect(self):
        try:
            if self.instr:
                self.instr.close()
                self.instr = None

            return INSTR_DISCONNECTED
        except:
            logger.exception('instr_disconnect error')
            return EXCEPTION

    def instr_info(self):
        if not self.instr:
            return INSTR_DISCONNECTED

        return self.instr

    def instr_init(self):
        if not self.instr:
            return INSTR_DISCONNECTED

        try:
            self.instr.write('*RST')
            self.instr.write('TRIG:SOUR EXT')
            self.instr.write('INIT:CONT OFF')
            self.instr.write('TRAC:STAT ON')
            self.instr.write('AVER:STAT OFF')
            self.instr.write('SENS:TRAC:TIME {}'.format(self.trac_time))
            return OK
        except:
            logger.exception('Instr Init')
            return EXCEPTION

    def instr_query(self, param):
        if not self.instr:
            return INSTR_DISCONNECTED
        try:
            return str(self.instr.query(param))
        except:
            logger.exception('Instr query')
            return EXCEPTION

    def instr_write(self, param):
        if not self.instr:
            return INSTR_DISCONNECTED
        try:
            return str(self.instr.write(param))
        except:
            logger.exception('Instr write')
            return EXCEPTION


    def instr_trac_data(self):
        if not self.instr:
            return INSTR_DISCONNECTED

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
            else:
                res = EXCEPTION
                logger.error('Wrong format response') 
            return str(res)
        except:
            logger.exception('Instr trac data')
            return EXCEPTION

        
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
                response = NO_RESPONSE

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
                    elif command == 'getResources':
                        response =  self.manager.list_resources()

                # Set
                elif command.startswith('setTracTime'):
                    try:
                        match = re.search(r'setTracTime (\d+?\.?\d*)', command)
                        if hasattr(match, 'group'):
                            self.manager.trac_time = float(match.group(1))
                            response = self.manager.trac_time
                        else:
                            response = EXCEPTION

                    except IndexError:
                        response = 'Wrong command format'

                # Query
                elif command.startswith('query'):
                    try:
                        match = re.search(r'query (.*)', command)
                        if hasattr(match, 'group'):
                            response = self.manager.instr_query(match.group(1))
                        else:
                            response = WRONG_FORMAT
                    except IndexError:
                        response = EXCEPTION

                # Write
                elif command.startswith('write'):
                    try:
                        match = re.search(r'write (.*)', command)
                        if hasattr(match, 'group'):
                            response = self.manager.instr_write(match.group(1))
                        else:
                            response = WRONG_FORMAT
                    except IndexError:
                        response = EXCEPTION

                # Others
                else:
                    if command == 'instrConnect':
                        response = self.manager.instr_connect()
                    elif command == 'instrDisconnect':
                        response = self.manager.instr_disconnect()
                    elif command == 'instrInit':
                        response = self.manager.instr_init()

                connection.sendall('{}\r\n'.format(response).encode('utf-8'))
                logger.debug('Command {} Length {}'.format(command, response))
        except:
            logger.exception('Connection exception')
        finally:
            logger.warning('Connection closed')
            connection.close()

