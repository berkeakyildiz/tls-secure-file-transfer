import socket
import ssl
import os

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('root.pem', 'server.key')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    sock.bind(('127.0.0.1', 8443))
    sock.listen(5)
    with context.wrap_socket(sock, server_side=True) as ssock:
        conn, addr = ssock.accept()
        file = os.open("recv.txt", "wb")

        while True:
            conn, addr = ssock.accept()

            RecvData = conn.recv(1024)
            while RecvData:
                file.write(RecvData)
                RecvData = conn.recv(1024)

            file.close()

            conn.close()
            print("\nFILE TRANSFERED SUCCESFULLY \n")

            break