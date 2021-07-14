#!/usr/bin/python3

# enumerate ecu units which support the uds protocol
# currently only supports the atsp6 / atsp8 elm327 supported protocols (CAN 500/11, CAN 250/11)


import argparse
import serial
import sys
import time
from colorama import Fore, Back, Style

UDS_SERVICE_NAMES = {
    0x10: "DIAGNOSTIC_SESSION_CONTROL",
    0x11: "ECU_RESET",
    0x14: "CLEAR_DIAGNOSTIC_INFORMATION",
    0x19: "READ_DTC_INFORMATION",
    0x20: "RETURN_TO_NORMAL",
    0x22: "READ_DATA_BY_IDENTIFIER",
    0x23: "READ_MEMORY_BY_ADDRESS",
    0x24: "READ_SCALING_DATA_BY_IDENTIFIER",
    0x27: "SECURITY_ACCESS",
    0x28: "COMMUNICATION_CONTROL",
    0x2A: "READ_DATA_BY_PERIODIC_IDENTIFIER",
    0x2C: "DYNAMICALLY_DEFINE_DATA_IDENTIFIER",
    0x2D: "DEFINE_PID_BY_MEMORY_ADDRESS",
    0x2E: "WRITE_DATA_BY_IDENTIFIER",
    0x2F: "INPUT_OUTPUT_CONTROL_BY_IDENTIFIER",
    0x31: "ROUTINE_CONTROL",
    0x34: "REQUEST_DOWNLOAD",
    0x35: "REQUEST_UPLOAD",
    0x36: "TRANSFER_DATA",
    0x37: "REQUEST_TRANSFER_EXIT",
    0x38: "REQUEST_FILE_TRANSFER",
    0x3D: "WRITE_MEMORY_BY_ADDRESS",
    0x3E: "TESTER_PRESENT",
    0x7F: "NEGATIVE_RESPONSE",
    0x83: "ACCESS_TIMING_PARAMETER",
    0x84: "SECURED_DATA_TRANSMISSION",
    0x85: "CONTROL_DTC_SETTING",
    0x86: "RESPONSE_ON_EVENT",
    0x87: "LINK_CONTROL"
}

NRC_NAMES = {
    0x00: "POSITIVE_RESPONSE",
    0x10: "GENERAL_REJECT",
    0x11: "SERVICE_NOT_SUPPORTED",
    0x12: "SUB_FUNCTION_NOT_SUPPORTED",
    0x13: "INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT",
    0x14: "RESPONSE_TOO_LONG",
    0x21: "BUSY_REPEAT_REQUEST",
    0x22: "CONDITIONS_NOT_CORRECT",
    0x24: "REQUEST_SEQUENCE_ERROR",
    0x25: "NO_RESPONSE_FROM_SUBNET_COMPONENT",
    0x26: "FAILURE_PREVENTS_EXECUTION_OF_REQUESTED_ACTION",
    0x31: "REQUEST_OUT_OF_RANGE",
    0x33: "SECURITY_ACCESS_DENIED",
    0x35: "INVALID_KEY",
    0x36: "EXCEEDED_NUMBER_OF_ATTEMPTS",
    0x37: "REQUIRED_TIME_DELAY_NOT_EXPIRED",
    0x70: "UPLOAD_DOWNLOAD_NOT_ACCEPTED",
    0x71: "TRANSFER_DATA_SUSPENDED",
    0x72: "GENERAL_PROGRAMMING_FAILURE",
    0x73: "WRONG_BLOCK_SEQUENCE_COUNTER",
    0x78: "REQUEST_CORRECTLY_RECEIVED_RESPONSE_PENDING",
    0x7E: "SUB_FUNCTION_NOT_SUPPORTED_IN_ACTIVE_SESSION",
    0x7F: "SERVICE_NOT_SUPPORTED_IN_ACTIVE_SESSION",
    0x81: "RPM_TOO_HIGH",
    0x82: "RPM_TOO_LOW",
    0x83: "ENGINE_IS_RUNNING",
    0x84: "ENGINE_IS_NOT_RUNNING",
    0x85: "ENGINE_RUN_TIME_TOO_LOW",
    0x86: "TEMPERATURE_TOO_HIGH",
    0x87: "TEMPERATURE_TOO_LOW",
    0x88: "VEHICLE_SPEED_TOO_HIGH",
    0x89: "VEHICLE_SPEED_TOO_LOW",
    0x8A: "THROTTLE_PEDAL_TOO_HIGH",
    0x8B: "THROTTLE_PEDAL_TOO_LOW",
    0x8C: "TRANSMISSION_RANGE_NOT_IN_NEUTRAL",
    0x8D: "TRANSMISSION_RANGE_NOT_IN_GEAR",
    0x8F: "BRAKE_SWITCHES_NOT_CLOSED",
    0x90: "SHIFT_LEVER_NOT_IN_PARK",
    0x91: "TORQUE_CONVERTER_CLUTCH_LOCKED",
    0x92: "VOLTAGE_TOO_HIGH",
    0x93: "VOLTAGE_TOO_LOW"
}


def main():
    arb_id_pairs = []
    valid_service_ids = []
    parser = argparse.ArgumentParser(prog = 'discover uds')
    args = process_args(parser)
    show_settings(args)
    chosen_module = args.module
    
    # open serial connection
    ser = connect_serial(args)

    if chosen_module == "enum-uds":
        arb_id_pairs = enum_uds(ser, args)
    elif chosen_module == "enum-service":
        valid_service_ids = enum_service(ser, args)
    else:
        print("[!] Please select a module!")
    try:
        ser.close()
    except:
        pass


def enum_uds(ser, args):
    arb_id_pairs = []
    blacklist = []
    # identifies arbitration ids which do support uds
    protocol = args.protocol
    # initialize obdlink sx / elm327 / stn1130
    init_stn11xx(ser, args)

    # loop over all possible arbitration ids
    arb_id_min = 0x000
    arb_id_max = 0x7FF
    
    isotp = 0x02
    service_id = 0x10
    subfunction = 0x01
    msg = "{:02x}{:02x}{:02x}0000000000\r".format(isotp, service_id, subfunction).upper().encode('latin-1')
    print(msg)
    valid_responses = [b'50',b'7F']
    
    input("-- press key to continue --")
    
    for arb_id in range(arb_id_min, arb_id_max):
        s_arb_id = "{:03x}".format(arb_id).upper()
        print("\r[+] Probing {:>3}/{:03x}".format(s_arb_id, arb_id_max), end="")
        
        # set arbid header
        ser.write(b'ATSH ' + s_arb_id.encode('latin-1') + b'\r')
        data = recv_data(ser)
        if not b'OK' in data:
            print("[error]")
        else:
            ser.write(msg)
            data = recv_data(ser)
            b = data[0].split(b' ')
            if b[1] == valid_responses[0]:
                arb_id_pairs.append((int(args.source_id,16), arb_id))
            else:
                blacklist.append((int(args.source_id,16), arb_id))
    
    #arb_id_pairs = [(0x7bb,0x6e1),(0x7bb,0x431),(0x7bb,0x7e1)]
    print()
    print("[+] Found valid arbitration ids:")
    for p in arb_id_pairs:
        print("\t0x{:03x}, 0x{:03x}".format(p[0],p[1]))    
    
    print("[+] Blacklisted arbitration ids:")    
    for bl in blacklist:
        print("\t0x{:03x}, 0x{:03x}".format(bl[0],bl[1]))         
        
    return arb_id_pairs

    
def enum_service(ser, args):
    print("[+] Initialize STN11xx")
    init_stn11xx(ser, args)
    
    #loop through provided arbitration ids
    for aid in args.dest_id:
        #loop through service id list
        for sid, name in UDS_SERVICE_NAMES.items():
            print(aid, sid, name)
            


def init_stn11xx(ser, args):
    print("[+] Initialize STN11xx")
    try:
        # reset stn11xx, reset elm327, echo off, linefeed off, add spaces, add header id, auto format off, silent monitor off, use protocol X, set id filter
        init_seq = [b'ATZ\r',
                    b'ATE0\r',
                    b'ATL0\r',
                    b'ATS1\r',
                    b'ATH1\r',
                    b'ATCSM0\r',
                    b'ATCAF0\r',
                    b'ATSP' + str(args.protocol).encode('latin-1') + b'\r']
                    #b'ATCRA ' + "{:03x}".format(int(args.source_id,16)).upper().encode('latin-1') + b'\r']
        print(init_seq)
        for cmd in init_seq:
            ser.write(cmd)
            data = recv_data(ser)
            if b'OK' in data:
                print(Fore.GREEN + "[{cmd: <8}] - OK".format(cmd = cmd[:-1].decode('latin-1')) + Fore.WHITE)
            else:
                print(Fore.YELLOW + "[{cmd: <8}] - {data}".format(cmd = cmd[:-1].decode('latin-1'), data = "|".join(x.decode('latin-1') for x in data)) + Fore.WHITE)
    except:
        print("[!] Serial Error when sending AT command!")
        raise
        

def recv_data(ser, delimiter = b'>'):
    _data = []
    while(1):
        data = ser.read_until(delimiter)
        parts = data.split(b'\r')
        for p in parts:
            if p != b'' and p != delimiter:
                #print_data(p)    
                _data.append(p)                           
        if ser.in_waiting < 1:
            break
    return _data


def print_data(data):
    print(time.strftime("[%X] ") + data.decode('latin-1'))


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
    parser.add_argument('-p', dest = 'port', help = 'serial port e.g. COM7,COM14', default = '/dev/ttyUSB0')
    parser.add_argument('-b', dest = 'baudrate', type = int, help = 'baudrate of serial', default = 115200)
    parser.add_argument('--protocol', dest = 'protocol', type = int, choices = {6, 8}, default = 6, help = 'transfer protocol to use; id according to elm327 specification; e.g. 6 = CAN 500/11')
    # currently only protocols CAN 500/11 (6) and CAN 250/11 (8) are supported
    
    subparsers = parser.add_subparsers(help = 'commands', dest = 'module')
    enum_uds = subparsers.add_parser('enum-uds', help='enumerate which arbitration ids support uds.')
    enum_uds.add_argument('-s', dest='source_id', default = '7BB')
    
    enum_services = subparsers.add_parser('enum-service', help='enumerate available services for a list of arbitration ids.')
    enum_services.add_argument('-s', dest='source_id', default = '7BB')
    enum_services.add_argument('-d', dest='dest_id', nargs = '+')
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
