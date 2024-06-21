#!/bin/bash
if [ -z "$1" ]
  then 
    read -p "Enter VPN user number TO REMOVE: " USERNAME
    if [ -z $USERNAME ]
      then
      echo "[#]Empty VPN user number. Exit"
      exit 1;
    fi
  else USERNAME=$1
fi

cd /etc/wireguard/
