import math
start_bit_offset = 0
  
# def gamma_encode(number):
#     # Ensure the input number is greater than 0
#     if number <= 0:
#         raise ValueError("Input number must be greater than 0")

#     # Find the position of the most significant bit
#     msb_position = 0
#     while number >> msb_position:
#         msb_position += 1

#     # Calculate unary code (msb_position - 1 '1's followed by '0')
#     unary_code = '0' * (msb_position - 1) + '1'

#     # Calculate binary code (remaining bits excluding the most significant bit)
#     binary_code = format(number, f'0{msb_position - 1}b')[1:]

#     # Combine unary and binary codes
#     gamma_code = unary_code + binary_code

#     return gamma_code

# def gamma_decode(gamma_code):
#     # Find the position of the first '0' to separate unary and binary codes
#     separator_index = gamma_code.find('1')

#     # Extract unary and binary codes
#     unary_code = gamma_code[:separator_index + 1]
#     binary_code = gamma_code[separator_index + 1:]

#     # Calculate the decoded number
#     decoded_number = (1 << len(binary_code)) + int(binary_code, 2)

#     return decoded_number

# def rice_encode(number, k):
#     # Calculate quotient and remainder
#     quotient = number // (2 ** k)
#     remainder = number % (2 ** k)

#     # Encode quotient in unary code
#     unary_code = '1' * quotient + '0'

#     # Encode remainder in binary code
#     binary_code = format(remainder, f'0{k}b')

#     # Combine unary and binary codes
#     rice_code = unary_code + binary_code

#     return rice_code

# def rice_decode(rice_code, k):
#     # Find the index of the first '0' to separate unary and binary codes
#     separator_index = rice_code.find('0')

#     # Extract unary and binary codes
#     unary_code = rice_code[:separator_index + 1]
#     binary_code = rice_code[separator_index + 1:]

#     # Decode unary code to get the quotient
#     quotient = unary_code.count('1')

#     # Decode binary code to get the remainder
#     remainder = int(binary_code, 2)

#     # Calculate the original number
#     number = quotient * (2 ** k) + remainder

#     return number

def vbyte_encode(pos_int):
    result = chr(pos_int & 127) if pos_int < 128 else chr(128 | (pos_int & 127))
    pos_int >>= 7
    while pos_int > 0:
        result += chr(pos_int & 127) if pos_int < 128 else chr(128 | (pos_int & 127))
        pos_int >>= 7
    return result

def vbyte_decode(data, offset):
    pos_int = ord(data[offset]) & 127
    shift = 7
    while (ord(data[offset]) & 128) > 0:
        offset += 1
        pos_int += (ord(data[offset]) & 127) << shift
        shift += 7
    offset += 1
    return pos_int, offset

def decode_unary(input_str):
    global start_bit_offset
    cur_char = start_bit_offset >> 3
    if cur_char >= len(input_str):
        return False

    bits_first_byte = start_bit_offset & 7
    cur_ord = (ord(input_str[cur_char]) << bits_first_byte) & 255

    if cur_ord > 0:
        decoded_number = 9 - math.ceil(math.log2(cur_ord + 1))
        start_bit_offset += decoded_number
        return decoded_number

    decoded_number = 8 - bits_first_byte

    while True:
        cur_char += 1
        cur_ord = ord(input_str[cur_char]) if cur_char < len(input_str) else ord("\0")
        if cur_ord == 0:
            decoded_number += 8
        else:
            decoded_number += 9 - math.ceil(math.log2(cur_ord + 1))
        if cur_ord != 0 or cur_char >= len(input_str):
            break

    start_bit_offset += decoded_number
    return decoded_number

def append_unary(number, input_str, just_bit_offset=False):
    global start_bit_offset
    total_bits = start_bit_offset + number

    if just_bit_offset:
        # only compute new bit offset
        start_bit_offset = total_bits
        return input_str

    bits_last_byte = total_bits & 7
    total_chars = total_bits >> 3 if bits_last_byte == 0 else (total_bits >> 3) + 1
    bits_first_byte = start_bit_offset & 7
    start_char = start_bit_offset >> 3

    output = input_str[:start_char + 1].ljust(total_chars, "\x00")

    start_char_ord = ord(output[start_char]) if start_char < len(output) else 0
    start_char_ord &= ((1 << bits_first_byte) - 1) << (8 - bits_first_byte)
    output = output[:start_char] + chr(start_char_ord) + output[start_char + 1:]

    last_ord = ord(output[total_chars - 1]) if total_chars > 0 else 0
    output = output[:total_chars - 1] + chr(last_ord + (1 if bits_last_byte == 0 else 1 << (8 - bits_last_byte)))

    start_bit_offset = total_bits
    return output

def append_bits(number, input_str, num_bits=-1):
    global start_bit_offset
    start_char = start_bit_offset >> 3
    num_bits = num_bits if num_bits != -1 else int(math.ceil(math.log2(number + 1)))
    total_bits = start_bit_offset + num_bits
    bits_last_byte = total_bits & 7
    total_chars = total_bits >> 3 if bits_last_byte == 0 else (total_bits >> 3) + 1

    number &= (1 << num_bits) - 1  # notice using low order here

    output = input_str[:start_char + 1].ljust(total_chars, "\x00")
    cur_char = total_chars - 1
    cur_bits = number & ((1 << bits_last_byte) - 1)
    number >>= bits_last_byte
    start_remaining_bits = num_bits - bits_last_byte
    shift_last_byte = 0 if bits_last_byte == 0 else 8 - bits_last_byte
    output = output[:cur_char] + chr(ord(output[cur_char]) + (cur_bits << shift_last_byte)) + output[cur_char + 1:]

    cur_char -= 1

    remaining_bits = start_remaining_bits
    while remaining_bits > 7 :
        output = output[:cur_char] + chr(number & 255) + output[cur_char + 1:]
        remaining_bits -= 8
        cur_char -= 1
        number >>= 8

    if remaining_bits > 0:
        start_char_ord = ord(output[start_char])
        start_char_ord &= 255 - (1 << (remaining_bits - 1))
        output = output[:start_char] + chr(start_char_ord + number) + output[start_char + 1:]

    start_bit_offset = total_bits
    return output

def decode_bits(input_str, num_bits):
    global start_bit_offset
    cur_char = start_bit_offset >> 3
    total_bits = start_bit_offset + num_bits
    bits_first_byte = start_bit_offset & 7
    input_char = input_str[cur_char] if cur_char < len(input_str) else ''
    cur_ord = ((ord(input_char) << bits_first_byte) & 255) >> bits_first_byte
    output = cur_ord & ((1 << (8 - bits_first_byte)) - 1)

    if num_bits <= 8 - bits_first_byte:
        excess_bits = 8 - bits_first_byte - num_bits
        output >>= excess_bits
        start_bit_offset = total_bits
        return output

    remaining_bits = num_bits - (8 - bits_first_byte)
    cur_char += 1

    while remaining_bits > 7 and cur_char < len(input_str):
        output <<= 8
        output += ord(input_str[cur_char])
        remaining_bits -= 8
        cur_char += 1

    if remaining_bits > 0 and cur_char < len(input_str):
        last_char_ord = ord(input_str[cur_char])
        output <<= remaining_bits
        output += (last_char_ord >> (8 - remaining_bits))

    start_bit_offset = total_bits
    return output

def append_gamma(number, input_str):
    global start_bit_offset
    bit_len = int(math.ceil(math.log2(number + 1)))
    append_unary(bit_len, input_str, just_bit_offset=True)
    start_bit_offset -= 1  # $start_bit_offset will have advanced by append_unary call
    return append_bits(number, input_str, bit_len)

def decode_gamma_list(input_str, num_decode):
    global start_bit_offset
    out_list = []
    for i in range(num_decode):
        num_bits = decode_unary(input_str)
        start_bit_offset -= 1
        out_list.append(decode_bits(input_str, num_bits))
    return out_list

def append_rice_sequence(int_sequence, modulus, output, delta_start=-1):
    global start_bit_offset
    last_encode = delta_start
    output = append_unary(modulus, output)
    mask = (1 << modulus) - 1

    for pre_to_encode in int_sequence:
        to_encode = pre_to_encode if delta_start < 0 else pre_to_encode - last_encode
        to_encode -= 1
        last_encode = pre_to_encode

        output = append_unary((to_encode >> modulus) + 1, output)
        output = append_bits(to_encode & mask, output, modulus)

    return output

def decode_rice_sequence(input_str, num_decode, delta_start=-1):
    out_list = []
    last_decode = delta_start
    modulus = decode_unary(input_str)

    for i in range(num_decode):
        quotient = decode_unary(input_str) - 1
        remainder = decode_bits(input_str, modulus)
        decode = (quotient << modulus) + remainder + 1
        last_decode = decode if delta_start == -1 else last_decode + decode
        out_list.append(last_decode)

    return out_list

ip = ""
ip = append_gamma(534,ip)
ip = append_gamma(45323,ip)
# print(encoded)
start_bit_offset = 0
# print(repr(ip))
decoded = decode_gamma_list(ip,2)
print(decoded)
# print(start_bit_offset)

arr = [1,4,7]
mod = 4
op = ""
start_bit_offset = 0
op = append_rice_sequence(arr,mod,op,-1)
# print(repr(op))
start_bit_offset = 0
print(decode_rice_sequence(op,3,-1))