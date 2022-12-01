
""" Libraries in use """
import serial
import webbrowser
import time

from serial.tools import list_ports
from gsm_linker import DataGSM
from gps_linker import DataGPS
from url_format import URL


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
    ob_data_gsm = DataGSM(serial_port_gsm=serialPortGsm,
                          on_off_txt_mode=True,
                          format_txt_mode=False)
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