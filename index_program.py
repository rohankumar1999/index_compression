import math
import os
import string
import sys
import heapq
import time
from utils import Compressor
import json

index_dict = {}
sorted_index_dict = {}
doc_len = {}

# ------------------------------------------------------------------------------

def binary_representation(number, k):
    binary_str = bin(number)[2:]  # Convert to binary and remove the '0b' prefix
    formatted_binary = binary_str.zfill(k)  # Fill with leading zeros to meet the specified length
    return formatted_binary

def inverted_index():
    infile_commandline = sys.argv[1]
    infile = open(infile_commandline, "r")
    global index_dict
    read_infile = infile.read()

    document_split = read_infile.split("\n\n")

    doc_id = 1
    for doc in document_split:

        filtered_doc = ''.join((x for x in doc if not x.isdigit()))
        filtered_doc = filtered_doc.replace("\n", " ")
        filtered_doc = filtered_doc.translate(str.maketrans('', '', string.punctuation))
        filtered_doc = filtered_doc.lower()
        doc_len[doc_id] = len(filtered_doc)
        pos_v = 0
        for term in filtered_doc.split():
            if term in index_dict:
                if doc_id in index_dict[term]:
                    index_dict[term][doc_id].append(pos_v)
                else:
                    index_dict[term][doc_id] = []
                    index_dict[term][doc_id].append(pos_v)
            else:
                doc_id_dict = {}
                doc_id_dict[doc_id] = []
                doc_id_dict[doc_id].append(pos_v)
                index_dict[term] = doc_id_dict

            pos_v += len(term) + 1

        doc_id += 1
        infile.close()

    index_dict = dict(sorted(index_dict.items()))
    dump_txt_file = open(sys.argv[2]+"_dump.txt", "w")
    dump_txt_file.write(json.dumps(index_dict))
    dump_txt_file.close()

    outfile_txt = open(sys.argv[2]+".txt", "w")
    dic_comp = Compressor()
    outfile_dic = open(sys.argv[2]+".dic", "w")
    dic_content = ""
    dic_content = dic_comp.append_gamma(len(doc_len), dic_content)
    m = math.ceil(math.log(max(doc_len.values()), 2))+1
    dic_content = dic_comp.append_gamma(m, dic_content)
    for doc, length in doc_len.items():
        dic_content = dic_comp.append_bits(length, dic_content, m)
    outfile_dic.write(dic_content)
    outfile_dic.close()

    line1 = ""
    line2 = ""
    line3 = ""
    line1_comp = Compressor()
    line2_comp = Compressor()
    line3_comp = Compressor()
    line1_offsets = []
    for term, posting in index_dict.items():
        line1_offsets.append(line2_comp.start_bit_offset)

        num_docs = len(posting)
        adjusted_term = term + '\0'
        line2 += adjusted_term
        line2_comp.start_bit_offset += 8*len(adjusted_term)
        line2 = line2_comp.vbyte_encode(num_docs, line2)
        line2 = line2_comp.vbyte_encode(line3_comp.start_bit_offset, line2)

        m_star = -1 / math.log((1 - num_docs / len(doc_len)), 2) if num_docs < len(doc_len) else 1
        mod = math.ceil(2**math.floor(math.log(m_star, 2))) #choosing appropriate modulus for rice encoding
        line3 = line3_comp.vbyte_encode(num_docs, line3)
        line3 = line3_comp.vbyte_encode(mod, line3)
        freq_doc = [[doc, len(occurences)] for doc,occurences in posting.items()]
        line3 = line3_comp.append_rice_sequence(freq_doc, mod, line3)

    offset_2 = line2_comp.start_bit_offset

    w = math.ceil(math.log(offset_2, 2))+2
    print('offsets: ', line1_offsets)
    for offset in line1_offsets:
        line1 = line1_comp.append_bits(offset, line1, w)
    offset_1 = line1_comp.start_bit_offset

    print(offset_1, offset_2)
    print(w)
    line0 = ""
    line0_comp = Compressor()
    line0 = line0_comp.append_gamma(offset_1, line0)
    line0 = line0_comp.append_gamma(offset_2, line0)
    line0 = line0_comp.append_gamma(w, line0)

    outfile_txt.write(line0)
    outfile_txt.write(line1)
    outfile_txt.write(line2)
    outfile_txt.write(line3)
    outfile_txt.close()

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print("Error: Invalid number of arguments. At least 3 arguements required.")
        print("Here is a sample command \"python index_program.py my_corpus index_file_name\".\n")

    else: 
        inverted_index()
        print(sorted_index_dict)