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

def build_a_packet(torque):
    header = "feee"
    motor_id = "02" #00 01 02
    part1 = "ba0aff000000000000" # TODO
    torque = torque_to_hex(torque) #torque 00-ff 0600 is positive, 06ff is negative
    part2 = "ff7fcd2f01800000ba11020000000000" #TODO
    
    raw_packet = header + motor_id + part1 + torque + part2
    return raw_packet + get_go1_crc(raw_packet)


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
