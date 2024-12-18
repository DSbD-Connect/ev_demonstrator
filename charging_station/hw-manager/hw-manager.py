from flask import Flask, send_from_directory, request, jsonify, make_response
from flask_cors import CORS
import subprocess
import base64
import os
app = Flask(__name__)
CORS(app)


@app.route('/hw/verify', methods=["POST"])
def verify():
    data = request.json['vehicle_id']
    print(data)
    command_str = "python3 hw-io.py "+base64.urlsafe_b64decode(data).decode('utf-8')
    print(command_str)
    output = subprocess.run(command_str,
                            shell=True,
                            text=True)
    print(output)
    if output.returncode == 0:
        return jsonify(True)
    else:
        return jsonify(False)


@app.route('/hw/current', methods=["GET"])
def get_current():
    try:
        # Call the compiled C program
        result = subprocess.run(['./ev_sensor'],
                                capture_output=True,
                                text=True,
                                check=True)

        # Return the output from the C program
        return jsonify(result.stdout.strip())

    except subprocess.CalledProcessError as e:
        print("Error occurred while calling the C program:")
        print(e.stderr)
        return jsonify(str(-1))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ["HARDWARE_MANAGER_API_PORT"])
