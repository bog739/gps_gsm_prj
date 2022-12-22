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

"""
async def blink(led, t_clk):
    while True:
        led.value(1)
        await uasyncio.sleep_ms(5)
        led.value(0)
        await uasyncio.sleep_ms(t_clk)
        
async def create_blinks(led1, led2):
    uasyncio.create_task(blink(led1, 700))
    uasyncio.create_task(blink(led2, 400)) # smaller period
    await uasyncio.sleep_ms(10_000)
"""

if __name__ == '__main__':
    led_ps = Pin(25, Pin.OUT)  # led PS -> RaspberryPiPico
    led_ps.value(0)

    led_gps_ready = Pin(16, Pin.OUT)
    led_sms_send = Pin(17, Pin.OUT)

    #uasyncio.run(create_blinks(led_gps_ready, led_sms_send))

    led_gps_ready.value(0)
    led_sms_send.value(0)

    # Pin 1 <-> Tx, Pin 2 <-> Rx => gsm
    # Pin 6 <-> Tx, Pin 7 <-> Rx => gps
    serial_port_gps = UART(1, 9600)  # init with given baudrate
    serial_port_gps.init(9600, bits=8, parity=None, stop=1, timeout=100)  # init with given param

    serial_port_gsm = UART(0, 115200)  # init with given baudrate
    serial_port_gsm.init(115200, bits=8, parity=None, stop=1, timeout=50)  # init with given param

    ob_data_gps = DataGPS()
    ob_data_gsm = DataGSM(serial_port_gsm, True, False)
    url_data_gps = URL()
    data_stored_gps_msg_dim = 3

    start_byte = bytes(1)
    read_byte = bytes(1)

    while True:
        i = 0
        while i < data_stored_gps_msg_dim:
            while True:
                start_byte = serial_port_gps.read(1)
                if start_byte == b'$':
                    break

            gps_data_format_gga = False
            message_gps = b''

            while True:
                read_byte = serial_port_gps.read(1)
                if read_byte == b'\n' or read_byte == b'\r':
                    break
                if None == read_byte:
                    continue
                message_gps = message_gps + read_byte

            message_gps = "".join(['{:c}'.format(b) for b in message_gps])
            #print(message_gps)
            gps_data_format_gga = message_gps.startswith('GPGGA')
            if gps_data_format_gga:
                ob_data_gps.add_string(message_gps)
                led_gps_ready.on()
                i = i + 1
                #print(message_gps)
                #if i == data_stored_gps_msg_dim - 1:
                #   ob_data_gps.delete_string()
            else:
                led_gps_ready.off()
                continue

        ob_data_gps.parse_message()

        if ob_data_gps.check_for_data() == False:
            ob_data_gps.delete_string()
            continue

        #ob_data_gps.display_()
        
        url_data_gps.url_google_maps = url_data_gps.url_google_maps.replace("#", ob_data_gps.latitude[0])
        url_data_gps.url_google_maps = url_data_gps.url_google_maps.replace("$", ob_data_gps.longitude[0])

        asyncio.run(ob_data_gsm.synchronize_two_tasks(
                                ob_data_gsm.read_continuously_from_gsm_after_sms_sent,
                                ob_data_gsm.analyze_message
        ))
        
        led_sms_send.value(1)
        ob_data_gsm.send_message(url_data_gps.url_google_maps)
        led_sms_send.value(0)

        ob_data_gps.delete_string()