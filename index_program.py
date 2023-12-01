import math
import os
import string
import sys
import heapq
import time
import utils
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

    # sort the dictionary by alphabetical order
    global sorted_index_dict    # need to specify we are editing the global (idk why we just do or else it doesnt work)
    sorted_index_dict = {k: v for k, v in sorted(index_dict.items(), key=lambda item: item[0])}
    


    outfile_txt = open(sys.argv[2]+".txt", "w")
    #items to be compressed
    #writing to outfile_dic
    outfile_dic = open(sys.argv[2]+".dic", "w")
    outfile_dic.write(utils.gamma_encode(len(doc_len)))
    # outfile_dic.write("\n")
    print(max(doc_len.values()))
    m = math.ceil(math.log(max(doc_len.values()), 2))
    outfile_dic.write(utils.gamma_encode(m))
    # outfile_dic.write("\n")
    for doc, length in doc_len.items():
        outfile_dic.write(binary_representation(length, m))
        # outfile_dic.write("\n")
    outfile_dic.close()

    #writing to outfile_txt
    outfile_txt = open(sys.argv[2]+".txt", "w")
    # offset_1 = 0
    # offset_2 = 0
    # outfile_txt.write(offset_1)
    # outfile_txt.write(offset_2)
    max_int_offset = sum([len(x)+8+8 for x in index_dict.keys()]) #sum of all tuple lengths in second line len(term)+len(vByte(posting len))+len(vByte(offset))
    w = math.ceil(math.log(w,2))
    outfile_txt.write(utils.gamma_encode(w))
    line1 = ""
    idx = 0
    for word in index_dict.keys():
        line1 += ("0"*w+str(idx))[-w:]
        idx += (len(word)+16)
    line2 = ""
    pos=0
    line3 = ""
    for word,occurences in index_dict.items():
        line2 += word
        line2 += ("00000000"+str(pos))[-8:]
        pos += 2*len(docs)
        for doc in docs:
            line3+=(str(doc)+',')
    line3 = line3[:-1]
    

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