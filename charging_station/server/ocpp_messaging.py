import asyncio
import os
import websockets
import logging
import requests
import json

from ocpp.v201 import call
from ocpp.v201 import call_result
from ocpp.v201 import ChargePoint as cp
from ocpp.v201.enums import RegistrationStatusType, Action
from ocpp.routing import on
from datetime import datetime


logging.basicConfig(level=logging.INFO)


class ChargingSession:
    def __init__(self, start_time, price):
        self.total_energy = 0
        self.total_price = 0
        self.start_time = start_time
        self.stop_time = None
        self.interval = 0  # Seconds
        self.interval_thread = None
        self.sync_func = None
        self.price = price

    def start(self, sync_func):
        self.total_energy = 0
        self.interval = 2
        self.schedule_energy_update()
        self.sync_func = sync_func

    def schedule_energy_update(self):
        loop = asyncio.get_event_loop()
        self.interval_thread = loop.call_later(self.interval, lambda: asyncio.ensure_future(self.update_energy()))
        # timer.cancel()

    async def update_energy(self):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.get("http://" +
                                os.environ["CHARGING_STATION_SERVER_HOST"] +
                                ":" + os.environ["HARDWARE_MANAGER_API_PORT"] +
                                "/hw/current",
                                headers=headers)

        current = int(response.json())  # Amperes
        voltage = 230  # Volts
        kW = ((current * voltage)/1000)
        h = 1.0 / 3600  # 1 second in terms of 1 hour
        self.total_energy += kW * h
        print("updating energy", str(self.total_energy))
        self.total_price = self.total_energy * self.price
        self.schedule_energy_update()
        await self.sync_func()

    def stop(self):
        if self.interval_thread:
            self.stop_time = datetime.now().timestamp()
            self.interval = 0
            self.interval_thread.cancel()
            self.interval_thread = None

    def get_session_status(self):
        return {
            "start": self.start_time,
            "stop": self.stop_time,
            "total_energy": self.total_energy,
            "total_price": self.total_price
        }


class ChargePoint(cp):

    def __init__(self, id, connection):
        super().__init__(id, connection)
        self.status = "Not Ready"
        self.charging_session = None
        self.session_interval = 0  # Seconds
        self.charging_thread = None

    async def send_boot_notification(self):
        ocpp_request = call.BootNotificationPayload(
            charging_station={
                'model': 'EV v1',
                'vendor_name': 'ACME'
            },
            reason="PowerUp"
        )
        response = await self.call(ocpp_request)

        if response.status == RegistrationStatusType.accepted:
            print("Connected to central system.")
            self.status = "Ready"

    async def stop_transaction(self):
        if self.charging_session:
            self.charging_session.stop()

        session_data = {
            "vendor_id": "ACME",
            "session_status": {
                    "start_time": self.charging_session.start_time,
                    "stop_time": self.charging_session.stop_time,
                    "total_energy": self.charging_session.total_energy,
                    "total_price": self.charging_session.total_price,
                    "unit": "kWh"
            }
        }

        req = call.RequestStopTransaction(
            transaction_id=self.transaction_id,
            custom_data=session_data
        )

        response = await self.call(req)
        self.charging_session.stop()
        logging.info("Sent Stop Request to CMS")
        if response.status == "Accepted":
            self.status = "Summary"
        return response

    async def reset_charger(self):
        req = call.Reset(type="Immediate")
        response = await self.call(req)
        logging.info("Sent Reset Request to CMS")
        if response.status == "Accepted":
            self.status = "Ready"
        return response

    async def send_session_info(self):

        data = {
            "start_time": self.charging_session.start_time,
            "stop_time": self.charging_session.stop_time,
            "total_energy": self.charging_session.total_energy,
            "total_price": self.charging_session.total_price,
            "unit": "kWh"
        }
        req = call.DataTransfer(
            vendor_id="ACME",
            data=data
        )

        response = await self.call(req)
        logging.info("Sent Session Info")
        return response

    @on(Action.RequestStartTransaction)
    async def on_start_transaction(self, id_token, remote_start_id, evse_id=None):
        self.transaction_id = id_token['id_token']
        self.status = "Charging"
        price = self.charging_profile["charging_schedule"][0]["charging_schedule_period"][0]["custom_data"]["tariff"]["price"]
        self.charging_session = ChargingSession(datetime.now().timestamp(), price)
        self.charging_session.start(self.send_session_info)
        return call_result.RequestStartTransaction(
            status="Accepted"
        )

    @on(Action.RequestStopTransaction)
    async def on_stop_transaction(self, transaction_id):

        if transaction_id == self.transaction_id:
            self.transaction_status = "Accepted"
            self.status = "Summary"
        else: 
            self.transaction_status = "Rejected"

        if self.charging_session:
            self.charging_session.stop()

        session_data = {
            "vendor_id": "ACME",
            "session_status": {
                    "start_time": self.charging_session.start_time,
                    "stop_time": self.charging_session.stop_time,
                    "total_energy": self.charging_session.total_energy,
                    "total_price": self.charging_session.total_price,
                    "unit": "kWh"
            }
        }
        return call_result.RequestStopTransactionPayload(
            status=self.transaction_status,
            custom_data=session_data
        )

    @on(Action.DataTransfer)
    async def on_customer_information(self, vendor_id, data):

        verification_data = json.dumps({
            "vehicle_id": data["vehicle_id"]
        })
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post("http://" + 
                                 os.environ["CHARGING_STATION_SERVER_HOST"] +
                                 ":" + os.environ["HARDWARE_MANAGER_API_PORT"] +
                                 "/hw/verify",
                                 data=verification_data,
                                 headers=headers)
        ocpp_response = ""

        if (response.status_code == 200):
            ocpp_response = "Accepted"
        else:
            ocpp_response = "Rejected"

        return call_result.DataTransfer(
            status=ocpp_response,
        )

    @on(Action.SetChargingProfile)
    async def on_set_charging_profile(self, evse_id, charging_profile):
        self.charging_profile = charging_profile
        print(self.charging_profile)
        logging.info(self.charging_profile)
        return call_result.SetChargingProfile(
            status="Accepted"
        )

    @on(Action.ChangeAvailability)
    async def on_disable(self, operational_status):
        self.status = operational_status
        print(self.charging_profile)
        logging.info(self.charging_profile)
        return call_result.ChangeAvailability(
            status="Accepted"
        )


cp = None


async def main():
    central_management_server = os.environ["CENTRAL_MANAGEMENT_SERVER_HOST"]
    central_management_server_port = os.environ["CENTRAL_MANAGEMENT_SERVER_OCPP_PORT"]
    charging_point_id = os.environ["CHARGING_STATION_ID"]
    async with websockets.connect(
            'ws://' + central_management_server + ':' +
            central_management_server_port + '/' + charging_point_id,
            subprotocols=['ocpp2.0.1']
    ) as ws:
        global cp
        cp = ChargePoint(charging_point_id, ws)
        await asyncio.gather(cp.start(), cp.send_boot_notification())
