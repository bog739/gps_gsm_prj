import time
import uasyncio


class DataGSM:
    def __init__(self,
                 serial_port_gsm,
                 on_off_txt_mode=True,
                 format_txt_mode=False,
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
        #diff vars
        self.response_gsm_mem_idx = b''
        self.read_byte = bytes(1)
        self.dummy_byte = bytes(1)
        
        #infos
        self.serial_port_gsm = serial_port_gsm
        self.status = ''
        self.number = ''
        self.msg_from = ''
        self.new_messages_arrived = '0'
        
        #useful commands
        self.text_mode_param = 'AT+CSMP'
        self.enable_errors_as_string = 'AT+CMEE=2'
        self.format_msg = 'AT+CMGF' # 0 - PDU 1 - Txt
        self.search_network = 'AT+COPS'  # =0 for auto
        self.mobile_phone_status = 'AT+CPAS'
        self.send_msg_from_storage = 'AT+CMSS'
        self.list_msg_idx_store = 'AT+CMGL'
        self.read_msg = 'AT+CMGR=' # returns message with specific id
        self.send_msg = 'AT+CMGS='
        self.delete_msg = 'AT+CMGD='
        self.write_msg_to_mem = 'AT+CMGW'
        self.new_msg_notifications = 'AT+CNMI'
        self.stored_msg_in_gsm = 'AT+CPMS=\"ME\",\"ME\",\"ME\"'
        self.character_set_gsm_msg = 'AT+CSCS=\"HEX\"'
        self.set_param_manufacturer_default = 'AT&F0'
        self.disable_echo = 'ATE0'
        self.enable_network_registration = 'AT+CREG=1'
        self.check_for_new_msgs = 'AT+CNMI=0,1,0,0,0'
        
        """ Init part """
        self.serial_port_gsm.write(self.set_param_manufacturer_default + '\r\n')
        self.delay_in_seconds(1)

        self.serial_port_gsm.write(self.disable_echo + '\r\n')
        self.delay_in_seconds(1)
        
        self.serial_port_gsm.write(self.enable_network_registration + '\r\n')
        self.delay_in_seconds(1)

        """ For txt msg -> text mode, storage and char set """
        if on_off_txt_mode:
            self.serial_port_gsm.write(self.format_msg + '=1\r\n')
            self.delay_in_seconds(1)
            if not format_txt_mode:
                self.serial_port_gsm.write(self.text_mode_param + '=17,167,0,0\r\n')
                self.delay_in_seconds(1)
                # <fo>,<vp>,<pid>,<dcs>
                # <fo> - sms-submit
                # <vp> - integer format for TP-Validity-Period
                # <pid> - protocol identifier in integer format
                # <dcs> - data coding scheme
        else:
            self.serial_port_gsm.write(self.format_msg + '=0\r\n')
            self.delay(1)

        #By default store messages in gsm module's internal memory
        self.serial_port_gsm.write(self.stored_msg_in_gsm + '\r\n')
        self.delay_in_seconds(1)
        
        self.serial_port_gsm.write(self.character_set_gsm_msg + '\r\n')
        self.delay_in_seconds(1)

    #def check_simcard_inserted():

    def analyze_message(self):
        #print('Enter read function')
        # set format CMT: "SM", last_idx
        self.serial_port_gsm.write(self.check_for_new_msgs + '\r\n') # check for later errors
        self.delay_in_seconds(1)
        """ <mode> 0 -> buffer unsolicited
            <mt> 1 -> +CMTI: <mem>, <index> returned
            rest are default values
        """
        
        # wait until this program synchronizes with gsm module
        # same idea as in main.py for gps module
        #while True:
        #    self.read_byte = self.serial_port_gsm.read(1)
        #    if self.read_byte == None:
        #        break

        #TODO: solve synchronization problem for gsm module
        # python program runs at higher frequencies than gsm dev
        # which causes Tx, respectively Rx to not match precisely
        
        #await uasyncio.sleep_ms(1000) # the other task to store in 
        # response_gsm_mem_idx what we need
        
        if self.response_gsm_mem_idx != b'': 
            self.response_gsm_mem_idx = "".join(['{:c}'.format(b) for b in self.response_gsm_mem_idx])
            self.new_messages_arrived = self.response_gsm_mem_idx[len(self.response_gsm_mem_idx) - 1]
            print('Idx: ' + self.new_messages_arrived)
        else:
            self.new_messages_arrived = '0'

        if self.new_messages_arrived > '0': #as idx
            print('Index: ' + self.new_messages_arrived + '\n')
            self.serial_port_gsm.write(self.read_msg + self.new_messages_arrived + '\r\n')
            #self.delay_in_seconds(5)
            take_phone_nr_second_comma = 2
            while True: # blocked here
                self.read_byte = self.serial_port_gsm.read(1)
                #if dummy_byte == None:
                #    break
                print(dummy_byte)
                if self.read_byte == ',':
                    take_phone_nr_second_comma = take_phone_nr_second_comma - 1
                if take_phone_nr_second_comma == 0:
                    dummy_byte = self.serial_port_gsm.read(1)
                    self.read_byte = self.serial_port_gsm.read(1)
                    if self.read_byte == '+':
                        self.number = self.read_byte + self.serial_port_gsm.read(11)
                if self.read_byte == '\r':
                    while True:
                        self.read_byte = self.serial_port_gsm.read(1)
                        self.msg_from = self.msg_from + self.read_byte
                        if self.read_byte == '\r':
                            break   # inner loop
                    break   # outer loop
            
            self.number = "".join(['{:c}'.format(b) for b in self.number])
            print('Phone number: ' + self.number + '\n')
            print('Msg: ' + self.msg_from)
            self.serial_port_gsm.write(self.delete_msg + self.new_messages_arrived)
            self.delay_in_seconds(1)

    def send_message(self, msg):
        print('Msg to be sent: ' + msg + '\n')
        print('Phone nr: ' + self.number)
        self.serial_port_gsm.write(self.send_msg + self.number + '\r\n')
        self.delay_in_seconds(1)
        self.serial_port_gsm.write(msg)
        print('Msg send!')

    def delay_in_seconds(self, timeout_sec):
        """ On uPython use internal clock to create delays
            through timers
        """
        timeout_sec = timeout_sec*1000000
        time.sleep_us(timeout_sec) # sleep_us for more price delays

    def synchronize_two_tasks(self, task_no_1, task_no_2):
        uasyncio.create_task(task_no_1)
        uasyncio.create_task(task_no_2)
        await uasyncio.sleep_ms(100)
        print('Done')

    def read_continuously_from_gsm_after_sms_sent(self):
        wait_for_two_cr = int(1)
        if self.serial_port_gsm.any() != 0:
            while True:
                dummy_byte = self.serial_port_gsm.read(1)
                if dummy_byte == b'\r':
                    dummy_byte = self.serial_port_gsm.read(1) # for '\n'
                    while True:
                        self.read_byte = self.serial_port_gsm.read(1)
                        if self.read_byte == b'\r': # look for carriage return after it was read from gsm \r\n
                            if wait_for_two_cr == 0:
                                break
                            else:
                                wait_for_two_cr = wait_for_two_cr - 1
                        else:
                            response_gsm_mem_idx = response_gsm_mem_idx + read_byte
                    break
    
    #def command(self):

    #def transmit(self):

    #def check_for_err(self):
        """ CPAS: 0 - ready
            1 - unavailable
            2 - unknown
            3 - ringing
            4 - call in progress
        """

