""""
GPS 9600,   8, N, 1     -> 3.3V
GSM     115200, 8, N, 1 -> 5V power supply, but with 3.3V compatible pins
"""

from gsm_linker import DataGSM
from gps_linker import DataGPS
from reset_if_blocked import ResetIfBlocked
from machine import UART

import uasyncio

async def main():
    # Pin 1 <-> Tx, Pin 2 <-> Rx => gsm
    # Pin 6 <-> Tx, Pin 7 <-> Rx => gps

    serial_port_gsm = UART(0, 115200)  # init with given baudrate
    serial_port_gsm.init(115200, bits=8, parity=None, stop=1, timeout=0)  # init with given param
    
    serial_port_gps = UART(1, 9600)  # init with given baudrate
    serial_port_gps.init(9600, bits=8, parity=None, stop=1, timeout=0)  # init with given param
    
    od_data_gps = DataGPS(serial_port_gps)
    ob_data_gsm = DataGSM(serial_port_gsm, True, False)
    ob_data_gsm.init() # initialise gsm module with the wanted settings

    ResetIfBlocked.wdt.feed()
    uasyncio.create_task(od_data_gps.fetch_gps_data()) #by default
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