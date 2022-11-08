import time
import serial
from serial.tools import list_ports


class DataGPS:
    fTestDevice = False

    def __init__(self, message):
        self.message = message
        self.dict_message_gps = dict()

    def parse_message(self):
        """
        Function to parse the string of bytes coming from a GPS module,
        it starts with '$' sign and ends with carriage return. Different
        info is available in this collection: latitude, longitude, utc time,
        nr of satellites
        :return: Dictionary of chunks of data from the parsed string
        """
        # TODO: segment into lat, long, utc keys ...


def swap(x, y):
    x, y = y, x
    return x, y


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
    endByte = bytes(1)
    readByte = bytes(1)

    data_line_extracted = 10
    insertWhiteSpacePos = 5
    while True:
        try:
            for i in range(data_line_extracted):
                startByte = serialPortGps.read(1)
                x = 0
                gpsDataFormatGGA = False
                messageGPS = ""

                while True:
                    readByte = serialPortGps.read(1)
                    if readByte == b'\n':
                        break

                    if x == insertWhiteSpacePos:
                        readByte = b' '
                        x = x + 1
                    else:
                        x = x + 1

                    messageGPS = messageGPS + str(readByte.decode('ascii'))

                gpsDataFormatGGA = messageGPS.startswith('GPGGA')
                if gpsDataFormatGGA:
                    print(messageGPS)

                time.sleep(1)
            break
        except KeyboardInterrupt:
            break

    serialPortGps.close()