# ELM CAN Bus Monitor

This project is an ELM CAN Bus Monitor that reads CAN bus data from a serial port and sends it over UDP.

## Background

The ELM327 is a popular OBD-II adapter that can be used to read CAN bus data from a vehicle.
This project uses an ELM327 adapter to read CAN bus data from a car and send it over UDP for processing in SavvyCAN using CANserver connection type.

## Files

- `main.py`: Main script to initialize the serial connection, read CAN bus data, and send it over UDP.
- `test_server.py`: Test server to receive and print the UDP messages for debugging.