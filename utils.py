import struct


def hti(hex_string: str) -> int:
    """
    Convert a hexadecimal string to an integer.
    """
    return int(hex_string, 16)


def encode(can_id: int, bus_id: int, data: list, disable_checks=False) -> bytes:
    """
    Encode CAN frame data into a CANserver message.

    Args:
        can_id (int): The CAN frame identifier. Must be between 0 and 2047.
        bus_id (int): The bus identifier. Must be between 0 and 268435455.
        data (list): The data payload as a list of integers. Must have a length between 0 and 15.
        disable_checks (bool): Disable argument checks for maximum performance. Default is False.

    Raises ValueError if the arguments are not valid.
    """
    if not disable_checks:
        if not (0 <= can_id <= 2**11 - 1):
            raise ValueError(f"Frame ID out of range: {can_id}")
        if not (0 <= bus_id <= 2**28 - 1):
            raise ValueError(f"Bus ID out of range: {bus_id}")
        if len(data) > 2**4 - 1:
            raise ValueError(f"Data too long: {len(data)}")
        for x in data:
            if isinstance(x, int):
                if not (0 <= x <= 2**8 - 1):
                    raise ValueError(f"Data byte out of range: {x}")
            else:
                raise ValueError(f"Data byte not an integer: {x}")

    data += [0] * (8 - len(data))  # pad data to 8 bytes

    return struct.pack(
        "B" * (8 + len(data)),
        0x00,  # Timestamp byte 1 (not implemented)
        0x00,  # Timestamp byte 2 (not implemented)
        (can_id & 0x07) << 5,  # CAN ID lower bits and flags
        can_id >> 3,  # CAN ID upper bits
        ((bus_id & 0x0F) << 4) | (len(data) & 0x0F),  # Bus ID lower bits and data length
        bus_id >> 4 & 0xFF,  # Bus ID middle bits
        bus_id >> 12 & 0xFF,  # Bus ID middle bits
        bus_id >> 20 & 0xFF,  # Bus ID upper bits
        *data,  # Data payload
    )
