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

docker compose up -d
