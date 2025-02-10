#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [on|off]"
    exit
fi

docker compose down

case "$1" in
    on)  source .env-connect
         ln -sf .env-connect .env
         ;;
    off) source .env-no-connect
         ln -sf .env-no-connect .env
         ;;
    *)   echo "Usage: $0 [on|off]" ;;
esac

docker compose up server client hw-manager -d

# Replace 'charging_station-hw-manager-1' with the correct name
CONTAINER_NAME=$(docker ps -a --filter "name=charging_station-hw-manager" --format "{{.Names}}")

if [ -z "$CONTAINER_NAME" ]; then
    echo "No container found with the name charging_station-hw-manager"
    exit 1
fi

export AUDITBEAT_WATCHDIR=$(docker inspect "$CONTAINER_NAME" | grep -i merged | cut -d'"' -f4)
echo "AUDITBEAT_WATCHDIR: $AUDITBEAT_WATCHDIR"

docker compose up auditbeat
