# Sirius RF - Keysight U2021XA IOC

## Description

PyVisa is used to communicate with the instrument.
StreamDevice based IOC.

### Usage

Start the Unix socket at `U2021XAVisaInterface/run.py`:
Run the IOC:
```
cd iocBoot/iocpowerMeter
./st.cmd
```

### Dependencies
Virtual environment
```
pip3 -m virtualenv U2021XAVisaInterface/venv
source ./U2021XAVisaInterface/venv/bin/activate
pip3 install -r U2021XAVisaInterface/requirements.txt
```
