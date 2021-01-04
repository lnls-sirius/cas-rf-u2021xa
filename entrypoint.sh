#!/bin/bash
echo "##########################################################################"
echo "# ProcServControl - unix:"${PCTRL_SOCK}
echo "#     In order to connect: \"socat - UNIX-CLIENT:${PCTRL_SOCK}"
echo "##########################################################################"
echo ""
/usr/local/bin/procServ \
    --holdoff 2 \
    --logfile - \
    --chdir "$(pwd)/procCtrl/iocBoot/iocprocCtrl" \
    --foreground \
    --ignore ^D^C \
    --name "${NAME}-PCTRL-IOC" \
    'unix:'${PCTRL_SOCK} ./st.cmd &

sleep 4

echo ""
echo ""
echo "##########################################################################"
echo "# ${NAME} - Port ${IOC_PROCSERV_SOCK}"
echo "# ${NAME} - Port ${DEVICE_PROCSERV_SOCK}"
echo "##########################################################################"
echo ""

function ioc {
    /usr/local/bin/procServ \
    --chdir "$(pwd)/iocBoot/iocpowerMeter/" \
    --foreground \
    --holdoff 2 \
    --ignore ^D^C \
    --logfile - \
    --name "${NAME}-IOC" \
    --pidfile "$(pwd)/pids/ioc" \
    unix:${IOC_PROCSERV_SOCK} ./${CMD} &
}

function device {
    /usr/local/bin/procServ \
        --chdir "$(pwd)/U2021XAVisaInterface" \
        --foreground \
        --holdoff 2 \
        --ignore ^D^C \
        --logfile - \
        --name "${NAME}-IOC" \
        --pidfile "$(pwd)/pids/device" \
        unix:${DEVICE_PROCSERV_SOCK} \
        /bin/bash -c "\
            /usr/local/bin/python \
                $(pwd)/U2021XAVisaInterface/run.py \
                --resource ${VISA_INSTR} \
                --unix-socket-path ${VISA_SOCK}" &
}

while true; do
    DEVICE_PID=$(cat $(pwd)/pids/device)
    [[ -n ${DEVICE_PID} ]] && [[ -d "/proc/${DEVICE_PID}" ]] || device

    IOC_PID=$(cat $(pwd)/pids/ioc)
    [[ -n ${IOC_PID} ]] && [[ -d "/proc/${IOC_PID}" ]] || ioc

    sleep 2
done;
