# Sirius RF - Keysight U2021XA IOC

## Description

PyVisa is used to communicate with the instrument. PyVISA-py seems to work just fine as a backend.

### Requirements

EPICS base 3.15.8+ and the modules listed at `./configure/RELEASE.tmplt`.
Python 3.7+ and the modules listed at `./scripts/requirements.txt`.

### Usage

Build the IOC.
Package `gettext` is recommended in order to generate `configure/RELEASE`.

```bash
envsubst < ./configure/RELEASE.tmplt > ./configure/RELEASE
```

Start the python script that will interface with VISA.
```bash
./script/run.py --resource <visa_resource>
```

Start the IOC.
```bash
cd iocBoot/iocpowerMeter
./st.cmd
```

### NI-VISA

```bash
wget https://download.ni.com/support/softlib/MasterRepository/LinuxDrivers2020/NILinux2020DeviceDrivers.zip
unzip NILinux2020DeviceDrivers.zip
yum install ni-software-2020-20.1.0.49152-0+f0.el7.noarch.rpm
yum install ni-visa ni-serial ni-488 libusb-ni1 libni4882 libusb
dkms autoinstall
```

More info at https://www.ni.com/pt-br/support/documentation/supplemental/18/downloading-and-installing-ni-driver-software-on-linux-desktop.html
