#!/bin/bash
#ADD_CLIENT FOR VPNBOT! HAS A LOT OF MODIFIERS!!!
# We read from the input parameter the name of the client

#if [ -z "$1" ]
#  then 
#    read -p "Enter VPN user name: " USERNAME
#    if [ -z $USERNAME ]
#      then
#      echo "[#]Empty VPN user name. Exit"
#      exit 1;
#    fi
#  else USERNAME=$1
#fi

cd /etc/wireguard/

read DNS < ./dns.var
read ENDPOINT < ./endpoint.var
read VPN_SUBNET < ./vpn_subnet.var
PRESHARED_KEY="_preshared.key"
PRIV_KEY="_private.key"
PUB_KEY="_public.key"
ALLOWED_IP="0.0.0.0/0, ::/0"

# Go to the wireguard directory and create a directory structure in which we will store client configuration files
cd ./VPNBOT
read USERNAME <./usercounter.var


USERNAMEOLD=(USERNAME)
USERNAME=$((USERNAME + 1))
if [ USERNAME==$((USERNAMEOLD + 1)) ] 
then
    rm usercounter.var   
    echo "[#]Success"
    cat > /etc/wireguard/VPNBOT/usercounter.var << EOF
$USERNAME 
EOF
else
    echo "[#]Error"
    exit 1
fi

mkdir -p ./clients
cd ./clients
mkdir ./$USERNAME
cd ./$USERNAME
umask 777
	
CLIENT_PRESHARED_KEY=$( wg genpsk )
CLIENT_PRIVKEY=$( wg genkey )
CLIENT_PUBLIC_KEY=$( echo $CLIENT_PRIVKEY | wg pubkey )

#echo $CLIENT_PRESHARED_KEY > ./"$USERNAME$PRESHARED_KEY"
#echo $CLIENT_PRIVKEY > ./"$USERNAME$PRIV_KEY"
#echo $CLIENT_PUBLIC_KEY > ./"$USERNAME$PUB_KEY"

read SERVER_PUBLIC_KEY < /etc/wireguard/server_public.key

# We get the following client IP address
read OCTET_IP < /etc/wireguard/last_used_ip.var
OCTET_IP=$(($OCTET_IP+1))
echo $OCTET_IP > /etc/wireguard/last_used_ip.var

CLIENT_IP="$VPN_SUBNET$OCTET_IP/32"

# Create a blank configuration file client 
cat > /etc/wireguard/VPNBOT/clients/$USERNAME/$USERNAME.conf << EOF
[Interface]
PrivateKey = $CLIENT_PRIVKEY
Address = $CLIENT_IP
DNS = $DNS


[Peer]
PublicKey = $SERVER_PUBLIC_KEY
PresharedKey = $CLIENT_PRESHARED_KEY
AllowedIPs = $ALLOWED_IP
Endpoint = $ENDPOINT
PersistentKeepalive=25
EOF

#zip file to send
zip wireguardkey.zip $USERNAME.conf
chmod 777 wireguardkey.zip

# Add new client data to the Wireguard configuration file
cat >> /etc/wireguard/wg0.conf << EOF

[Peer]
PublicKey = $CLIENT_PUBLIC_KEY
PresharedKey = $CLIENT_PRESHARED_KEY
AllowedIPs = $CLIENT_IP
#USERNUM = $USERNAME
EOF

# Restart Wireguard
systemctl stop wg-quick@wg0
systemctl start wg-quick@wg0

# Show QR config to display
qrencode -t ansiutf8 < ./$USERNAME.conf

# Show config file
echo "# Display $USERNAME.conf"
cat ./$USERNAME.conf

# Save QR config to png file
#qrencode -t png -o ./$USERNAME.png < ./$USERNAME.conf