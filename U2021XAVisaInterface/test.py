#!/usr/bin/env python

import visa
import time

visa.log_to_screen()
rm = visa.ResourceManager("@py")
instr = rm.list_resources()
print(instr, "\n\n")
instr = rm.open_resource(instr[3])
instr.timeout = 5000


def try_to_clear():
    print("---------------------")
    print("*RST", instr.write("*RST"))  # Reset device config
    print(":TRIG:SOUR EXT", instr.write(":TRIG:SOUR EXT"))
    print(":INIT:CONT OFF", instr.write(":INIT:CONT OFF"))
    print(":TRIG:DEL:AUTO OFF", instr.write("TRIG:DEL:AUTO OFF"))
    print(":TRAC:STAT ON", instr.write(":TRAC:STAT ON"))
    print(":AVER:STAT OFF", instr.write(":AVER:STAT OFF"))
    print(":SENS:TRAC:TIME 0.42", instr.write(":SENS:TRAC:TIME 0.42"))
    print(":ABORT", instr.write("ABORT"))  # Abort op
    print("*CLS", instr.write("*CLS"))  # Reset all errors
    try:
        print(":SYST:ERR?", instr.query(":SYST:ERR?"))
    except:
        pass


def get_trac():
    print("---------------------")
    print(instr.write(":INIT"))
    print(instr.write(":TRAC:DATA? MRES"))
    print(instr.read_raw())


def get_data():
    print("---------------------")
    instr.write("INIT")
    print(instr.query("FETC?"))


while True:
    try_to_clear()
    get_data()
    get_trac()
    time.sleep(1)

# print(instr.query(':SYST:ERR?'))
# print(instr.query('STAT:DEV:COND?')) # Device status
# print(instr.query('STAT:DEV?'))
print("---------------------")
print("*IDN?", instr.query("*IDN?"))
print(":TRIG:SOUR?", instr.query(":TRIG:SOUR?"))
print(":INIT:CONT?", instr.query(":INIT:CONT?"))
print(":AVER:STAT?", instr.query(":AVER:STAT?"))
print(instr.query("*ESR?"))
print("---------------------\n\n")

print("---------------------")
print(":CORR:GAIN2?", instr.query(":CORR:GAIN2?"))
print(":CORR:GAIN2:STAT?", instr.query(":CORR:GAIN2:STAT?"))
print(":CORR:LOSS2?", instr.query(":CORR:LOSS2?"))
print(":CORR:LOSS2:STAT?", instr.query(":CORR:LOSS2:STAT?"))
print(":SENS:DET:FUNC?", instr.query(":SENS:DET:FUNC?"))
print("---------------------\n\n")
exit(0)
print("---------------------")
print(":TRAC:STAT OFF", instr.write(":TRAC:STAT OFF"))
print(":AVER:STAT ON", instr.write(":AVER:STAT ON"))
print(":INIT", instr.write(":INIT"))
print(":FETC?", instr.write(":FETC?"))
print(instr.read_raw())
print("---------------------\n\n")


instr.close()
rm.close()


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
