#!/usr/bin/python3

import sys
import argparse
import random
import string
import serial
import time
import keyboard
import os
from colorama import Fore, Back, Style

BUFFER_SIZE = 16

def main():
    args = process_args(argparse.ArgumentParser())
    show_settings(args)
    ser = connect_serial(args)

    send_cmd(ser, args)
    
    if ser.isOpen():
      ser.close()


def send_cmd(ser, args):
    print(F"{Fore.GREEN}[+]{Fore.WHITE} Sending command \'{args.cmd}\' ...")
    # string all commands together and add '\r\n' so each command gets send seperately
    cmd = ""
    for c in args.cmd:
        cmd += F"{c}\r\n"
    ser.write(cmd.encode('latin-1'))
    
    # read (and print) response until input buffer is empty or 'space' pressed
    buffer = b""
    while (1):
        print(time.strftime("[%X] ") + "-"*60)
        buffer = ser.read_until(b'>')
        parts = buffer.split(b'\r')
        for p in parts:
            if p != b'' and p != b'>':
                print(p.decode('latin-1'))
                
        #print(b"[" + buffer + b"]")
        if keyboard.is_pressed('space') or ser.in_waiting < 1:
            break
    ser.reset_output_buffer()
    ser.reset_input_buffer()


def connect_serial(args):
    try:
      ser = serial.Serial(baudrate = args.baudrate, 
                          port = args.port,
                          timeout = 1)
      return ser
    except:
      print(F"[ERROR] Could not connect serial at {args.port}. Is device plugged in? Did you select the correct port?")
      sys.exit(1)
    

# process arguments    
def process_args(parser):
    parser.add_argument('-p', dest='port', help='serial port e.g. COM7,COM14', default='/dev/ttyUSB0')
    parser.add_argument('-b', dest='baudrate', type=int, help='baudrate of serial', default=38400)
    parser.add_argument('-c', dest='cmd', nargs='+', help='AT command to send', default='ATZ')
    parser.add_argument('-d', dest='delim', help='delimiter', default='\r\r')
    args = parser.parse_args()
    return args


def show_settings(args):
    print('[info] Using following settings:')
    print('-'*37)
    for k,v in args.__dict__.items():
        print(F'{str(k).ljust(15)}: {str(v).rjust(20)}')
    print('-'*37)

if __name__ == "__main__":
    main()

