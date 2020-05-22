#!/bin/bash

generate_auth(){
token="$(oathtool -b --totp  $AUTH_SECRET)"
cat > ./token.txt <<EOF
$VPN_USER
$VPN_PASS${token}
EOF
}

run_vpn(){
config=$1
sudo -S openvpn --config $config --auth-nocache --auth-user-pass ./token.txt --daemon
}

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

cd "$parent_path"

if [ -n "${VPN}" ] && [ "${VPN}" = '1' ]; then
    generate_auth
    run_vpn $CONFIG_FILE
    sleep 10
    python3 pull.py 
    sleep 10
    sudo pkill openvpn
    sleep 10
    python3 scrape.py
    sleep 10
    generate_auth
    run_vpn $CONFIG_FILE
    sleep 5
    python3 send.py
else
    python3 run_cron.py 
fi
