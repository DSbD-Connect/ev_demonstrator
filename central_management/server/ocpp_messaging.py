import asyncio
import logging
import websockets
import uuid
import os
from datetime import datetime
from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call_result
from ocpp.v201 import call
from ocpp.v201.enums import RegistrationStatusType, Action
from db_manager import db_manager

logging.basicConfig(level=logging.INFO)


class ChargingSession:
    def __init__(self, charging_station_id, username, start_time):
        self.total_energy = 0
        self.total_price = 0
        self.start_time = start_time
        self.stop_time = None
        self.charging_station_id = charging_station_id
        self.username = username

    def to_dict(self):

        return {
            'charging_station_id': self.charging_station_id,
            'user_id': self.username,
            'start_time': datetime.fromtimestamp(self.start_time) if self.start_time else None,
            'stop_time':  datetime.fromtimestamp(self.stop_time) if self.stop_time else None,
            'total_price': self.total_price,
            'total_energy':  self.total_energy,
            'tariff': 0.30
        }


class ChargePoint(cp):

    @on('BootNotification')
    async def on_boot_notification(self, charging_station, reason, **kwargs):
        self.status = "Ready"
        asyncio.create_task(self.set_charging_profile())
        return call_result.BootNotificationPayload(   
            status=RegistrationStatusType.accepted,
            current_time=datetime.utcnow().isoformat(),
            interval=10,
        )

    async def send_remote_start(self, username):
        if self.remote_start_id is None:
            self.remote_start_id = 0

        self.transaction_id = str(uuid.uuid4())
        req = call.RequestStartTransaction(
                id_token={"id_token": self.transaction_id, "type": "Central"},
                remote_start_id=self.remote_start_id,
                evse_id=1
            )
        response = await self.call(req)
        self.remote_start_id += 1
        self.status = "Charging"
        self.charging_session = ChargingSession(self.id, username, datetime.now().timestamp())
        logging.info("Sent Remote Start Command")
        return response

    async def send_remote_stop(self):
        req = call.RequestStopTransaction(self.transaction_id)
        response = await self.call(req)
        logging.info("Sent Remote Stop Command")
        self.status = "Summary"
        custom_data_json = response.custom_data
        self.charging_session.total_energy = custom_data_json["session_status"]["total_energy"]
        self.charging_session.total_price = custom_data_json["session_status"]["total_price"]
        self.charging_session.stop_time = custom_data_json["session_status"]["stop_time"]
        db_manager().save_session(self.charging_session.to_dict())
        return response

    async def verify_customer_info(self, data):
        req = call.DataTransfer(
            vendor_id="ACME",
            data=data
        )

        response = await self.call(req)
        logging.info("Sent Customer Data Command")
        return response

    async def set_charging_profile(self):
        tariff = {
            "id": 1,
            "price_per_kwh": 0.30,
        }

        chargingProfile = {
            "id": tariff["id"],
            "stackLevel": 0,
            "chargingProfilePurpose": "TxProfile",
            "chargingProfileKind": "Absolute",
            "chargingSchedule": [
                {
                    "id": 1,
                    "chargingRateUnit": "W",
                    "chargingSchedulePeriod": [
                        {
                            "startPeriod": 0,
                            "limit": 10000,
                            "customData": {
                                "vendor_id": "ACME",
                                "tariff": {
                                    "price": 0.2,
                                    "currency": "GBP"
                                }
                            }
                        }
                    ]
                }
            ]
        }

        response = await self.call(
            call.SetChargingProfile(
                evse_id=1,
                charging_profile=chargingProfile
            )
        )
        logging.info("Sent Set Charging Profile")
        return response

    @on(Action.RequestStopTransaction)
    async def on_stop_transaction(self, transaction_id, custom_data):

        if transaction_id == self.transaction_id:
            self.transaction_status = "Accepted"
            self.charging_session.total_energy = custom_data["session_status"]["total_energy"]
            self.charging_session.total_price = custom_data["session_status"]["total_price"]
            self.charging_session.stop_time = custom_data["session_status"]["stop_time"]
            db_manager().save_session(self.charging_session.to_dict())
            self.status = "Summary"
        else:
            self.transaction_status = "Rejected"

        return call_result.RequestStopTransactionPayload(
            status=self.transaction_status,
        )

    @on(Action.Reset)
    async def on_reset(self, type):
        self.status = "Ready"
        return call_result.ResetPayload(
            status="Accepted",
        )

    @on(Action.DataTransfer)
    async def on_session_info(self, vendor_id, data):
        try:
            self.charging_session.start_time = data["start_time"]
            self.charging_session.total_energy = data["total_energy"]
            self.charging_session.total_price = data["total_price"]
            if "stop_time" in data:
                self.charging_session.stop_time = data["stop_time"]

            return call_result.DataTransfer(
                status="Accepted"
            )

        except Exception as e:
            logging.error(f"Error processing Data Transfer: {e}")
            return call_result.DataTransfer(
                status="Rejected"
            )


class Central_Management:

    def __init__(self):
        self.charging_points = {}

    async def on_connect(self, websocket, path):
        """ For every new charge point that connects, create a ChargePoint
        instance and start listening for messages.
        """
        try:
            requested_protocols = websocket.request_headers[
                'Sec-WebSocket-Protocol']
        except KeyError:
            logging.info("Client hasn't requested any Subprotocol. "
                    "Closing Connection")
            return await websocket.close()

        if websocket.subprotocol:
            logging.info("Protocols Matched: %s", websocket.subprotocol)
        else:
            # In the websockets lib if no subprotocols are supported by the
            # client and the server, it proceeds without a subprotocol,
            # so we have to manually close the connection.
            logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                            ' but client supports  %s | Closing connection',
                            websocket.available_subprotocols,
                            requested_protocols)
            return await websocket.close()

        charge_point_id = path.strip('/')
        cp = ChargePoint(charge_point_id, websocket)
        cp.remote_start_id = 0
        cp.charging_session = None
        self.charging_points[charge_point_id] = cp        
        await cp.start()
        cp.status = "Ready"
        print("Registered charge point with id: ", charge_point_id)
        logging.info("Registered charge point with id: " + charge_point_id)

    async def main(self):
        server = await websockets.serve(
            self.on_connect,
            '0.0.0.0',
            os.environ["CENTRAL_MANAGEMENT_SERVER_OCPP_PORT"],
            subprotocols=['ocpp2.0.1']
        )
        logging.info("WebSocket Server Started")
        await server.wait_closed()
