import socket
import ssl
import os
hostname = 'example.com'

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations('root.pem')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        file = os.open("recv_received.txt", "rb")
        SendData = file.read(1024)

        while SendData:
            ssock.send(SendData)
            SendData = file.read(1024)

        ssock.close()
