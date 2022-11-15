import serial
from serial.tools import list_ports
import webbrowser


class URL:
    def __init__(self):
        self.url_google_maps = 'https://www.google.com/maps/@#,$,14z'
        self.format_google_maps = 'https://www.google.com/maps/@46.7566592,23.6191744,14z'
        self.format_gm_acc = "https://www.google.com/maps/place/46%C2%B045'17.3%22N+23%C2%B034'47.9%22E/@#,$," \
                             "17z/data=!4m4!3m3!8m2!3d#!4d$"


class DataGPS:
    def __init__(self, message=None):
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

    def add_string(self, item):
        self.message.append(item)

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
                break

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


def swap(prev_val_x, prev_val_y):
    a, b = prev_val_y, prev_val_x
    return a, b


if __name__ == "__main__":
    comports_ = [list(list_ports.comports())]

    gps_module_port = comports_[0][0].device
    gsm_module_port = comports_[0][1].device

    serialPort = serial.Serial(port=gps_module_port, baudrate=9600,
                               bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
    serialPort.close()

    # For gsm module it is not mandatory to write smth to it,
    # from it we can use only Rx pin and to parse the existing
    # string of bytes.

    serialPort.open()
    dummyByte = serialPort.read(1)
    if dummyByte != b'$':    # use != if gps var is used above
        serialPort.close()
        gps_module_port, gsm_module_port = swap(gps_module_port, gsm_module_port)

    serialPort.close()
    serialPortGsm = serial.Serial(port=gsm_module_port, baudrate=115200, bytesize=8,
                                  timeout=1, stopbits=serial.STOPBITS_ONE)
    serialPortGps = serial.Serial(port=gps_module_port, baudrate=9600, bytesize=8,
                                  timeout=1, stopbits=serial.STOPBITS_ONE)

    messageGPS = ""
    commandATGsm = ""

    startByte = bytes(1)
    readByte = bytes(1)

    data_line_extracted = 10
    ob_data_gps = DataGPS()
    try:
        for i in range(data_line_extracted):
            startByte = serialPortGps.read(1)
            gpsDataFormatGGA = False
            messageGPS = ""

            while True:
                readByte = serialPortGps.read(1)
                if readByte == b'\n' or readByte == b'\r':
                    break
                messageGPS = messageGPS + str(readByte.decode('ascii'))

            gpsDataFormatGGA = messageGPS.startswith('GPGGA')
            if gpsDataFormatGGA:
                ob_data_gps.add_string(messageGPS)

        ob_data_gps.parse_message()
        ob_data_gps.display_()
    except KeyboardInterrupt:
        pass
    serialPortGps.close()

    url_data_gps = URL()
    url_data_gps.format_gm_acc = url_data_gps.format_gm_acc.replace("#", ob_data_gps.latitude[0])
    url_data_gps.format_gm_acc = url_data_gps.format_gm_acc.replace("$", ob_data_gps.longitude[0])
    webbrowser.open_new_tab(url_data_gps.format_gm_acc)
    """ for using only open()
        new=0 -> url open in the same browser window 
        new=1 -> a new browser window is opened
        new=2 -> a new browser tab is opened
    """