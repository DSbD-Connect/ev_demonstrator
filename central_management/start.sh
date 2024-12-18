#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [on|off]"
    exit
fi

docker compose down
# pkill lt

case "$1" in
    on)  source .env-connect
         ln -sf .env-connect .env
         ;;
    off) source .env-no-connect
         ln -sf .env-no-connect .env
         ;;
    *)   echo "Usage: $0 [on|off]" ;;
esac

# lt -s dsbd-cms-001 --port $CENTRAL_MANAGEMENT_SERVER_API_PORT &

# curl https://loca.lt/mytunnelpassword
# echo "Go to https://dsbd-cms-001.loca.lt and enter the password above to activate the tunnel"

docker compose up -d
