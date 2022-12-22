-> machine module is for generic board in contrast with pyb lib

-> This project was started with gps and gsm modules
on a simple plastic board with attached cables for
TTL conversion for USB and Pycharm was used to link up
with devices. 

-> Virtual environment for 
python interpreter for desktop was left here if anyone
want to build it, files for pcb and scheme is yet to come !!

-> In meantime the development of this project started on Pi pico, and
Thonny IDE is used afterwards, MicroPython plugin for Pycharm is not
so great. Although, Thonny IDE needs some improvement for USB communication, but for this 
issue a  reset button was attached for Pi pico to re-enable the communication.

-> There is a problem for matching modules to have a perfect synchronization as close as possible,
when working on a real PCB board, taking into consideration that components are not place as close as
possible to each other's pins which traces' inductance can increase substantialy.

-> For gps module a simple solution is to use a loop to wait for gps' data to come, but
this method is not very precise because of uncertainty of synchronization between python program and 
how quick gps sends its data in its specific format.

