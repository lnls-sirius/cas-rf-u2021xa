TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build the IOC application

PROD_IOC = powerMeter

# powerMeter.dbd will be created and installed
DBD += powerMeter.dbd

# powerMeter.dbd will be made up from these files:
powerMeter_DBD += base.dbd
powerMeter_DBD += calcSupport.dbd
powerMeter_DBD += asyn.dbd
powerMeter_DBD += stream.dbd
powerMeter_DBD += drvAsynIPPort.dbd

# Include dbd files from all support applications:
#powerMeter_DBD += xxx.dbd

# Add all the support libraries needed by this IOC
powerMeter_LIBS += stream
powerMeter_LIBS += asyn
powerMeter_LIBS += calc

# powerMeter_registerRecordDeviceDriver.cpp derives from powerMeter.dbd
powerMeter_SRCS += powerMeter_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
powerMeter_SRCS_DEFAULT += powerMeterMain.cpp
powerMeter_SRCS_vxWorks += -nil-

# Add support from base/src/vxWorks if needed
#powerMeter_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Finally link to the EPICS Base libraries
powerMeter_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

