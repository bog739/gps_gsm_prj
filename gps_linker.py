
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

    def delete_string(self):
        del self.message
        self.message = []

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