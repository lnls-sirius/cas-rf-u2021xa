# Sirius RF - Keysight U2021XA IOC

## Description

PyVisa is used to communicate with the instrument.
StreamDevice based IOC.

Package gettext is required

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

### NI-VISA

```command
wget https://download.ni.com/support/softlib/MasterRepository/LinuxDrivers2020/NILinux2020DeviceDrivers.zip
unzip NILinux2020DeviceDrivers.zip
yum install ni-software-2020-20.1.0.49152-0+f0.el7.noarch.rpm
yum install ni-visa
sudo dkms autoinstall
```

https://www.ni.com/pt-br/support/documentation/supplemental/18/downloading-and-installing-ni-driver-software-on-linux-desktop.html
