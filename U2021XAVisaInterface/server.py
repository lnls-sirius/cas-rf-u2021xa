import logging
import os
import socket
import visa
import struct

logger = logging.getLogger()

class VisaManager():

    def __init__(self, resource, trace_time):
        self.rm = visa.ResourceManager('@py')
        self.resource_str = resource
        self.instr = self.rm.open_resource(self.resource_str)
        self.instr.timeout = None # Use or not?
        self.trace_time = str(trace_time)

    def list_resources(self):
        return str(list(self.rm.list_resources())) + '\r\n'

    def instr_info(self):
        return str(self.instr) + '\r\n'

    def instr_init(self):
        self.instr.write('*RST')
        self.instr.write('TRIG:SOUR EXT')
        self.instr.write('INIT:CONT OFF')
        self.instr.write('TRAC:STAT ON')
        self.instr.write('AVER:STAT OFF')
        self.instr.write('SENS:TRAC:TIME {}'.format(self.trace_time))

    def instr_trac_data(self):

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
            res = 'ERROR'
            logger.error('Wrong format')
        return str(res) + '\r\n'

        
class Comm():
    def __init__(self, unix_socket_path, resource, *args, **kwargs):
        self.unix_socket_path = unix_socket_path
        self.connection = None
        self.welcome_socket = None

        self.manager = VisaManager(resource=resource, trace_time=0.41)
        self.manager.instr_init()

        logger.info('Connected to {}'.format(self.manager.instr))


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
                response = self.manager.instr_trac_data()
                connection.sendall(response.encode('utf-8'))
                logger.debug('Command {} Length {}'.format(command, len(response)))
        except:
            logger.exception('Connection exception')
        finally:
            connection.close()

