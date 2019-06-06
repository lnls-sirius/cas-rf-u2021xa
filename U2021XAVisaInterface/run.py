#!/usr/bin/python3

import argparse
import logging
import time 
import visa
import struct

time=0.41

def initialize():
        rm=visa.ResourceManager('@py')
        PS=rm.open_resource('USB0::2391::32536::MY57380004::0::INSTR')
        PS.timeout=None
        PS.write('*RST')
        PS.write('TRIG:SOUR EXT')
        PS.write('INIT:CONT OFF')
        PS.write('TRAC:STAT ON')
        PS.write('AVER:STAT OFF')
        PS.write('SENS:TRAC:TIME '+str(time))
        print("Init ok")
        start_flag=1;
        return [PS,rm]

def read(PS):

        PS.write('INIT')
        print("Read set")
        PS.write('TRAC:DATA? MRES')
        data = PS.read_raw()

        char_data = [] 

        if chr(data[0]) == '#':
            x = int(chr(data[1]))
            y = int(data[2:2+x])

            d_bytes = data[2+x:-1]
             
            print(data[0], x, y, type(y), len(d_bytes))
            res = [struct.unpack('>f', d_bytes[4*i:4*i+4])[0] for i in range(int(y/4))]
            print(res)
        else:
            print('Wrong format')
        
[PS,rm]=initialize()

while (1):
    read(PS)

if __name__ == '__main__':
    pass

