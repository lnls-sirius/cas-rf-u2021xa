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

drvAsynIPPortConfigure("L0", "unix://${TOP}/U2021XAVisaInterface/unix-socket")

## Load record instances
dbLoadRecords("db/devU2021XA.db","P=Test,R=:,PORT=L0,A=0")

cd "${TOP}/iocBoot/${IOC}"
iocInit

# enable debug output
#var streamDebug 1

