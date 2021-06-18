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

example for script usage:

  - ATI - get chip versioninfo
  - ATSD xx - save data in chip (1byte)
  - ATRD - read saved data from chip (1byte)

![example](https://github.com/zaphoxx/obd/blob/main/obd-script_example.png "Example for script usage.")
