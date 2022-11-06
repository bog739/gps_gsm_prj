from serial.tools import list_ports
import serial


class DataGPS:
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


if __name__ == "__main__":
    comports_ = [[]]
    comports_ = list(list_ports.comports())

    gps_module_port = str()
    gsm_module_port = str()
    # for x in comports_:
    #    if "RS-232" in x:
    #        gps_module_port = x[0]

    serialPort = serial.Serial(port=gps_module_port, baudrate=9600,
                               bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)

    # TODO: For gsm module it is not mandatory to write smth to it,
    #       from it we can use only Rx pin and to parse the existing
    #       string of bytes.
    serialPort.open()

    messageGPS = ""

    startByte = bytes(1)
    endByte = bytes(1)
    readByte = bytes(1)

    data_line_extracted = 4
    while True:
        try:
            for i in range(data_line_extracted):
                startByte = serialPort.read(1)
                while True:
                    readByte = serialPort.read(1)
                    if readByte == b'/r':
                        break
                    messageGPS = messageGPS + chr(ascii(readByte))
                print(messageGPS)
        except KeyboardInterrupt:
            break

    serialPort.close()