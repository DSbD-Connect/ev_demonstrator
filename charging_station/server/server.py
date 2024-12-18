from flask import Flask, send_from_directory, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

import asyncio
import os
from ocpp.v201.enums import RegistrationStatusType
import logging
import websockets

from ocpp.v201 import call
from ocpp.v201 import ChargePoint as cp

from threading import Thread

import ocpp_messaging

load_dotenv()

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
loop = asyncio.new_event_loop()

@app.route('/')
def hello():
    return send_from_directory('client/dist', 'index.html')


@app.route('/api/status')
def get_status():
    status = {
        "station_status": ocpp_messaging.cp.status, 
        "session_status": ocpp_messaging.cp.charging_session.get_session_status() if ocpp_messaging.cp.charging_session else None

    }
    return jsonify(status)


@app.route('/api/session_status')
def get_session_status():
    return jsonify(ocpp_messaging.cp.charging_session.get_session_status())


@app.route('/api/reset')
def reset():
    future = asyncio.run_coroutine_threadsafe(
        ocpp_messaging.cp.reset_charger(),
        loop
    )
    response = future.result()
    return jsonify(response)


@app.route('/api/qr')
def get_qr():
    central_management_server = os.environ["CENTRAL_MANAGEMENT_SERVER_PUBLIC_HOST"]
    charging_point_id = os.environ["CHARGING_STATION_ID"]
    qr_string = central_management_server + \
        "/api/start?charging_point_id=" + \
        charging_point_id

    return qr_string

@app.route('/api/stop')
def stop_charging():
    future = asyncio.run_coroutine_threadsafe(
        ocpp_messaging.cp.stop_transaction(),
        loop
    )
    response = future.result()
    return jsonify(response)


def run_flask():
    app.run(host='0.0.0.0', port=os.environ["CHARGING_STATION_SERVER_PORT"])


def run_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


async def main():
    # Replace this with your actual async logic
    await ocpp_messaging.main()

if __name__ == '__main__':

    asyncio_thread = Thread(target=run_asyncio_loop, args=(loop,))
    asyncio_thread.start()
    asyncio.run_coroutine_threadsafe(ocpp_messaging.main(), loop)

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    asyncio_thread.join()
    flask_thread.join()
