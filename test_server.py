import contextlib
import socket
import time

import utils

HOST = "127.0.0.1"
PORT = 1338

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"Server started on {HOST}:{PORT}")

try:
    while True:
        server.settimeout(0.01)
        with contextlib.suppress(socket.timeout):
            data, addr = server.recvfrom(1024)
            print(f"Received data from {':'.join(map(str, addr))}: {data}")
        server.settimeout(10)

        can_id = 0x7FF
        bus_id = 0
        data = [1, 2, 3, 4, 5, 6, 7, 8]

        encoded_msg = utils.encode(can_id, bus_id, data)
        server.sendto(encoded_msg, (HOST, PORT))
        hex_string = encoded_msg.hex()
        print(f"Sent message: {' '.join(hex_string[i:i+2] for i in range(0, len(hex_string), 2))}")
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
