import time
import uasyncio
from machine import Pin

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
        #using uasyncio method
        self.serial_writer = uasyncio.StreamWriter(serial_port_gsm, {})
        self.serial_reader = uasyncio.StreamReader(serial_port_gsm)
        
        #infos
        self.number = ''
        self.msg_from = ''
        self.index = 1
        self.flg_read_func = False
        self.flg_send_msg = True #first time
        self.led_sms_send = Pin(17, Pin.OUT)
        self.led_sms_send.value(0)
        
        #useful commands
        self.text_mode_param = 'AT+CSMP'
        self.enable_errors_as_string = 'AT+CMEE=2'
        self.format_msg = 'AT+CMGF' # 0 - PDU 1 - Txt
        self.search_network = 'AT+COPS'  # =0 for auto
        self.mobile_phone_status = 'AT+CPAS'
        self.send_msg_from_storage = 'AT+CMSS'
        self.list_msg_idx_store = 'AT+CMGL'
        self.read_msg = 'AT+CMGR=' # returns message with specific id
        self.read_all_msg = 'AT+CMGL=\"ALL\"'
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
        
    async def init(self):
        """ Init part """
        self.serial_writer.write(self.set_param_manufacturer_default + '\r\n')
        await self.serial_writer.drain()
        await uasyncio.sleep(10)

        self.serial_writer.write(self.disable_echo + '\r\n')
        await self.serial_writer.drain()
        await uasyncio.sleep(5)
        
        self.serial_writer.write(self.enable_network_registration + '\r\n')
        await self.serial_writer.drain()
        await uasyncio.sleep(5)

        """ For txt msg -> text mode, storage and char set """
        if on_off_txt_mode:
            self.serial_writer.write(self.format_msg + '=1\r\n')
            await self.serial_writer.drain()
            await uasyncio.sleep(5)
            
            if not format_txt_mode:
                self.serial_writer.write(self.text_mode_param + '=17,167,0,0\r\n')
                await self.serial_writer.drain()
                await uasyncio.sleep(5)
                # <fo>,<vp>,<pid>,<dcs>
                # <fo> - sms-submit
                # <vp> - integer format for TP-Validity-Period
                # <pid> - protocol identifier in integer format
                # <dcs> - data coding scheme
        else:
            self.serial_writer.write(self.format_msg + '=0\r\n')
            await self.serial_writer.drain()
            await uasyncio.sleep(5)

        #By default store messages in gsm module's internal memory
        self.serial_writer.write(self.stored_msg_in_gsm + '\r\n')
        await self.serial_writer.drain()
        await uasyncio.sleep(5)
        
        self.serial_writer.write(self.character_set_gsm_msg + '\r\n')
        await self.serial_writer.drain()
        await uasyncio.sleep(5)

        #set format CMT: "SM", last_idx
        self.serial_writer.write("{}\r\n".format(self.check_for_new_msgs)) # check for later errors
        await self.serial_writer.drain()
        await uasyncio.sleep(5)
        """ <mode> 0 -> buffer unsolicited
            <mt> 1 -> +CMTI: <mem>, <index> returned
            rest are default values
        """
    #merge below functions to simplify process
    async def send_message(self, msg):
        while True:
            if self.flg_read_func == True:
                self.flg_send_msg = False
                print('here4')
                await self.serial_writer.write(self.send_msg + self.number + '\r\n')
                await self.serial_writer.drain()
                await uasyncio.sleep(5)
                #if self.msg_from == "#":
                self.led_sms_send.on()
                await uasyncio.sleep(5)
                print(msg)
                await self.serial_writer.write(msg)
                await self.serial_writer.drain()
                await uasyncio.sleep(5)
                await self.serial_writer.write(chr(26)) # Ctrl+Z
                await self.serial_writer.drain()
                await uasyncio.sleep(5)
                self.led_sms_send.off()
                await uasyncio.sleep(5)
                self.flg_read_func = False
                self.flg_send_msg = True
            
    async def read_from_gsm(self):
        while True:
            #uasyncio.sleep(3) # delay to get into send_message func
            if self.flg_send_msg == True:
                self.flg_read_func = False
                self.serial_writer.write(self.read_msg + str(self.index) + '\r\n')
                await self.serial_writer.drain()
                await uasyncio.sleep(10)
                
                white_space = await self.serial_reader.readline()
                #await uasyncio.sleep(5)
                print(b'whitespace:' + white_space)
                cmd = await self.serial_reader.readline()
                #await uasyncio.sleep(5)
                print(b'cmd:' + cmd)
                msg = await self.serial_reader.readline()
                #await uasyncio.sleep(5)
                print(b'msg:' + msg)
                #await uasyncio.sleep(5)
                if white_space != b'+CMS ERROR: 321\r\n' and cmd != b'+CMS ERROR: 321\r\n' and msg != b'+CMS ERROR: 321\r\n': # then exists sms with this index
                    cmd = "".join(['{:c}'.format(b) for b in cmd])
                    if cmd[0] == '+' and len(cmd) > 50:
                        self.number = cmd.split(",")[1] #phone number
                    print(self.number)
                    msg = "".join(['{:c}'.format(b) for b in msg])
                    self.msg_from = msg[0] # just one character # or !
                    print(self.msg_from)
                    self.index = self.index + 1
                else:
                    self.index = 1
                    
                self.flg_send_msg = False    
                self.flg_read_func = True