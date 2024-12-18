#!/bin/bash

cd server/
chmod +x build-cmpt.sh
./build-cmpt.sh
chmod +x auth_cheri.o
chmod +x auth_noncheri.o
cd ..

docker build -t central_management-server server --network host