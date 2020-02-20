#!/bin/bash

echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf
echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf

printenv | grep -v "no_proxy" >> /app/.env
sudo mv /app/.env /etc/environment
exec "$@"
sh cronset.sh
sh run.sh