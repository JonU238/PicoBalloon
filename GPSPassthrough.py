import board
import busio
import supervisor

# UART connected to GPS (adjust pins and baudrate as needed)
gps_uart = busio.UART(board.TX, board.RX, baudrate=38400, timeout=0.1)

# USB serial console (your computer side)
usb_serial = supervisor.runtime.serial_bytes_available

import sys

def read_usb():
    data = b""
    while supervisor.runtime.serial_bytes_available:
        data += sys.stdin.buffer.read(1)
    return data

def write_usb(data):
    sys.stdout.buffer.write(data)
    #sys.stdout.flush()

while True:
    # Forward from GPS → USB
    gps_data = gps_uart.read(64)  # read up to 64 bytes
    if gps_data:
        write_usb(gps_data)

    # Forward from USB → GPS
    usb_data = read_usb()
    if usb_data:
        gps_uart.write(usb_data)