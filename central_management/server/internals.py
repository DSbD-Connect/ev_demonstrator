import asyncio
import logging


def verify_start_request(cm, loop, charging_point_id, request_data):

    vehicle_id = request_data["vehicle_id"]
    logging.info(charging_point_id)
    logging.info(vehicle_id)
    return _verify_vehicle_on_cs(cm, loop, charging_point_id, vehicle_id)


def _verify_vehicle_on_cs(cm, loop, charging_point_id, vehicle_id):

    data = {"charging_point_id": charging_point_id, "vehicle_id": vehicle_id}
    future = asyncio.run_coroutine_threadsafe(
            cm.charging_points[charging_point_id].verify_customer_info(data),
            loop
    )
    response = future.result()
    if (response.status == "Accepted"):
        return True
    else:
        return False
