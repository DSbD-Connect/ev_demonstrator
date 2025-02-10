import asyncio
import logging
import websockets
from datetime import datetime

from flask import Flask, send_from_directory, request, jsonify, make_response
from dotenv import load_dotenv
from flask_cors import CORS

from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call_result
from ocpp.v201 import call
from ocpp.v201.enums import RegistrationStatusType
from threading import Thread
from db_manager import db_manager

import auth
import ocpp_messaging
import internals
import os
import payment


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

cm = ocpp_messaging.Central_Management()
loop = asyncio.new_event_loop()

received_alerts = set()

@app.route('/api/start')
def start_transaction():
    charging_point_id = request.args["charging_point_id"]
    username = request.args["username"]
    request_args = request.args
    logging.info(request_args)
    logging.info("Starting transaction")
    verification = internals.verify_start_request(cm,
                                                  loop,
                                                  charging_point_id,
                                                  request_args)

    logging.info("Sending start remote charging request,", verification)
    if verification:
        future = asyncio.run_coroutine_threadsafe(
            cm.charging_points[charging_point_id].send_remote_start(username),
            loop
        )
        response = future.result()
        return jsonify(response)
    else:
        return jsonify("")


@app.route('/api/stop/<charging_point_id>')
def stop_transaction(charging_point_id):
    future = asyncio.run_coroutine_threadsafe(
        cm.charging_points[charging_point_id].send_remote_stop(),
        loop
    )
    response = future.result()
    return jsonify(response)


@app.route('/api/status/<charging_point_id>')
def status(charging_point_id):

    session_status = {
        "start_time": "NaN",
        "stop_time": "NaN",
        "total_energy": "NaN",
        "total_price": "NaN"
    }

    if cm.charging_points[charging_point_id].charging_session:
        session_status = cm.charging_points[charging_point_id].charging_session.to_dict()

    data = {
        "cp_status": cm.charging_points[charging_point_id].status,
        "session_status": session_status
    }
    return jsonify(data)


@app.route('/api/session_info/<charging_point_id>')
def session_info(charging_point_id):
    return jsonify(cm.charging_points[charging_point_id].charging_session.to_dict())


@app.route('/api/login', methods=['POST'])
def login():
    '''
    Check the credentials and return the TOKEN to the user
    '''
    request_json = request.get_json()
    status = auth.login(request_json["username"],
                        request_json["password"],
                        request_json["cheri_on"])
    make_response()
    response_data = {
        "status":  "Success" if status == "1" else "Fail",
        "TOKEN": "abcdefadsadsadsadsadsad"
    }
    response_status = 200 if status == "1" else 401
    return make_response(response_data,  response_status)


@app.route('/api/sessions', methods=['GET'])
def sessions():
    sessions_list = db_manager().list_sessions()
    logging.info(sessions_list)
    return jsonify(sessions_list)


@app.route('/api/payment', methods=['POST'])
def handle_payment():
    '''
    Check the credentials and return the TOKEN to the user
    '''
    request_json = request.get_json()
    result = payment.process(
                    request_json["card-number"],
                    request_json["expire-date"],
                    request_json["cvv"],
                    request_json["amount"],
                    request_json["cheri_on"]  # Indicates cheri compartments
                    )

    return jsonify(result)

@app.route('/api/card_provider', methods=['POST'])
def card_provider():
    '''
    Check the credentials and return the TOKEN to the user
    '''
    request_json = request.get_json()
    logging.info(request_json)
    result = payment.fetch_card_provider(
                    request_json["credit_card_number"],
                    request_json["expiry_date"],
                    request_json["cvv"],
                    request_json["amount"],
                    request_json["cheri_on"]  # Indicates cheri compartments
                    )

    logging.info(result)
    return str(result)


@app.route('/api/qr')
def get_qr():
    return True


@app.route('/api/alert', methods=['POST'])
def alert():
    if os.environ["MONITORING"] == "on":
        request_json = request.get_json()
        logging.info(request_json)
        if (request_json["alert_id"] not in received_alerts):
            received_alerts.add(request_json["alert_id"])
            # processing the alert
            if 'initial_scan' not in request_json['event']['action']:
                logging.info("Suspicious activity on: %s", str(request_json["charging_point_id"]))
                future = asyncio.run_coroutine_threadsafe(
                     cm.charging_points[request_json["charging_point_id"]].disable_station(),
                     loop
                )
                response = future.result()
                return jsonify(response)
        else:
            logging.info("Received duplicate alert: %s", str(request_json["alert_id"]))
    return jsonify(True)


def run_flask():
    app.run(host='0.0.0.0', port=os.environ["CENTRAL_MANAGEMENT_SERVER_API_PORT"])


def run_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    asyncio_thread = Thread(target=run_asyncio_loop, args=(loop,))
    asyncio_thread.start()
    asyncio.run_coroutine_threadsafe(cm.main(), loop)

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    asyncio_thread.join()
    flask_thread.join()
