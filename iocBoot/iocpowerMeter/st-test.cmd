#!../../bin/linux-x86_64/powerMeter

< envPaths

cd "${TOP}"

epicsEnvSet("STREAM_PROTOCOL_PATH", "${TOP}/db")

epicsEnvSet("P", "RA-RF:PowerSensor1")
epicsEnvSet("R", ":")

epicsEnvSet("TO_DEV_SOCK",   "${TOP}/scripts/in-socket")  # to device
epicsEnvSet("FROM_DEV_SOCK", "${TOP}/scripts/out-socket") # from device

dbLoadDatabase "dbd/powerMeter.dbd"
powerMeter_registerRecordDeviceDriver pdbbase
asSetFilename("${TOP}/db/Security.as")

drvAsynIPPortConfigure("TO", "unix://${TO_DEV_SOCK}")
drvAsynIPPortConfigure("FROM", "unix://${FROM_DEV_SOCK}")

dbLoadRecords("db/devUtils.db", "P=$(P),R=$(R),TO=TO,FROM=FROM,A=0")
dbLoadRecords("db/devGain.db", "P=$(P),R=$(R),TO=TO,FROM=FROM,A=0")
dbLoadRecords("db/devFreq.db", "P=$(P),R=$(R),TO=TO,FROM=FROM,A=0")
dbLoadRecords("db/devEgu.db", "P=$(P),R=$(R),TO=TO,FROM=FROM,A=0")
dbLoadRecords("db/devTracData.db", "P=$(P),R=$(R),TO=TO,FROM=FROM,A=0")

cd "${TOP}/iocBoot/${IOC}"
iocInit

cd "${TOP}"

# var streamDebug 0
