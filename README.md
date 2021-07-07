# obd
python script to communicate with OBDLink SX connector

## About OBDLink SX (text is just copied from the official homepage)
https://www.obdlink.com/products/obdlink-sx/
OBDLink SX USB is an easy-to-use, inexpensive, lightning-fast USB OBD adapter that can turn your tablet, laptop, or netbook into a sophisticated diagnostic scan tool, trip computer, and real-time performance monitor.
SX USB supports all legislated OBD-II protocols, and works with all 1996 & newer cars and light trucks sold in the United States. It also supports EOBD, JOBD, and all other international variants of OBD-II.

## About this script
This is a very basic and simple python script to communicate with the OBDLink SX connector via serial and AT/ST commands.

## Usage
```
┌──(root💀kali)-[/opt/obd]
└─# ./obd.py -h                                                 
usage: obd.py [-h] [-p PORT] [-b BAUDRATE] [-c CMD [CMD ...]] [-d DELIM]

optional arguments:
  -h, --help        show this help message and exit
  -p PORT           serial port e.g. COM7,COM14
  -b BAUDRATE       baudrate of serial
  -c CMD [CMD ...]  AT/ST command to send
  -d DELIM          delimiter 

```
You might need or just want to adjust how the OBDLink tool responds e.g. turning echo of the command on/off or turning linefeed on/off. If you change these settings you might need to adjust the script for that. e.g.
```
AT E1/E0 # turn echo on/off
AT L1/L0 # turn linefeed on/off
```
For more information on the available AT and ST commands please refer to 
 - https://www.elmelectronics.com/wp-content/uploads/2017/01/ELM327DS.pdf
 - https://cdn.sparkfun.com/datasheets/Widgets/stn1110-ds.pdf

Example for script usage:

  - ATI - get chip versioninfo
  - ATSD xx - save data in chip (1byte)
  - ATRD - read saved data from chip (1byte)

![example](https://github.com/zaphoxx/obd/blob/main/obd-script_example.png "Example for script usage.")

