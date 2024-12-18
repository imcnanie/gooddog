#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python39Packages.pyserial python39Packages.numpy

import serial
import time
import signal
import sys
import numpy as np
import math

#from LUT.torque_table import torque_table
#from torque_table_FR_2 import torque_table # I definitely don't need it...
import go1_calc_crc as packetman

def configure_serial(port):
    ser = serial.Serial(
        port=port,                   
        baudrate=5000000,            
        bytesize=serial.EIGHTBITS,   
        stopbits=serial.STOPBITS_ONE, 
        parity=serial.PARITY_NONE,   
        timeout=0,                   
        rtscts=False,                
        dsrdtr=False                 
    )

    ser.reset_input_buffer()
    ser.reset_output_buffer()

    return ser

def send_packets(ser, packets, reverse=False):
    if reverse:
        packets = packets[::-1]

    for i, packet in enumerate(packets):
        ser.write(packet[:36])
        direction = "reverse" if reverse else "forward"
        print(f"Sent packet {i} in {direction}: {packet.hex().upper()}")
        time.sleep(0.05)

def handle_exit_signal(signum, frame, ser):
    print("\nCTRL+C detected. Closing serial port...")
    ser.close()
    sys.exit(0)

# You put in an int, get the nearest packet back
def find_nearest_packet(input_float, table):
    # Find the key in the table that is closest to the input_float
    closest_key = min(table.keys(), key=lambda k: abs(k - input_float))
    # Convert the hex string to bytes before returning
    packet_bytes = bytes.fromhex(table[closest_key]['packet'])
    return packet_bytes, closest_key
    
if __name__ == "__main__":
    port_name = "/dev/ttyUSB0"
    serial_port = configure_serial(port_name)

    # Handle CTRL+C to safely close the serial port
    signal.signal(signal.SIGINT, lambda signum, frame: handle_exit_signal(signum, frame, serial_port))

    try:
        print("Sending packets forward and reverse in a loop...")
        # Write the first 36 bytes of the nearest packet
        while True:
            sin_of_time = 3000*(math.sin(2 * math.pi * 0.1 * time.time())) 
            #nearest_packet, nearest_key = find_nearest_packet(sin_of_time, torque_table)
            #print(nearest_key)
            the_packet = packetman.build_a_better_packet(int(sin_of_time), "02", 0)


            #print(the_packet)
            
            serial_port.write(bytes.fromhex(the_packet)) # probably unecessary to slice, TODO check the number of bytes in the LUTs

    except KeyboardInterrupt:
        pass
    finally:
        serial_port.close()
        print("Serial port closed.")

        
