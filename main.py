""""
GPS 9600,   8, N, 1     -> 3.3V
GSM     115200, 8, N, 1 -> 5V
"""

from gsm_linker import DataGSM
from url_format import URL

from machine import Pin, UART
from gps_linker import DataGPS

import time
import binascii

if __name__ == '__main__':
    led_ps = Pin(25, Pin.OUT)  # led PS -> RaspberryPiPico
    led_ps.value(0)

    led_gps_ready = Pin(16, Pin.OUT)
    led_sms_send = Pin(17, Pin.OUT)

    led_gps_ready.value(0)
    led_sms_send(0)

    # Pin 1 <-> Tx, Pin 2 <-> Rx => gsm
    # Pin 6 <-> Tx, Pin 7 <-> Rx => gps
    serialPortGps = UART(1, 9600)  # init with given baudrate
    serialPortGps.init(9600, bits=8, parity=None, stop=1)  # init with given param

    serialPortGsm = UART(0, 115200)  # init with given baudrate
    serialPortGsm.init(115200, bits=8, parity=None, stop=1)  # init with given param

    ob_data_gps = DataGPS()
    data_stored_gps_msg_dim = 3

    startByte = bytes(1)
    readByte = bytes(1)

    while True:
        i = 0
        while i < data_stored_gps_msg_dim:
            while True:
                startByte = serialPortGps.read(1)
                if startByte == b'$':
                    break

            gpsDataFormatGGA = False
            messageGPS = b''

            while True:
                readByte = serialPortGps.read(1)
                if readByte == b'\n' or readByte == b'\r':
                    break
                if None == readByte:
                    continue
                messageGPS = messageGPS + readByte

            messageGPS = "".join(['{:c}'.format(b) for b in messageGPS])
            print(messageGPS)
            gpsDataFormatGGA = messageGPS.startswith('GPGGA')
            if gpsDataFormatGGA:
                ob_data_gps.add_string(messageGPS)
                led_gps_ready.on()
                i = i + 1
            else:
                continue
                led_gps_ready.off()

        ob_data_gps.parse_message()
        ob_data_gps.display_()

        url_data_gps = URL()
        url_data_gps.format_gm_acc = url_data_gps.format_gm_acc.replace("#", ob_data_gps.latitude[0])
        url_data_gps.format_gm_acc = url_data_gps.format_gm_acc.replace("$", ob_data_gps.longitude[0])

        ob_data_gps.delete_string()