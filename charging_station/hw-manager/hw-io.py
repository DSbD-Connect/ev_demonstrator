import sys


def talk_to_vehicle(vehicle_id):
    if vehicle_id == "ACME":
        return True
    else:
        return False


vehicle_id = sys.argv[1]
if talk_to_vehicle(vehicle_id):
    sys.exit(0)
else:
    sys.exit(-1)
