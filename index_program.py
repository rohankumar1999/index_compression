import math
import os
import string
import sys
import heapq
import time
from utils import Compressor
"""
DATA STRUCTURE EXPLAINED
For this project, we are storing a posting list of terms as a nested dictionary
with the format of key:key:list such that:
    {term: {docid:[pos1, pos2, ... , pos_n] } }
All of the functions assume this prequisite datatype
"""
# the dicitonary will have the format { term:{u:[v1v2:vn], u:vn, u:vn} }
index_dict = {}         # create dicitonary that will serve as our index
sorted_index_dict = {}  # this is the alphabetically sorted version of the above
doc_len = {}            # this dictionary stores the length of docs by doc_id

# ------------------------------------------------------------------------------

def binary_representation(number, k):
    binary_str = bin(number)[2:]  # Convert to binary and remove the '0b' prefix
    formatted_binary = binary_str.zfill(k)  # Fill with leading zeros to meet the specified length
    return formatted_binary

"""
This is the function that creates our inverted_index and stores it in the
variable: index_dict. Be sure to run this function first in main in order to
properly read in files and create the index.
"""
def inverted_index():
    infile_commandline = sys.argv[1]
    infile = open(infile_commandline, "r")
    global index_dict
    read_infile = infile.read()

    # split infile into "documents" denoted by "\n\n"
    document_split = read_infile.split("\n\n")

    doc_id = 1  # keeps track of doc_id (u)
    for doc in document_split:

        # filtering the documents
        filtered_doc = ''.join((x for x in doc if not x.isdigit()))                         # remove digits
        filtered_doc = filtered_doc.replace("\n", " ")                                      # remove newline
        filtered_doc = filtered_doc.translate(str.maketrans('', '', string.punctuation))    # remove punctuation
        filtered_doc = filtered_doc.lower()                                                 # make everything lowercase

        doc_len[doc_id] = len(filtered_doc)

        # creating the index / filling the dictionary
        # filter through terms of a doc and add them to dictionary
        pos_v = 0  # keeps track of positions (v)
        for term in filtered_doc.split():
            # term exists in dictionary
            if term in index_dict:
                # term has a list for the doc_id
                if doc_id in index_dict[term]:
                    index_dict[term][doc_id].append(pos_v)
                # term DOES NOT have a list for the doc_id
                else:
                    index_dict[term][doc_id] = []   # create list of pos (v)
                    index_dict[term][doc_id].append(pos_v)
            # term does not exist in dictionary
            else:
                doc_id_dict = {}    # create a doc_id dict at term (same as index_dict[term])
                doc_id_dict[doc_id] = []    # create list of pos (v)
                doc_id_dict[doc_id].append(pos_v)
                index_dict[term] = doc_id_dict

            pos_v += len(term) + 1  # increment pos (v) by term len + 1 space

        doc_id += 1     # increment doc_id (u)
        infile.close()  # close infile

    index_dict = dict(sorted(index_dict.items()))
    


    outfile_txt = open(sys.argv[2]+".txt", "w")
    #items to be compressed
    #writing to outfile_dic
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

        mod = 2
        line3 = line3_comp.vbyte_encode(num_docs, line3)
        line3 = line3_comp.vbyte_encode(mod, line3)
        # for doc, occurences in posting.items():
            # line3 = line3_comp.append_gamma(len(occurences), line3)
            # line3 = line3_comp.append_rice_sequence(occurences, mod, line3, -1)
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

    # print(line1)
    # print(repr(line2))
    # print("\n\n")
    # print(repr(line3))

## 2,7,5,<1,5,6,8,9>,4,<1,4,5,6>

    # #writing to outfile_txt
    # outfile_txt = open(sys.argv[2]+".txt", "w")
    # # offset_1 = 0
    # # offset_2 = 0
    # # outfile_txt.write(offset_1)
    # # outfile_txt.write(offset_2)
    # max_int_offset = sum([len(x)+8+8 for x in index_dict.keys()]) #sum of all tuple lengths in second line len(term)+len(vByte(posting len))+len(vByte(offset))
    # w = math.ceil(math.log(max_int_offset,2))
    # outfile_txt.write(utils.gamma_encode(w))

    outfile_txt.write(line0)
    outfile_txt.write(line1)
    outfile_txt.write(line2)
    outfile_txt.write(line3)
    outfile_txt.close()
    
        
    

    ######integer offsets into term, num_docs_with_term, offset tuple list######



    ############################################################################

    ######list of term, vByte number of documents containing the term, vByte coded posting list offset tuples######



    ############################################################################

    ######posting lists in format: γ-encoded number of documents containing the term, followed by a modulus to use with a Rice code for posting gaps, followed by a sequence of γ-encoded frequency of term in doc, Rice coded gap from previous docs pairs (where the modulus used is the one at the start of the posting list).######



    ############################################################################

    return

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    # check for valid command line arguments
    # print_commandline_args()
    if (len(sys.argv) < 4):     # invalid numb of commandline args
        print("Error: Invalid number of arguments. At least 4 arguements required.")
        print("Here is a sample command \"python ConjunctiveRank.py my_corpus 5 good_dog bad cat\".\n")

    else:                       # valid numb of commandline args exist
        # create inverted index
        inverted_index()
        print(sorted_index_dict)