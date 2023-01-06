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
import uasyncio

async def fetch_gps_data():
    led_ps = Pin(25, Pin.OUT)  # led PS -> RaspberryPiPico
    led_ps.value(0)

    led_gps_ready = Pin(16, Pin.OUT)
    led_gps_ready.value(0)

    # Pin 1 <-> Tx, Pin 2 <-> Rx => gsm
    # Pin 6 <-> Tx, Pin 7 <-> Rx => gps
    serial_port_gps = UART(1, 9600)  # init with given baudrate
    serial_port_gps.init(9600, bits=8, parity=None, stop=1, timeout=0)  # init with given param
    serial_reader_gps = uasyncio.StreamReader(serial_port_gps)
    ob_data_gps = DataGPS()
    
    data_stored_gps_msg_dim = 3

    start_byte = bytes(1)
    read_byte = bytes(1)

    while True:
        i = 0
        while i < data_stored_gps_msg_dim:
            gps_data_format_gga = False
            message_gps = b''
            
            message_gps = await serial_reader_gps.readline()
            message_gps = message_gps[1:(len(message_gps) - 1)] # get rid of $ sign and '\r'
            message_gps = "".join(['{:c}'.format(b) for b in message_gps])
            
            gps_data_format_gga = message_gps.startswith('GPGGA')
            if gps_data_format_gga:
                ob_data_gps.add_string(message_gps)
                i = i + 1
            else:
                continue
                
        ob_data_gps.parse_message()
        if ob_data_gps.check_for_data():
            led_gps_ready.on()
            URL.url_google_maps = URL.url_google_maps.replace("#", ob_data_gps.latitude[0]) #static variable to be accessed between files
            URL.url_google_maps = URL.url_google_maps.replace("$", ob_data_gps.longitude[0])
            await uasyncio.sleep(10)
            ob_data_gps.delete_string()
            led_gps_ready.off()

async def main():
    serial_port_gsm = UART(0, 115200)  # init with given baudrate
    serial_port_gsm.init(115200, bits=8, parity=None, stop=1, timeout=0)  # init with given param

    ob_data_gsm = DataGSM(serial_port_gsm, True, False)
    ob_data_gsm.init() # initialise gsm module with the wanted settings

    uasyncio.create_task(fetch_gps_data()) #by default
    uasyncio.create_task(ob_data_gsm.read_from_gsm_send_sms()) #make this variable global
    while True:
        await uasyncio.sleep(1)

if __name__ == '__main__':
    try:
        uasyncio.run(main()) # only once run the methods
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        uasyncio.new_event_loop()