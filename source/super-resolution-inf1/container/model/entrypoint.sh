#!/bin/bash

sed -i 's/\"shmem_enabled\":\ true/\"shmem_enabled\":\ false/g' /opt/aws/neuron/config/neuron-rtd.config
wait_for_nrtd() {
  nrtd_sock="/run/neuron.sock"
  SOCKET_TIMEOUT=60
  is_wait=true
  wait_time=0
  i=1
  sp="/-\|"
  echo -n "Waiting for neuron-rtd  "
  pid=$1
  while $is_wait; do
    if [ -S "$nrtd_sock" ]; then
      echo "$nrtd_sock Exist..."
      is_wait=false
    else
      sleep 1
      wait_time=$((wait_time + 1))
      if [ "$wait_time" -gt "$SOCKET_TIMEOUT" ]; then
        echo "neuron-rtd failed to start, exiting"
          cat /tmp/nrtd.log
        exit 1
      fi
      printf "\b${sp:i++%${#sp}:1}"
    fi
  done
  cat /tmp/nrtd.log
}


nrtd_present=0
if [[ -z "${NEURON_RTD_ADDRESS}" ]]; then
  # Start neuron-rtd
  /opt/aws/neuron/bin/neuron-rtd -g unix:/run/neuron.sock --log-console  >>  /tmp/nrtd.log 2>&1 &
  nrtd_pid=$!
  echo "NRTD PID: "$nrtd_pid""
  #wait for nrtd to be up (5 minutes timeout)
  wait_for_nrtd $nrtd_pid
  export NEURON_RTD_ADDRESS=unix:/run/neuron.sock
  nrtd_present=1
else
  echo "Neuron RTD is running as a side car container...."
fi

python predictor.py