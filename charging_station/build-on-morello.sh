chmod +x build_target_process.sh
./build_target_process.sh

gcc hw-manager/ev_sensor.c -o hw-manager/ev_sensor
rm -r client/node_modules

docker build --no-cache -t charging_station-server server --network host
docker build --no-cache -t charging_station-client client --network host
docker build --no-cache -t charging_station-hw-manager hw-manager --network host