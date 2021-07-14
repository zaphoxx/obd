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

BUFFER_SIZE = 1024

def main():
    args = process_args(argparse.ArgumentParser())
    show_settings(args)
    ser = connect_serial(args)
   

    for n in range(len(args.cmd)):
        send_cmd(ser, args.cmd[n])
        
        while(1):
            data = recv_data(ser)
            if ser.in_waiting < 1:
                break
    
    if args.interactive:
        interactive(ser, args)

    
    if ser.isOpen():
        ser.close()


def interactive(ser, args):
    print("Entering interactive mode! Press 'x' to exit!")
    while(1):
        command = input("> ").lower()
        if command == 'x':
            break
        send_cmd(ser, command)
        cont = False
        while(1):
            data = recv_data(ser)
            #print(data)            
            #print_data(data)
            #if args.outfile != None:
            #    save_data(args.outfile,data)
            if ser.in_waiting < 1 and command != 'atma' and command != 'at ma' and  command != 'stma' and command != 'st ma': 
                break
            #cont = (keyboard.read_key() == 'space' or keyboard.read_key() == 'esc')
            if (keyboard.read_key() == 'space'):
                print("x"*20)
                break            
            #send_cmd(ser, '\r\n')
        else:
            print('\r',end='\x7f')
            send_cmd(ser, '\r\n')
            recv_data(ser)
            
            #print_data(data)


def send_cmd(ser, cmd):
    cmd += F"\r"
    ser.write(cmd.encode('latin-1'))


def recv_data(ser):
    buffer = b""
    parts = []
    buffer = ser.read(256)
    print(buffer.decode('latin-1'))   
    parts.append(buffer)    
    while ser.in_waiting > 0:            
        buffer = ser.read(256)
        parts.append(buffer)
        if keyboard.read_key() == 'esc':
            ser.write(b'\r\n')
            break
        print(buffer.decode('latin-1'))
    return parts


def print_data(data):
    #print(time.strftime("[%X] ") + "-"*60)
    #print(data)
    for p in data:
        if p != b'' and p != b'>':
            print(time.strftime("[%X] ") + p.decode('latin-1'))


def save_data(fn, data):
    with open(fn, "ba") as fin:
        for i in data:
            if i != b'' and i != b'>':
                fin.write(i)
        fin.write(b'\n')


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
    parser.add_argument('-o', dest='outfile', help='output content to a file', default=None)
    parser.add_argument('-i', dest='interactive', action='store_true', default=False)
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

