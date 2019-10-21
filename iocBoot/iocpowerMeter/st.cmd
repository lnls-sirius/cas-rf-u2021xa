#!../../bin/linux-x86_64/powerMeter

< envPaths

cd "${TOP}"

epicsEnvSet("STREAM_PROTOCOL_PATH", "${TOP}/db")
epicsEnvSet("EPICS_CA_MAX_ARRAY_BYTES", "1073676294")

dbLoadDatabase "dbd/powerMeter.dbd"
powerMeter_registerRecordDeviceDriver pdbbase

drvAsynIPPortConfigure("L0", "unix://${TOP}/U2021XAVisaInterface/socket-1")

dbLoadRecords("db/devU2021XA.db", "P=RA-RF:PowerSensor1,R=:,PORT=L0,A=0")
dbLoadRecords("db/debug.db",      "P=RA-RF:PowerSensor1,R=:,PORT=L0,A=0")

save_restoreSet_DatedBackupFiles(1)
save_restoreSet_NumSeqFiles(2)
save_restoreSet_SeqPeriodInSeconds(600)

cd "${TOP}/iocBoot/${IOC}"
iocInit

cd "${TOP}"
create_monitor_set("autosave/Config.req", 10, "P=RA-RF:PowerSensor1,R=:,")

epicsThreadSleep(10)
fdbrestoreX("Config.sav")
