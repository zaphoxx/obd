# obd
python script to communicate with OBDLink SX connector

simple python script to communicate with the OBDLink SX connector via serial and AT commands.

```
┌──(root💀kali)-[/opt/obd]
└─# ./obd.py -h                                                 
usage: obd.py [-h] [-p PORT] [-b BAUDRATE] [-c CMD [CMD ...]] [-d DELIM]

optional arguments:
  -h, --help        show this help message and exit
  -p PORT           serial port e.g. COM7,COM14
  -b BAUDRATE       baudrate of serial
  -c CMD [CMD ...]  AT command to send
  -d DELIM          delimiter 

```
you might need or just want to adjust how the OBDLink tool responds e.g. turning echo of the command on/off or turning linefeed on/off. If you change these settings you might need to adjust the script for that. e.g.
```
AT E1/E0 # turn echo on/off
AT L1/L0 # turn linefeed on/off
```
for more information on the available AT and ST commands please refer to 
 - https://www.elmelectronics.com/wp-content/uploads/2017/01/ELM327DS.pdf
 - https://cdn.sparkfun.com/datasheets/Widgets/stn1110-ds.pdf

example for script usage:

  - ATI - get chip versioninfo
  - ATSD xx - save data in chip (1byte)
  - ATRD - read saved data from chip (1byte)

![example](https://github.com/zaphoxx/obd/blob/main/obd-script_example.png "Example for script usage.")
