#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python39Packages.pyserial python39Packages.numpy

import serial
import time
import numpy as np 
import ast
import pprint


pp = pprint.PrettyPrinter(indent=4)

def configure_serial(port):
    """
    Configure the serial port for communication at 5 Mbps,
    8 data bits, 1 stop bit, no parity.
    """
    # baudrate 5000000
    ser = serial.Serial(
        port=port,                   # Replace with your serial port (e.g., '/dev/ttyUSB0', 'COM3')
        baudrate=5000000,            # 5 Mbps baud rate
        bytesize=serial.EIGHTBITS,   # 8 data bits
        stopbits=serial.STOPBITS_ONE, # 1 stop bit
        parity=serial.PARITY_NONE,    # No parity
        timeout=0,                   # Non-blocking mode
        rtscts=False,                # No hardware flow control
        dsrdtr=False                 # Disable DSR/DTR flow control
    )

    # Flush input and output buffers to start fresh
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    return ser

def split_by_feee_packet(unparsed):
    return ["feee"+x for x in (''.join(unparsed)).split("feee")]

def filter_lines_of_specific_len(lines):
    # Set the desired length based on the reference packet
    desired_length = len("feee01d800ff00000000000000000000805ce97f000000000000000000000cb48ffa")

    #print(lines)
    # Filter lines that meet the specified length
    filtered_lines = [line for line in lines if len(line) == desired_length]

    return filtered_lines 

#24-27
RR_1 = "feee01ba0aff"
def filter_by_actuator(actuator, lines):
    """
    Filters the lines that start with the given actuator string.
    
    Args:
    actuator (str): The actuator string to filter by.
    lines (list): A list of lines to be filtered.

    Returns:
    list: A list of lines that start with the actuator string.
    """
    # Filter lines that start with the actuator string
    filtered_lines = [line for line in lines if line.startswith(actuator)]
    
    return filtered_lines


# the hex vals go from e.g. 9f00-0000 and loop over from ffff-60ff
# you can use the second byte ff or 00 to get the sign
def hex_to_twos_complement(hex_list):
    # Convert hex strings to signed integers
    signed_ints = np.array([int(x, 16) for x in hex_list], dtype=np.int64)
    for i, val in enumerate(signed_ints):
        if (val & 0xFF) == 0xFF:  # Check if the second byte is 'FF'
            signed_ints[i] -= 65536  # Subtract 65536 for the full 16-bit negative conversion
    return signed_ints


# Function to extract the 25th to 28th characters from the packets and convert them to signed floats... TODO I should rename this to SIGNED INTS
# These are the torque values
def extract_and_convert(packets):
    packet_bytes = [bytes.fromhex(x) for x in packets]
    extracted_hex = [packet[12:14].hex() for packet in packet_bytes]  # Extract hex substring
    signed_floats = hex_to_twos_complement(extracted_hex)  # Convert to signed floats
    return extracted_hex, signed_floats, packets


def generate_torque_table_source(torque_data):
    """
    Takes a dictionary of torque data and returns a string containing the source code
    for a Python file defining a torque_table.

    Parameters:
    torque_data (dict): The dictionary containing torque data.

    Returns:
    str: The formatted source code as a string.
    """
    # Initialize a list to store the lines of the source code
    output_lines = []
    output_lines.append("# torque_table.py\n")
    output_lines.append("torque_table = {\n")

    # Loop through each key-value pair in the dictionary and format it
    for torque_value, data in torque_data.items():
        hex_value = data['hex']
        packet_value = data['packet']
        formatted_line = f"    {torque_value}: {{ 'hex': '{hex_value}', 'packet': '{packet_value}' }},\n"
        output_lines.append(formatted_line)

    output_lines.append("}\n")

    # Join the list into a single string and return
    return ''.join(output_lines)


def read_serial_data(ser):
    """
    Continuously read data from the serial port, accumulate it in memory, and
    write it to a file as a continuous string of hexadecimal numbers with no spaces or newlines.
    """
    accumulated_data = []  # List to store all hex data

    try:
        while True:
            # Read data from the serial port
            data = ser.read(2048)  # Adjust buffer size as needed
            if data:
                # Convert the byte data to a continuous hexadecimal string with no spaces or newlines
                hex_data = ''.join(f'{byte:02x}' for byte in data)
                #print(hex_data)  # Print data for debugging purposes (can be removed if not needed)

                # Accumulate the hexadecimal data
                accumulated_data.append(hex_data)

            else:
                # No data read; small sleep to prevent busy waiting
                time.sleep(0.001)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()

        # Join all accumulated data into one big string and write it to the file at the end
        with open("torque_table2.py", mode="w") as file_writer:
            packets = split_by_feee_packet(accumulated_data)
            filtered_packets = filter_lines_of_specific_len(packets)
            filtered_by_actuator = filter_by_actuator(RR_1, filtered_packets)
            pp.pprint(filtered_by_actuator)
            
            # convert plaintext packets into hex list
            extracted_hex, signed_floats, paks = extract_and_convert(filtered_by_actuator)

            # turn it into a dict
            result_dict = {signed_float: {'hex': hex_val, 'packet': pak} 
                           for signed_float, hex_val, pak in zip(signed_floats, extracted_hex, paks)}

            generated_source_code = generate_torque_table_source(result_dict)
            

            file_writer.write(generated_source_code)

        print("Data written to file.")

if __name__ == "__main__":
    port_name = "/dev/ttyUSB0"  # Replace with your serial port (e.g., '/dev/ttyUSB0', 'COM3')
    serial_port = configure_serial(port_name)

    print("Starting to read data...")
    read_serial_data(serial_port)

    
