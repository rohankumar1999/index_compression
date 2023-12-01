import math
import os
import string
import sys
import heapq
import time

def term_rank():
    #items to be de-compressed:
    doc_len = {}
    index_dict = {}
    ############################

    num_results         = int(sys.argv[2])  # num_results of output table (k)
    num_acc             = int(sys.argv[3])  # number of acc to limit (limits num of doc)
    unfiltered_query    = sys.argv[4:]      # query starts at 3rd cmdline arg and onwards
    query               = []                # actual query var
    N                   = len(doc_len)      # N, document count
    start_time          = time.perf_counter()


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
                idf     = idf_values[q]
                TF_BM25 = (f_td * (2.2)) / (f_td + (1.2 * ((1 - 0.75) + (0.75 * (l_d / l_avg)))))
                score   = idf * TF_BM25
                acc[doc_id] += score

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
                    idf     = idf_values[q]
                    TF_BM25 = (f_td * (2.2)) / (f_td + (1.2 * ((1 - 0.75) + (0.75 * (l_d / l_avg)))))
                    score   = idf * TF_BM25
                    acc[doc_id] += score


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
    term_rank