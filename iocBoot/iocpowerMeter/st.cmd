#!../../bin/linux-x86_64/powerMeter

< envPaths

cd "${TOP}"

epicsEnvSet("STREAM_PROTOCOL_PATH", "${TOP}/db")
epicsEnvSet("VISA_SOCK", "${TOP}/sockets/visa.sock")

dbLoadDatabase "dbd/powerMeter.dbd"
powerMeter_registerRecordDeviceDriver pdbbase
asSetFilename("${TOP}/db/Security.as")

drvAsynIPPortConfigure("L0", "unix://${VISA_SOCK}")

dbLoadRecords("db/devU2021XA.db", "P=RA-RF:PowerSensor1,R=:,PORT=L0,A=0")
dbLoadRecords("db/debug.db",      "P=RA-RF:PowerSensor1,R=:,PORT=L0,A=0")

#save_restoreSet_DatedBackupFiles(1)
#save_restoreSet_NumSeqFiles(2)
#save_restoreSet_SeqPeriodInSeconds(600)

cd "${TOP}/iocBoot/${IOC}"
iocInit

caPutLogInit "$(EPICS_IOC_CAPUTLOG_INET):$(EPICS_IOC_CAPUTLOG_PORT)" 2

cd "${TOP}"

