
from url_format import URL
from machine import Pin
from reset_if_blocked import ResetIfBlocked

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
        #using uasyncio method
        self.serial_writer = uasyncio.StreamWriter(serial_port_gsm, {})
        self.serial_reader = uasyncio.StreamReader(serial_port_gsm)
        
        #infos
        self.number = str('...')
        self.msg_from = str('...')
        self.index = ''
        self.max_msg_in_gsm_mem = 10
        self.led_sms_send = Pin(17, Pin.OUT)
        self.led_sms_send.value(0)
        self.take_first_msg = False
        self.no_messages = False
        
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
        self.stop_gsm_from_responding_1 = 'AT+CNMI=0,0,0,0,0'
        self.stop_gsm_from_responding_2 = 'AT+CMER=3,0,0,0'
        self.at_cmd = 'AT'
        
    async def init(self):
        """ Init part """
        await uasyncio.sleep(1) # for messages w.r power supply when gsm module is hooked up on a PCB
        ResetIfBlocked.wdt.feed()
        
        self.serial_writer.write(self.at_cmd + '\r\n')
        await self.serial_writer.drain()
        ResetIfBlocked.wdt.feed()
        await uasyncio.sleep(1)
        
        self.serial_writer.write(self.set_param_manufacturer_default + '\r\n')
        await self.serial_writer.drain()
        ResetIfBlocked.wdt.feed()
        await uasyncio.sleep(1)

        self.serial_writer.write(self.disable_echo + '\r\n')
        await self.serial_writer.drain()
        ResetIfBlocked.wdt.feed()
        await uasyncio.sleep(1)
        
        self.serial_writer.write(self.enable_network_registration + '\r\n')
        await self.serial_writer.drain()
        ResetIfBlocked.wdt.feed()
        await uasyncio.sleep(1)

        """ For txt msg -> text mode, storage and char set """
        if on_off_txt_mode:
            self.serial_writer.write(self.format_msg + '=1\r\n')
            await self.serial_writer.drain()
            ResetIfBlocked.wdt.feed()
            await uasyncio.sleep(1)
            
            if not format_txt_mode:
                self.serial_writer.write(self.text_mode_param + '=17,167,0,0\r\n')
                await self.serial_writer.drain()
                ResetIfBlocked.wdt.feed()
                await uasyncio.sleep(1)
                # <fo>,<vp>,<pid>,<dcs>
                # <fo> - sms-submit
                # <vp> - integer format for TP-Validity-Period
                # <pid> - protocol identifier in integer format
                # <dcs> - data coding scheme
        else:
            self.serial_writer.write(self.format_msg + '=0\r\n')
            await self.serial_writer.drain()
            ResetIfBlocked.wdt.feed()
            await uasyncio.sleep(1)

        #By default store messages in gsm module's internal memory
        self.serial_writer.write(self.stored_msg_in_gsm + '\r\n')
        await self.serial_writer.drain()
        ResetIfBlocked.wdt.feed()
        await uasyncio.sleep(1)
        
        self.serial_writer.write(self.character_set_gsm_msg + '\r\n')
        await self.serial_writer.drain()
        ResetIfBlocked.wdt.feed()
        await uasyncio.sleep(1)

        #set format CMT: "SM", last_idx
        #self.serial_writer.write("{}\r\n".format(self.check_for_new_msgs)) # check for later errors
        #await self.serial_writer.drain()
        #await uasyncio.sleep(1)
        """ <mode> 0 -> buffer unsolicited
            <mt> 1 -> +CMTI: <mem>, <index> returned
            rest are default values
        """
        self.serial_writer.write("{}\r\n".format(self.stop_gsm_from_responding_1))
        await self.serial_writer.drain()
        ResetIfBlocked.wdt.feed()
        await uasyncio.sleep(1)
        
        self.serial_writer.write("{}\r\n".format(self.stop_gsm_from_responding_2))
        await self.serial_writer.drain()
        ResetIfBlocked.wdt.feed()
        await uasyncio.sleep(1)
        
    async def read_from_gsm_send_sms(self):
        while True:
            ResetIfBlocked.wdt.feed()
            
            self.serial_writer.write(self.read_all_msg + '\r\n')
            await self.serial_writer.drain()
            ResetIfBlocked.wdt.feed()
            await uasyncio.sleep(2)
            
            white_space_byte = b''
            temp_bytes = b''
            while True:
                ResetIfBlocked.wdt.feed()
                white_space_byte = await self.serial_reader.readline()
                ResetIfBlocked.wdt.feed()
                #print(white_space_byte)
                if temp_bytes == b'OK\r\n':
                    ResetIfBlocked.wdt.feed()
                    break

                if len(white_space_byte) > 0:
                    ResetIfBlocked.wdt.feed()
                    temp_bytes = await self.serial_reader.readline()
                    ResetIfBlocked.wdt.feed()
                    #print(temp_bytes)
                    if temp_bytes == b'OK\r\n':
                        ResetIfBlocked.wdt.feed()
                        self.no_messages = True
                        break
        
                    if temp_bytes == b'\r\n':
                        ResetIfBlocked.wdt.feed()
                        white_space_byte = await self.serial_reader.readline() # comes an OK if there are messages
                        ResetIfBlocked.wdt.feed()
                        break

                    temp_str = "".join(['{:c}'.format(b) for b in temp_bytes])
                    if self.take_first_msg == False:
                        ResetIfBlocked.wdt.feed()
                        self.index = temp_str.split(",")[0].split(" ")[-1] # take index
                        self.take_first_msg = True
                else:
                    ResetIfBlocked.wdt.feed()
                    self.no_messages = True
                    break

            if self.no_messages == True:
                self.no_messages = False
                #print('No messages!')
                continue

            ResetIfBlocked.wdt.feed()
            if self.index != '':
                #print("Index extracted: " + self.index)
                self.serial_writer.write(self.read_msg + str(self.index) + '\r\n')
                await uasyncio.sleep(1)
                await self.serial_writer.drain()
                ResetIfBlocked.wdt.feed()

            white_space = await self.serial_reader.readline()
            await uasyncio.sleep(1)
            ResetIfBlocked.wdt.feed()
            #print(b'whitespace1:' + white_space)
            
            cmd = await self.serial_reader.readline()
            await uasyncio.sleep(1)
            ResetIfBlocked.wdt.feed()
            #print(b'cmd:' + cmd)
            if cmd == b'+CMS ERROR: 305\r\n':
                continue
            
            msg = await self.serial_reader.readline()
            await uasyncio.sleep(1)
            ResetIfBlocked.wdt.feed()
            #print(b'msg:' + msg)
            
            white_space = await self.serial_reader.readline()
            await uasyncio.sleep(1)
            ResetIfBlocked.wdt.feed()
            #print(b'whitespace2:' + white_space)
            
            ok_resp = await self.serial_reader.readline()
            await uasyncio.sleep(1)
            ResetIfBlocked.wdt.feed()
            #print(b'->' + ok_resp)
            
            if white_space != b'+CMS ERROR: 321\r\n' and cmd != b'+CMS ERROR: 321\r\n' and msg != b'+CMS ERROR: 321\r\n': # then exists sms with this index
                cmd = "".join(['{:c}'.format(b) for b in cmd])
                if cmd[0] == '+':
                    #print("Message with index: " + str(self.index))
                    self.number = cmd.split(",")[1] #phone number
                    #print("Phone nr: " + self.number)
                    msg = "".join(['{:c}'.format(b) for b in msg])
                    self.msg_from = msg[0] # just one character # or !
                    #print("Message: " + self.msg_from)
                    
                    if URL.flg_url_state == True:
                        self.serial_writer.write(self.delete_msg + self.index + '\r\n')
                        await self.serial_writer.drain()
                        ResetIfBlocked.wdt.feed()
                    
                        ok_resp = await self.serial_reader.readline()
                        ResetIfBlocked.wdt.feed()
                        #print('Deleted msg - idx: ' + self.index)
                    else:
                        continue

                else:
                    self.serial_writer.write(self.delete_msg + self.index + '\r\n')
                    await self.serial_writer.drain()
                    ResetIfBlocked.wdt.feed()

                    ok_resp = await self.serial_reader.readline()
                    ResetIfBlocked.wdt.feed()
                    #print('Deleted msg - idx: ' + self.index)
                    
                    ResetIfBlocked.wdt.feed()
                    continue

            if self.msg_from == '#': # TODO: and when it receives '!'
                self.led_sms_send.on()
                temp = self.send_msg + self.number
                self.serial_writer.write("{}\r\n".format(temp))
                await self.serial_writer.drain()
                ResetIfBlocked.wdt.feed()
                await uasyncio.sleep(1)
                
                temp = "Hi, there!\nKeep an eye on me, here is your link:\n" + URL.url_google_maps_normal + str(chr(129)) # 129 -> Enter
                self.serial_writer.write(temp) #use static variable
                await self.serial_writer.drain()
                ResetIfBlocked.wdt.feed()
                await uasyncio.sleep(1)
            
                self.serial_writer.write(chr(26)) # Ctrl+Z
                await self.serial_writer.drain()
                await uasyncio.sleep(1)
                ResetIfBlocked.wdt.feed()
                
                self.led_sms_send.off()
            
            if self.msg_from == '!': # check how gsm interprets '$' sign
                self.led_sms_send.on()
                temp = self.send_msg + self.number
                self.serial_writer.write("{}\r\n".format(temp))
                await self.serial_writer.drain()
                ResetIfBlocked.wdt.feed()
                await uasyncio.sleep(1)
                
                temp = "Hi, there!\nKeep an eye on me, here is your link:\n" + URL.url_google_maps_satellite + str(chr(129)) # 129 -> Enter
                self.serial_writer.write(temp) #use static variable
                await self.serial_writer.drain()
                ResetIfBlocked.wdt.feed()
                await uasyncio.sleep(1)
            
                self.serial_writer.write(chr(26)) # Ctrl+Z
                await self.serial_writer.drain()
                await uasyncio.sleep(1)
                ResetIfBlocked.wdt.feed()
                
                self.led_sms_send.off()