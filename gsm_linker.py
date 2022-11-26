
class DataGSM:
    def __init__(self):
        """ Predefined commands for gsm module """
        """ AT+<x>=? -> test
            AT+<x>?  -> read
            AT+<x>=<...> -> write
            AT+<x>   -> execute
            OK -> command is read an acknowledged
            SIM card on gsm module is ready to use w/out
            any pin required
        """
        self.status = ''
        self.number = ''
        self.format_msg = 'AT+CMGF' # 0 - PDU 1 - Txt
        self.search_network = 'AT+COPS'  # =0 for auto
        self.mobile_phone_status = 'AT+CPAS'
        self.send_msg_from_storage = 'AT+CMSS'
        self.delete_msg = 'AT+CMGD'
        self.list_msg_idx_store = 'AT+CMGL'
        self.read_msg = 'AT+CMGR'
        self.send_msg = 'AT+CMGS'
        self.write_msg_to_mem = 'AT+CMGW'
        self.new_msg_notifications = 'AT+CNMI'

    def read_message(self, idx):

    def send_message(self, msg):

    def delay(self):

    def command(self):

    def transmit(self):

    def check_for_err(self):
        """ CPAS: 0 - ready
            1 - unavailable
            2 - unknown
            3 - ringing
            4 - call in progress
        """

