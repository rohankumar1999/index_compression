import math
import os
import string
import sys
import heapq
import time
from utils import Compressor

def term_rank():
    #items to be de-compressed:
    doc_len = {}
    with open(sys.argv[1]+".dic", 'rb') as infile_dic:
        dic_file = infile_dic.read().decode('utf-8')
        dic_comp = Compressor()
        num_docs = dic_comp.decode_gamma_list(dic_file,1)[0]
        m = dic_comp.decode_gamma_list(dic_file, 1)[0]
        for i in range(num_docs):
            doc_len[i] = dic_comp.decode_bits(dic_file, m)
    # return
    index_dict = {}
    with open(sys.argv[1]+".txt", 'rb') as infile_txt:
        txt_file = infile_txt.read().decode('utf-8')
        txt_comp = Compressor()
        import pdb;pdb.set_trace()
        offset_1,offset_2 = txt_comp.decode_gamma_list(txt_file,2)
        w = txt_comp.decode_gamma_list(txt_file, 1)[0]
        print('here', offset_1, offset_2, w)
        line1_start_offset = txt_comp.start_bit_offset
        temp = []
        while txt_comp.start_bit_offset - line1_start_offset <= offset_1:
            offset = txt_comp.decode_bits(txt_file, w)
            temp.append(offset)
        print(temp)
    # return

    ############################

    num_results         = 10  # num_results of output table (k)
    num_acc             = 10  # number of acc to limit (limits num of doc)
    unfiltered_query    = sys.argv[2:-1]      # query starts at 3rd cmdline arg and onwards
    query               = []                # actual query var
    N                   = len(doc_len)      # N, document count
    start_time          = time.perf_counter()
    rel_measure = sys.argv[-1]


    # calulcate the average doc length (l_avg)
    sum = 0
    for key in doc_len:
        sum += key
    l_avg = sum / len(doc_len)              # average length of docs in corpus

    # remove duplicate terms from query
    query = unfiltered_query[0]
    query = query.split(" ")

    q_copy = query

    # remove q terms not in index
    query = list(filter(lambda x: x in index_dict, query))
    query = list(query)

    # pre-calculate idf scores
    idf_values = {}
    for q in query:
        # calculate idf
        N_t = len(index_dict[q])    # item exists, thus len > 0
        idf = math.log(N / N_t, 2)  # idf, inverted term frequency (global)
        idf_values[q] = idf


    # sort query vec by increasing order of N[t(i)]
    query = sorted(query, key=lambda x: len(index_dict[x]))

    # initialize accumulator
    acc = {}

    # iterate through terms in query
    quit = False
    for q in query:
        if quit == True:    # QUIT STRATEGY
            break

        posting_list = index_dict[q]
        for doc_id in posting_list.keys():  # go through term posting list

            # ------------------------------------- #
            # doc_id already has an accumulator     #
            # ------------------------------------- #
            if doc_id in acc:
                f_td    = len(index_dict[q][doc_id])    # number of occurrences in doc
                l_d     = doc_len[doc_id]               # length of doc
                lam = 0.5
                q_t = 1 # we compute score for each occurence of term separately
                l_C = sum(doc_len.values())
                l_t = len(index_dict[q].keys())
                N = len(doc_len.keys())
                if rel_measure == 'LMJM':
                    LMJM = q_t * math.log(1 + ((1-lam)/lam) * (f_td/l_d) * (l_C/l_t), 2)
                    acc[doc_id] += LMJM
                else:
                    DFR = q_t * (math.log(1 + (l_t / N)) + (f_td * math.log(1 + (N / l_t)))) / (f_td + 1)
                    acc[doc_id] += DFR

            # ---------------------------------------------- #
            # doc_id does not have an accumulator, make one  #
            # ---------------------------------------------- #
            else:
                if len(acc) >= num_acc: # no more room, QUIT
                    quit = True
                    break
                else:   # more room, create acc
                    acc[doc_id] = 0
                    f_td    = len(index_dict[q][doc_id])    # number of occurrences in doc
                    l_d     = doc_len[doc_id]               # length of doc
                    lam = 0.5
                    q_t = 1 # we compute score for each occurence of term separately
                    l_C = sum(doc_len.values())
                    l_t = len(index_dict[q].keys())
                    N = len(doc_len.keys())
                    if rel_measure == 'LMJM':
                        LMJM = q_t * math.log(1 + ((1-lam)/lam) * (f_td/l_d) * (l_C/l_t), 2)
                        acc[doc_id] += LMJM
                    else:
                        DFR = q_t * (math.log(1 + (l_t / N)) + (f_td * math.log(1 + (N / l_t)))) / (f_td + 1)
                        acc[doc_id] += DFR
                    


        else:   # no term in index
            pass    # do nothing since not in index


    # sort ACC by value
    acc = dict(sorted(acc.items(), key=lambda item: item[1], reverse=True))

    # end timer
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time} seconds")

    # display acc
    print("Doc\tScore")
    l = list(acc.keys())
    for k in l[:num_results]:   # retun top k results
        print(f"{k}\t{acc[k]}")

    # make sure all k results are properly 
    if (len(acc) < num_results):
        i = num_results - len(acc)
        for d in doc_len.keys():
            if i == 0:
                break
            if d not in acc:
                print(f"{d}\t{0}")
                i -= 1

    # Print to outfile
    outfile = open("trec_top_file.txt", "w")

    query_id = 0
    for q in q_copy:
        for char in q:
            query_id += ord(char)

    for d in doc_len.keys():
        s = 0
        if d in acc:
            s = acc[d]
        string = f"{query_id} 0 DOC-{d:04d} 1 {s} term_time"
        outfile.write(string)
        outfile.write("\n")

    # close outfile
    outfile.close()

    return

if __name__ == "__main__":
    term_rank()