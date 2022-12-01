import time


class DataGSM:
    def __init__(self,
                 serial_port_gsm,
                 on_off_txt_mode,
                 format_txt_mode,
                 ):
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
        self.text_mode_param = 'AT+CSMP'
        self.enable_errors_as_string = 'AT+CMEE=2'
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

        """ Init part """
        """ For txt msg -> text mode, storage and char set """
        if on_off_txt_mode:
            serial_port_gsm.write(self.format_msg + '=1\r')
            self.delay(1000)
            if not format_txt_mode:
                serial_port_gsm.write(self.text_mode_param + '=17,167,0,0\r')
                self.delay(1000)
                # <fo>,<vp>,<pid>,<dcs>
                # <fo> - sms-submit
                # <vp> - integer format for TP-Validity-Period
                # <pid> - protocol identifier in integer format
                # <dcs> - data coding scheme
        else:
            serial_port_gsm.write(self.format_msg + '=0\r')
            self.delay(1000)

        #TODO: implement for storage selection from gsm module


    def read_message(self, idx):

    def send_message(self, msg):

    def delay(self, timeout_msec):
        """ On uPython use internal clock to create delays
            through timers
        """
        timeout_msec = timeout_msec/1000
        time.sleep(timeout_msec)

    def command(self):

    def transmit(self):

    def check_for_err(self):
        """ CPAS: 0 - ready
            1 - unavailable
            2 - unknown
            3 - ringing
            4 - call in progress
        """

