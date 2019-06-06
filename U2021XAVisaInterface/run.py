#!/usr/bin/python3
import argparse
import logging

import visa
import struct
import matplotlib.pyplot as plt
import numpy as np
time=0.41
def initialize():
        rm=visa.ResourceManager('@py')
        PS=rm.open_resource('USB0::2391::32536::MY57370012::0::INSTR')
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
        val=PS.read_raw()
        print("Read ok")
        offset=int(chr(val[1]))
        data=val[2+offset:-1]
        split = [struct.unpack('>f',(data[4*i:4*i+4])) for i in range (0, int(len(data)/4))]
        power=np.array(split)
        return power

[PS,rm]=initialize()

while (1):
    print(read(PS))

if __name__ == '__main__':
    pass

