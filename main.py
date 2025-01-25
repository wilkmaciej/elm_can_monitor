import argparse
import logging
import socket
import sys
import time

import serial

import utils

parser = argparse.ArgumentParser(description="ELM CAN Bus Monitor")
parser.add_argument("port", type=str, help="Serial port to use")
parser.add_argument("baud", type=int, help="Baud rate for the serial connection")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

try:
    logger.info("\033[92mInitializing. Please wait...\033[0m")
    ser = serial.Serial(args.port, args.baud, timeout=10)
    logger.info("\033[92mSerial port opened successfully\033[0m")
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logger.info("\033[92mUDP server started successfully\033[0m")

    def read_until(char: str):
        response = ser.read_until(char.encode())
        logger.debug(f"\033[93mR:\033[0m {repr(response.decode())} Len: {len(response)}")
        return response

    def send(command: str):
        logger.debug(f"\033[94mS:\033[0m {command}")
        ser.write(command.encode() + b"\r\n")
        return read_until(">")

    logger.info("\033[92mConnected to OBD adapter. Initializing...\033[0m")

    ser.write(b"\r\n")  # stop any running commands if there are any
    time.sleep(0.1)
    ser.read_all()  # clear buffer
    send("ATWS")  # warm restart
    send("ATZ")  # cold restart
    send("ATE0")  # turn off echo
    send("ATSP0")  # set protocol to auto
    response = send("0100")  # request current data
    if "UNABLE TO CONNECT" in response.decode():
        logger.error("\033[91mUnable to connect to ECU. Exiting...\033[0m")
        sys.exit(1)
    send("ATDP")  # display protocol
    send("ATCAF0")  # disable can message formatting
    send("AT H1")  # enable can headers

    logger.info("\033[92mInitialized. Monitoring CAN bus...\033[0m")

    ser.write(b"ATMA\r\n")  # monitor all can messages

    while True:
        try:
            response = read_until("\r").decode().strip()
            if len(response) == 0:
                continue
            splitted = response.split(" ")
            can_id = utils.hti(splitted[0])  # first byte is the CAN ID
            bus_id = 0
            data = [utils.hti(x) for x in splitted[1:]]  # the rest are data bytes

            encoded_msg = utils.encode(can_id, bus_id, data, disable_checks=True)
            server.sendto(encoded_msg, ("0.0.0.0", 1338))
            logger.debug(f"Sent CAN message: {hex(can_id)} {[hex(x) for x in data]}")
        except Exception as e:
            logger.error(e)
except KeyboardInterrupt:
    pass

if ser.writable():
    logger.debug("\033[93mCleaning up...\033[0m")
    ser.write(b"\r\n")  # stop any running commands if there are any

logger.info("\033[91mExiting...\033[0m")
