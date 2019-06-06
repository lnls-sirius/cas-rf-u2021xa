# Sirius RF - Keysight U2021XA IOC

## Description

PyVisa is used to communicate with the instrument.
StreamDevice based IOC.

### Usage

Run the Unix socket:
```
cd U2021XAVisaInterface
./run
```

Run the IOC:
```
cd iocBoot/iocpowerMeter
./st.cmd
```

### Dependencies
```
pyusb==1.0.2
PyVISA==1.9.1
PyVISA-py==0.3.1
```

Author: Cláudio Ferreira Carneiro

### Credits: 
[Victor Carneiro Lima](https://github.com/vclima/power_sensor.git)
