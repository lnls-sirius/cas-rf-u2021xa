# Author: Cláudio Ferreira Carneiro
# LNLS - Brazilian Synchrotron Light Source Laboratory

FROM  lnlscon/epics-r3.15.8:v1.2 AS base
LABEL maintainer="Claudio Carneiro <claudio.carneiro@lnls.br>"

# VIM
RUN apt-get -y update && apt-get -y install \
    libusb-1.0-0-dev \
    procps \
    socat \
    vim

# Epics auto addr list
ENV EPICS_CA_AUTO_ADDR_LIST YES

# Base procServ port
ENV EPICS_IOC_CAPUTLOG_INET 0.0.0.0
ENV EPICS_IOC_CAPUTLOG_PORT 7012
ENV EPICS_IOC_LOG_INET 0.0.0.0
ENV EPICS_IOC_LOG_PORT 7011

ENV DEVICE_PROCSERV_SOCK /opt/PowerMeterIOC/sockets/device.sock
ENV IOC_PROCSERV_SOCK /opt/PowerMeterIOC/sockets/ioc.sock
ENV PCTRL_SOCK /opt/PowerMeterIOC/procCtrl/sockets/pCtrl.sock

RUN mkdir -p /opt/PowerMeterIOC/autosave && mkdir -p /opt/PowerMeterIOC/pids

WORKDIR /opt/PowerMeterIOC
COPY requirements.txt /opt/PowerMeterIOC/requirements.txt
RUN pip install -r requirements.txt

COPY Makefile /opt/PowerMeterIOC/Makefile
COPY U2021XAVisaInterface /opt/PowerMeterIOC/U2021XAVisaInterface
COPY autosave /opt/PowerMeterIOC/autosave
COPY configure /opt/PowerMeterIOC/configure
COPY iocBoot /opt/PowerMeterIOC/iocBoot
COPY powerMeterApp /opt/PowerMeterIOC/powerMeterApp
COPY procCtrl /opt/PowerMeterIOC/procCtrl

RUN cd /opt/PowerMeterIOC/procCtrl && envsubst < configure/RELEASE.tmplt > configure/RELEASE &&\
    cat configure/RELEASE && make distclean && make clean && make -j$(nproc) && mkdir sockets &&\
    \
    cd /opt/PowerMeterIOC/ && mkdir sockets && envsubst < configure/RELEASE.tmplt > configure/RELEASE &&\
    make -j$(nproc)

ENV NAME RF-TCU6
ENV CMD st.cmd
ENV IOC_PROCSERV_PREFIX PCtrl:${NAME}
ENV DEVICE_PROCSERV_PREFIX PCtrl:${NAME}-Device
ENV VISA_SOCK /opt/PowerMeterIOC/sockets/visa.sock
ENV VISA_INSTR USB0::2391::32536::MY57370012::0::INSTR

ENV EPICS_CA_MAX_ARRAY_BYTES 1073676294

COPY entrypoint.sh /opt/PowerMeterIOC/entrypoint.sh

ENTRYPOINT [ "/bin/bash", "/opt/PowerMeterIOC/entrypoint.sh" ]

