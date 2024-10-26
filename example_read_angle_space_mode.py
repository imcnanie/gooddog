#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python39Packages.pyserial python39Packages.numpy

import serial
import time
import signal
import sys
import numpy as np
import math

# arm must be initialized fully extended and straight up as possible!

#from LUT.torque_table import torque_table
from torque_table_RR_0 import torque_table as lut_rr0
from torque_table_RR_1 import torque_table as lut_rr1
from torque_table_RR_2 import torque_table as lut_rr2

#                    theta_mot1:theta_mot2:torque_mot1(Nm)
arm_configuration = {"neg_arm_extended":  {"theta_m1":-math.pi/2, "theta_m2":math.pi/4,   "torque_mot1":0.61}, #arm fully extended in negative direction torque neede to balance gravity
                     "neg_arm_retracted": {"theta_m1":-math.pi/2, "theta_m2":math.pi*3/4, "torque_mot1":0.5}, #arm fully retracted in negative direction torque neede to balance gravity
                     "pos_arm_extended":  {"theta_m1":math.pi/2,  "theta_m2":math.pi/4,   "torque_mot1":-0.61}, #arm fully extended in positive direction torque neede to balance gravity
                     "pos_arm_retracted": {"theta_m1":math.pi/2,  "theta_m2":math.pi*3/4, "torque_mot1":-0.5}, #arm fully retracted in positive direction torque neede to balance gravity
                     "arm_straight_up":   {"theta_m1":0,          "theta_m2":0,           "torque_mot1":0}}  #arm straight up torque needed to balance gravity, actually arm is slightly not balanced here, so need to figure in

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
    set_motor_torque(0.0, lut_rr1)
    time.sleep(0.1)

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

def get_value_from_torque(Torque):
    # this function proves itself to be unnecessary, the Num on the LUTs is in 10000N
    # to convert g to Nm (((1833g/1000)kg*9.81)N)*.231775m
    # use find_polynomial to generate a new one of these if you update torque_measurements.csv
    #return 9920.6733 * Torque + 1172.0975
    return 10093.5836 * Torque + 592.6585

def simple_value_from_torque(Torque):
    return -10000*Torque

def interpret_signed_angle(hex_string):
    """
    Interpret the given hex string as a single signed 32-bit integer in little-endian format.

    Parameters:
    hex_string (str): A hex string of 8 characters representing a 32-bit value in little-endian.

    Returns:
    int: The interpreted signed integer.
    """
    # Ensure the hex string has exactly 8 characters (4 bytes)
    if len(hex_string) != 8:
        return "Error: Invalid input length"

    # Interpret the entire 8-character hex string as a little-endian signed 32-bit integer
    # Convert hex to an integer with two's complement interpretation
    signed_value = float(int.from_bytes(bytes.fromhex(hex_string), "little", signed=True))

    return -signed_value/20000 #TODO it's probably not div/2 measure angle accurately! This should be radians


motor_data = {"mot0_angle": None,
              "mot1_angle": None,
              "mot2_angle": None}
def read_and_update_motor_data():
    response = serial_port.read(int(156/2)).hex()

    try:
        if response.startswith("feee00010a00"):
            motor_data["mot0_angle"] = float(interpret_signed_angle(response[60:68]))
        
        if response.startswith("feee01010a00"):
            motor_data["mot1_angle"] = float(interpret_signed_angle(response[60:68])) + 0.35
        
        if response.startswith("feee02010a00"):
            motor_data["mot2_angle"] = -float(interpret_signed_angle(response[60:68]))

    except (ValueError, TypeError) as e:
        print("Data corruption detected or invalid angle data:", e)

def set_motor_torque(torque, lookup_table):
    nearest_packet, nearest_key = find_nearest_packet(simple_value_from_torque(torque), lookup_table) 
    serial_port.write(nearest_packet[:36]) # todo check if we need :36

def calc_spacemode_torques(motor_data):
    torque_extended = arm_configuration["pos_arm_extended"]["torque_mot1"]
    torque_retracted = arm_configuration["pos_arm_retracted"]["torque_mot1"]
    
    angle_min = math.pi / 4  # fully extended
    angle_max = 3 * math.pi / 4  # fully retracted
            
    mot2_angle = motor_data['mot2_angle']  # e.g., math.pi / 2 for midpoint torque
    
    #mot2_angle = max(min(mot2_angle, angle_max), angle_min)
    
    interpolation_factor = (mot2_angle - angle_min) / (angle_max - angle_min)
            
    
    current_torque_mot1 = torque_extended + interpolation_factor * (torque_retracted - torque_extended)
    
    current_torque = ( current_torque_mot1*math.sin(motor_data['mot1_angle']) )
    return current_torque
    
        
current_torque = 0.0
mot1_angle = 0.0
mot2_angle = math.pi/4.0
if __name__ == "__main__":
    port_name = "/dev/ttyUSB0"
    serial_port = configure_serial(port_name)

    # Handle CTRL+C to safely close the serial port
    signal.signal(signal.SIGINT, lambda signum, frame: handle_exit_signal(signum, frame, serial_port))

    try:
        print("Sending packets forward and reverse in a loop...")
        # Write the first 36 bytes of the nearest packet
        while True:

            set_motor_torque(0.0, lut_rr0)
            time.sleep(0.005)
            read_and_update_motor_data()
            
            
            set_motor_torque(current_torque, lut_rr1)
            time.sleep(0.005)
            read_and_update_motor_data()
            
            time.sleep(0.005)
            
            set_motor_torque(0.0, lut_rr2)
            time.sleep(0.005)
            read_and_update_motor_data()

            
            try:
                current_torque = calc_spacemode_torques(motor_data)

                #print(current_torque)
                #print(motor_data)
                print([f"{value:.4f}" for value in motor_data.values()])

            except (ValueError, TypeError) as e:
                print("Data corruption detected or invalid angle data:", e)
            
                
    except KeyboardInterrupt:
        pass
    
    finally:    
        serial_port.close()
        print("Serial port closed.")
