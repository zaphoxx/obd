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
# commands used for monitor mode
MONITORCMD = ["atma","at ma","stma","st ma","st m","stm"]
MODES = [b'ATSP0',b'ATSP6',b'ATSP7']

#container = []
'''
    note1:  'BUFFER FLOW' - increasing baudrate (STSBR command)    
            in case you repeatedly get 'BUFFER FULL' messages, try to increase the baudrate using the STSBR or STBR command.
            The Baudrate will be reset to default (115200kBaud) when using the STRSTNVM (reset non volatile memory) command.
            Keep in mind that when using the the STSBR command e.g. STSBR 500000 to set the baudrate to 500kBaud you need to
            restart the script with the parameter -b set to the new baudrate.
'''

class CanData:
    def __init__(self, arb_id = None, data_list = None, occurance_list = None):
        if arb_id == None:
            self.arb_id = 0xfff         # arbitration id
        else:
            self.arb_id = arb_id
        if data_list == None:        
            self.data_list = []          # list of distinguished data sets
        else:
            self.data_list = data_list
        if occurance_list == None:
            self.occurance_list = []     # list of occurances for each data set
        else:
            self.occurance_list = occurance_list


def main():
    args = process_args(argparse.ArgumentParser())
    show_settings(args)
    ser = connect_serial(args)
    fn = None
    if args.outfile != None:
        fn = open(outfile,"wb");
    
    try:
        # execute all commands in sequence
        for n in range(len(args.cmd)):
            cmd = args.cmd[n].lower()
            send_cmd(ser, cmd)
            data = recv_data(ser, cmd)
            print(data)
            if fn:
                for d in data:
                    fn.write(d)
    except:
        if fn:
            fn.close()

    if args.canmon:
        print("[+] Starting CAN monitoring mode")
        input("<press key to continue>")
        monitor(ser, args)
    
    # switch to interactive mode
    if args.interactive:
        interactive(ser, args)

    # close open serial
    if ser.isOpen():
        ser.close()


def monitor(ser, args):
    init_stn11xx(ser)
    
    print(MODES[args.canmon]) 
    ser.write(MODES[args.canmon]+b'\r')
    data = recv_data(ser, args.canmon)
    
    ser.write(b'ATMA\r')
    data = recv_data(ser, 'atma', args)


def init_stn11xx(ser):
    init_seq = [b'ATZ\r',b'ATE0\r',b'ATL0\r',b'ATS1\r',b'ATH1\r',b'ATCSM0\r',b'ATCAF0\r']
    for cmd in init_seq:
        ser.write(cmd)
        data = recv_data(ser, None)
    

def isOK(ser, cmd):
    if b'OK' in recv_data(ser, cmd):
        return True
    else:
        return False


def recv_data(ser, cmd, args = None): 
    container = []
    dataset = {}
    id_len = 0
    if cmd in MONITORCMD:
        try:
            while(1):
                if args != None:
                    if args.canmon == 1:
                        id_len = 1
                    if args.canmon == 2:
                        id_len = 4

                data = ser.read_until(b'\r')
                arb_id = b"".join(data.split(b' ')[:id_len])
                print(id_len)
                print(arb_id)
                data_frame = b" ".join(data.split(b' ')[id_len:])
                print(data_frame)
                                
                #print(data.decode('latin-1'))
                clear_screen()
                vline = "-"*51                
                header = "{: <10} {: <10} {: <10}".format("#n", "arb id", "data frame")
                print(vline); print(header)
                #for box in container:                
                #    print_data(box)
                for k,v in dataset.items():
                    print(vline)
                    for frame in v.data_list:
                        print("{: <10} {: <10} {: <10}".format(v.occurance_list[v.data_list.index(frame)], k.decode('latin-1'), frame.decode('latin-1')))
                        #print_data(frame)
                print(vline)                
                #print(container)  
                
                #print(data_frame)
                if data not in container:
                    container.append(data)
                    datapoint = CanData(arb_id, [data_frame], [1])
                    dataset.update({arb_id:datapoint})
                else:
                    if arb_id in dataset.keys():
                        #print(arb_id)
                        datapoint = dataset[arb_id]
                        #print(datapoint.data_list)
                        if data_frame in datapoint.data_list:
                            datapoint.occurance_list[datapoint.data_list.index(data_frame)] += 1
                            dataset.update({arb_id:datapoint})
                        else:
                            datapoint.data_list.append(data_frame)
                            datapoint.occurance_list.append(1)
                            dataset.update({arb_id:datapoint})       
        except KeyboardInterrupt:
            # stopp data accumulation                
            ser.write(b'\r\n')
            data = ser.read_until(b'>')
            parts = data.split(b'\r')            
            ser.reset_input_buffer()
            
            # save dataset information to session file
            save_session(dataset)
            
            # save output to a tmp file
            with open("data.log","wb") as tmp:
                for data in container:
                    tmp.write(data + b'\n')
           
            
    else:        
        while(1):
            data = ser.read_until(b'>')
            parts = data.split(b'\r')
            for p in parts:
                if p != b'' and p != b'>':
                    print_data(p)    
                    container.append(p)                           
            if ser.in_waiting < 1:
                break
            
    return container


def save_session(dataset):
    try:
        with open("session.log","w") as sess:
            for arbid, data in dataset.items():
                for datapoint in data.data_list:
                    sess.write(F"{arbid.decode('latin-1')},{datapoint.rstrip().decode('latin-1')},{data.occurance_list[data.data_list.index(datapoint)]}\n")
                    
    except Exception as logError:
        print(F"[!] Error saving data to file! {logError}")
        raise


def interactive(ser, args):
    print("Entering interactive mode! Press 'x' to exit!")
    while(1):
        cmd = input("> ").lower()
        if cmd == 'x':
            break
        send_cmd(ser, cmd)
        data = recv_data(ser, cmd, args)
        print(data)


def send_cmd(ser, cmd):
    cmd += F"\r"
    ser.write(cmd.encode('latin-1'))


def print_data(data):
    print(time.strftime("[%X] ") + data.decode('latin-1'))


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
    parser.add_argument('-c', dest='cmd', nargs='+', help='AT command to send')
    parser.add_argument('-d', dest='delim', help='delimiter', default='\r\r')
    parser.add_argument('-o', dest='outfile', help='output content to a file', default=None)
    parser.add_argument('-i', dest='interactive', action='store_true', default=False)
    # can monitoring
    # 0 - no can monitoring
    # 1 - 500kbd, 11bit
    # ... more might follow e.g. 500kbd, 29bit
    parser.add_argument('--can-mon', dest='canmon', type=int, choices=[0,1], default=0)
    parser.add_argument('--uds-bf', dest='uds_bf', action='store_true', default=False)
    args = parser.parse_args()
    return args


def show_settings(args):
    print('[info] Using following settings:')
    print('-'*37)
    for k,v in args.__dict__.items():
        print(F'{str(k).ljust(15)}: {str(v).rjust(20)}')
    print('-'*37)


def clear_screen():
    print(chr(27)+'[2j')
    print('\033c')
    print('\x1bc')


if __name__ == "__main__":
    main()

