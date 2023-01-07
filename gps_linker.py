
from machine import Pin, UART
from url_format import URL

import uasyncio

class DataGPS:
    def __init__(self, serial_port_gps, message=None):
        if message is None:
            message = []
        self.white_space = ""
        self.message = message
        self.gps_format_data = []

        self.latitude_pos = 2
        self.longitude_pos = 4
        self.utc_time_pos = 1

        self.latitude_raw = ""
        self.longitude_raw = ""
        self.utc_time_raw = ""

        self.latitude = []   # first to be inserted in maps
        self.longitude = []  # second to be inserted in maps
        self.utc_time = []
        
        self.flg_data_is_ready = False
        
        self.serial_reader_gps = uasyncio.StreamReader(serial_port_gps)

    def add_string(self, item):
        self.message.append(item)

    def delete_string(self):
        del self.message
        del self.latitude
        del self.longitude
        del self.utc_time
        del self.gps_format_data
        self.message = []
        self.latitude = []
        self.longitude = []
        self.utc_time = []
        self.gps_format_data = []

    def check_for_data(self):
        return self.flg_data_is_ready
        
    def parse_message(self):
        """
        Function to parse the string of bytes coming from a GPS module,
        it starts with '$' sign and ends with <CR><LF>. Different
        info is available in this collection: latitude, longitude, utc time,
        nr of satellites
        """
        for x in range(0, len(self.message)):
            split_msg = self.message[x].split(",")  # take first one just to practice
            del split_msg[13]  # 13th element is a whitespace, from datasheet
            if self.white_space in split_msg:
                self.flg_data_is_ready = False
                break
            else:
                self.flg_data_is_ready = True
            
            self.latitude_raw = split_msg[self.latitude_pos]
            self.longitude_raw = split_msg[self.longitude_pos]
            self.utc_time_raw = split_msg[self.utc_time_pos]

            north_minutes_seconds_part = self.latitude_raw[2:]
            """ ValueError: could not convert string to float.
                Usually, this happens if the string object has
                an invalid floating value with spaces or comma
            """
            north_value_minutes_seconds_part = float(north_minutes_seconds_part) / float(60.0)
            self.latitude.append(str(float(self.latitude_raw[0:2]) + north_value_minutes_seconds_part))

            east_minutes_seconds_part = self.longitude_raw[3:]
            east_minutes_seconds_part = float(east_minutes_seconds_part) / float(60.0)
            if self.longitude_raw[0] == '0':
                self.longitude.append(str(float(self.longitude_raw[1:3]) + east_minutes_seconds_part))
            else:
                self.longitude.append(str(float(self.longitude_raw[0:3]) + east_minutes_seconds_part))

            seconds_utc_part = self.utc_time_raw[4:]
            seconds_utc_part = int(float(seconds_utc_part) % 60)
            self.utc_time.append(str(int(self.utc_time_raw[0:2]) + 2) + ':'
                                 + str(int(self.utc_time_raw[2:4]))
                                 + ':' + str(seconds_utc_part))

            self.longitude[x] = self.longitude[x][0:9]
            self.latitude[x] = self.latitude[x][0:9]
            self.gps_format_data.append("UTC time: " + self.utc_time[x] + ", Longitude: "
                                        + self.longitude[x] + ", Latitude: " + self.latitude[x])

    def display_(self):
        for x in range(0, len(self.message)):
            print(self.gps_format_data[x])
            
    async def fetch_gps_data(self):
        led_ps = Pin(25, Pin.OUT)  # led PS -> RaspberryPiPico
        led_ps.value(0)

        led_gps_ready = Pin(16, Pin.OUT)
        led_gps_ready.value(0)
        
        data_stored_gps_msg_dim = 3

        start_byte = bytes(1)
        read_byte = bytes(1)

        while True:
            i = 0
            while i < data_stored_gps_msg_dim:
                gps_data_format_gga = False
                message_gps = b''
                
                message_gps = await self.serial_reader_gps.readline()
                message_gps = message_gps[1:(len(message_gps) - 1)] # get rid of $ sign and '\r'
                message_gps = "".join(['{:c}'.format(b) for b in message_gps])
                
                gps_data_format_gga = message_gps.startswith('GPGGA')
                if gps_data_format_gga:
                    self.add_string(message_gps)
                    i = i + 1
                else:
                    continue
                    
            self.parse_message()
            if self.check_for_data():
                led_gps_ready.on()
                URL.url_google_maps_satellite = URL.url_google_maps_satellite.replace("#", self.latitude[0]) #static variable to be accessed between files
                URL.url_google_maps_satellite = URL.url_google_maps_satellite.replace("$", self.longitude[0])
                URL.url_google_maps_normal = URL.url_google_maps_normal.replace("#", self.latitude[0]) #static variable to be accessed between files
                URL.url_google_maps_normal = URL.url_google_maps_normal.replace("$", self.longitude[0])
                URL.flg_url_state = True
                await uasyncio.sleep(1)
                self.delete_string()
                led_gps_ready.off()
            else:
                led_gps_ready.on()
                URL.flg_url_state = False