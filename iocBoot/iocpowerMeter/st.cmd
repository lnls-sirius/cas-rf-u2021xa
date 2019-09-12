#!../../bin/linux-x86_64/powerMeter

## You may have to change powerMeter to something else
## everywhere it appears in this file

< envPaths

cd "${TOP}"

epicsEnvSet("STREAM_PROTOCOL_PATH", "${TOP}/db")
epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "1073676294")

## Register all support components
dbLoadDatabase "dbd/powerMeter.dbd"
powerMeter_registerRecordDeviceDriver pdbbase

drvAsynIPPortConfigure("L0", "unix://${TOP}/U2021XAVisaInterface/socket-1")
#drvAsynIPPortConfigure("L1", "unix://${TOP}/U2021XAVisaInterface/socket-2")

## Load record instances
dbLoadRecords("db/devU2021XA.db","P=RA-RF:PowerSensor1,R=:,PORT=L0,A=0")
#dbLoadRecords("db/devU2021XA.db","P=RA-RF:PowerSensor2,R=:,PORT=L1,A=0")

cd "${TOP}/iocBoot/${IOC}"
iocInit

#var streamDebug 1
