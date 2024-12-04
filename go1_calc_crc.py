#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3

import struct

POLY = 0x04C11DB7  # CRC32 polynomial

def crc32_core(data_words):
    crc = 0xFFFFFFFF  # Initial value
    for word in data_words:
        crc ^= word
        for _ in range(32):  # Process 32 bits of each word
            if crc & 0x80000000:
                crc = (crc << 1) ^ POLY
            else:
                crc <<= 1
            crc &= 0xFFFFFFFF  # Ensure crc stays within 32 bits
    return crc

def get_go1_crc(hex_string):
    """
    Process a Go1 payload: convert hex to bytes, read as 7 uint32_t words, and calculate CRC32.
    
    Parameters:
    hex_string (str): Hexadecimal string representing the payload.
    
    Returns:
    str: Hexadecimal string of payload with CRC appended.
    """
    data_bytes = bytes.fromhex(hex_string)
    
    data_words = struct.unpack('<7I', data_bytes[:28])
    
    crc = crc32_core(data_words)

    crc_bytes = struct.pack('<I', crc)

    return crc_bytes.hex()

def test_packet_crc(torque_entry):
    """
    Test each packet in the torque table by calculating the CRC and comparing it with the stored value.
    
    Parameters:
    torque_entry (dict): Dictionary containing 'hex' and 'packet' values for a torque entry.
    
    Returns:
    bool: True if the computed CRC matches the expected CRC, False otherwise.
    """
    packet = torque_entry['packet']
    data_bytes = packet[:-8]  # All bytes except the last 4 for CRC
    expected_crc = packet[-8:]  # Last 4 bytes for CRC
    crc_hex = get_go1_crc(data_bytes)

    # Test CRC matches expected
    return crc_hex == expected_crc

def build_a_packet(torque, motor):
    header = "feee"
    motor_id = motor #00 01 02
    part1 = "ba0aff000000000000" # TODO
    torque = torque_to_hex(torque) #torque 00-ff 0600 is positive, 06ff is negative
    if motor == "00":
        part2 = "ff7fcaecff7f0000e427020000000000" 
    elif motor == "01":
        part2 = "ff7ffd6a00800000e427020000000000" 
    elif motor == "02":
        part2 = "ff7f981001800000ba11020000000000" 
    
    raw_packet = header + motor_id + part1 + torque + part2
    return raw_packet + get_go1_crc(raw_packet)

def int_to_little_endian_hex(number):
    """
    Convert an integer to a 4-character little-endian hex string.
    
    Parameters:
    number (int): Integer to convert
    
    Returns:
    str: 4-character hex string in little-endian format
    """
    # Convert to 16-bit little endian bytes
    bytes_le = number.to_bytes(2, byteorder='little')
    # Convert bytes to hex string
    return bytes_le.hex()


def build_a_better_packet(torque, motor, gear_reduction):
    scaled_torque = int(torque*10000)
    header = "feee"
    motor_id = motor #00 01 02
    part1 = "ba"+"0a" # command var 2
    part1_b = "ff"
    part2 = torque_to_hex(int(scaled_torque))
    part3 = torque_to_hex(int(scaled_torque))
    part4 = torque_to_hex(int(scaled_torque)) # TODO
    torque = torque_to_hex(int(scaled_torque)) #torque 00-ff 0600 is positive, 06ff is negative
    part5 = "ff7f"
    if motor == "00":
        pids = "6e250080"#RL0 #"caec"+"ff7f"  #ff7f 7250 0080 0000 e427 02
        part6 = "0000"        #ff7f 5055 0080 0000 e427 02
        gear_reduction = int_to_little_endian_hex(gear_reduction) #"e427"
    elif motor == "01":
        pids = "fd6a"+"0080" 
        part6 = "0000"
        gear_reduction = "e427"
    elif motor == "02":
        pids = "6e25"+ "0080"#RL0 #"9810"+"0180"  # not sure if this is pids
        part6 = "0000"
        gear_reduction = int_to_little_endian_hex(gear_reduction) #"ba11" #maybe not gear reduction
    part7 = "02"
    part8 = "0000000000"
    #                                 ^ gear reduction
    #feee029d0affff006666e63e000000000000dbffff66000018050000000000006fb69a1b
    #feee00ba0aff0000000000000000ff7f6e2500800000e4270200000000000c7a1860
    
    raw_packet = header + motor_id + part1 + part1_b + part2 + part3 + part4 + torque + part5 + pids + part6 + gear_reduction + part7 + part8
    #raw_packet = "feee029d0affff006666e63e000000000000dbffff6600001805000000000000"
    
    #0xFE,0xEE,0x02,0xBA,0x0A,0xFF,0x00,0x00,0x00,0x00,0x00,0x00,0x6E,0xFF,0x00,0x00,0xFC,0x88,0xFF,0xFF,0x00,0x00,0x37,0x02,0x02,0x00,0x00,0x00,0x00,0x00,0xA2,0x5A,0x03,0x8A
    #raw_packet = "feee02ba0aff0000000000006e000000fc88ff7f00003702020000000000"
    #["feee029e0affffffff006666e63e0000ff7f805ce97f140000040600000000056032f59"],
    #raw_packet = "feee02f90affffffff006666e63e00000000873b0000cc00001001000000000"
    return raw_packet + get_go1_crc(raw_packet) # calc and append crc





def torque_to_hex(key):
    if key >= 0:
        speed = key // 256
        sign_byte = '00'
    else:
        speed = (key + 65281) // 256
        sign_byte = 'ff'
    speed_byte = '{:02x}'.format(speed)
    hex_value = speed_byte + sign_byte
    return hex_value


if __name__ == "__main__":
    from torque_table_RL_1 import torque_table

    # Test packets manually
    #s = 'feee02ba0aff0000000000008600ff7fce31ff7f0000ba11020000000000'
    #s = 'feee02ba0aff0000000000006600ff7fce31ff7f0000ba11020000000000' #931116a5
    s = 'feee02ba0aff0000000000006500ff7fce31ff7f0000ba11020000000000' #2bf63b98
    result = get_go1_crc(s)
    print("should be 2bf63b98: ", result)


    results = []
    for key, entry in torque_table.items():
        result = test_packet_crc(entry)
        results.append((key, result))
        print(f"packet: {key}, Expected CRC: {entry['packet'][-8:]}, Test Result: {'Pass' if result else 'Fail'}")

    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    print(f"\nSummary: {passed_tests}/{total_tests} tests passed.")
