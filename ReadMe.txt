-> machine module is for generic board in contrast with pyb lib

-> This project was started with gps and gsm modules
on a simple plastic board with attached cables for
TTL conversion for USB and Pycharm was used to link up
with devices.

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

-> Basic functions read, readline, write from UART module of micropython do not work
as expected, by using uasyncio lib with StreamWriter and StreamReader classes only then characters
are stored in UART buffer and read or written as wanted. From StreamWriter class use drain function after a write func
to output buffer data or just awrite method(it uses internally drain()).

Possibilities for gsm Ctrl-Z problem:
-> It takes some time to process, send and return a status for SMS so an
immediate read doesn't report anything. A subsequent read may.
I would keep issuing read until you get something other than nothing.

-> The GA6 isn't actioning the Ctrl-Z. Issuing a write 'ABC\r' and a read
should show if it's still in its waiting for message mode.

-> For some reason the Ctrl-Z isn't being sent to the GA6.
Again, issuing a write 'ABC\r' and a read should show if it's still in its waiting for message mode.

-> Looking at what gets sent out with a Terminal Emulator
instead of the GA6 should confirm whether Ctrl-Z's are sent or not.
Being the ASCII code for "EOF - End of File' imeans it could be handled differently
to printable ASCII codes, but if that's the case would how any other GA6 user has achieved it.