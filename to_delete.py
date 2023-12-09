import math
import os
import string
import sys
import time


index_dict = {}
sorted_index_dict = {}
doc_len = {}
vectors = {}
c = {}
c_prev = {}
infty = 9999999999999999


l = {}
P = {}
    
def binarySearch(arr, low, high, x):
    while low < high:
        mid = low + (high - low) // 2
        if arr[mid][0] < x[0] or (arr[mid][0] == x[0] and arr[mid][1] <= x[1]):
            low = mid + 1
        else:
            high = mid
    return low

def binarySearch_2(arr, low, high, x):
    arr = arr[::-1]
    arr = [(-x, -y) for x,y in arr]
    x = [-x[0], -x[1]]
    low = len(arr)-1-low
    high = len(arr)-1-high
    return len(arr)-1-binarySearch(arr, high, low, x)


def next(t, current):
    c = {}
    if t not in c.keys():
        c[t] = 0
    if l[t] == 0 or P[t][l[t]-1] <= current:
        return [infty, infty]
    if P[t][0] > current:
        c[t] = 0
        return P[t][c[t]]
    if c[t] > 0 and P[t][c[t]-1] <= current :
        low = c[t] 
    else:
        low = 0

    jump = 1
    high = low + jump
    while high < l[t] and P[t][high] <= current: 
        low = high
        jump = 2*jump
        high = low + jump
    if high > l[t]:
        high = l[t]
    c[t] = binarySearch(P[t], low, high, current)
    return P[t][c[t]]

def prev(t, current):
    c_prev = {}
    if t not in c_prev.keys():
        c_prev[t] = l[t]
    if l[t] == 0 or P[t][0] >= current:
        return [-infty, -infty]
    if P[t][l[t]-1] < current:
        c_prev[t] = l[t]-1
        return P[t][c_prev[t]]
    if c_prev[t] < l[t] and P[t][c_prev[t]-1] >= current :
        high = c_prev[t] 
    else:
        high = l[t]-1

    jump = -1
    low = high + jump
    while low >=0 and P[t][low] >= current: 
        high=low
        jump = 2*jump
        low = high + jump
    if low < 0:
        low = 0
    c_prev[t] = binarySearch_2(P[t], low, high, current)
    return P[t][c_prev[t]]

def first(t):
    return next(t, [-infty, -infty])

def last(t):
    return prev(t, [infty, infty])

def nextPhrase(t, position):
    v = position
    n = len(t)
    for i in range(n):
        v = next(t[i], v)
    if v[0] == infty :
        return [[infty, infty], [infty, infty]]
    u = v
    for i in reversed(range(n-1)):
        u = prev(t[i],u)
    
    if v[0]==u[0] and v[1]-u[1] == n - 1:
        return [u, v]
    else:
        return nextPhrase(t, u)

def prevPhrase(t, position):
    v = position
    n = len(t)
    for i in reversed(range(n)):
        v = prev(t[i], v)
    if v[0] == -infty :
        return [[-infty, -infty], [-infty, -infty]]
    u = v
    for i in range(1, n):
        u = next(t[i],u)
    
    if v[0]==u[0] and u[1]-v[1] == n - 1:
        return [v, u]
    else:
        return prevPhrase(t, u)

def docRight(Q, u):
    return max([nextPhrase(x.split('_'), u)[0][0] for x in Q])

def docLeft(Q, u):
    return min([prevPhrase(x.split('_'), u)[0][0] for x in Q])

def nextSolution(Q, position):
    v = docRight(Q, position)
    if v == infty:
        return infty
    u = docLeft(Q, [v+1, -infty])
    if u == v:
        return u
    else:
        return nextSolution(Q, [v, -infty])

def allSolutions(Q):
    solutions = []
    u =  -infty
    while u < infty:
        u = nextSolution(Q, [u,-infty])
        if len(solutions) and solutions[-1] == u:
            u +=1
            continue
        if u < infty :
            solutions.append(u)
    return solutions


def inverted_index():
    infile_commandline = sys.argv[1]
    infile = open(infile_commandline, "r")

    read_infile = infile.read()

    document_split = read_infile.split("\n\n")

    doc_id = 1
    for doc in document_split:

        filtered_doc = ''.join((x for x in doc if not x.isdigit()))                         # remove digits
        filtered_doc = filtered_doc.replace("\n", " ")                                      # remove newline
        filtered_doc = filtered_doc.translate(str.maketrans('', '', string.punctuation))    # remove punctuation
        filtered_doc = filtered_doc.lower()                                                 # make everything lowercase

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

    global sorted_index_dict
    sorted_index_dict = {k: v for k, v in sorted(index_dict.items(), key=lambda item: item[0])}
    global P
    global l
    for term, postings in sorted_index_dict.items():
        for doc_id, occurences in postings.items():
            for occurence in occurences:
                P[term] = [[doc_id, occurence]] if not P.get(term) else P[term] + [[doc_id, occurence]]
    
    for key in P.keys():
        l[key] = len(P[key])

    return

def term_rank():
    num_results         = int(sys.argv[2])
    num_acc             = int(sys.argv[3])
    unfiltered_query    = sys.argv[4:]
    query               = []
    N                   = len(doc_len)
    start_time          = time.perf_counter()
    rel_measure = sys.argv[-1]
    sum_len = 0
    for key in doc_len:
        sum_len += key
    l_avg = sum_len / len(doc_len)

    query = unfiltered_query[0]
    query = query.split(" ")

    # get docs containing all query terms (conjunctive query)
    filtered_docs = allSolutions(query)
    print(filtered_docs)
    q_copy = query

    query = list(filter(lambda x: x in index_dict, query))
    query = list(query)

    idf_values = {}
    for q in query:
        N_t = len(index_dict[q])
        idf = math.log(N / N_t, 2)
        idf_values[q] = idf


    query = sorted(query, key=lambda x: len(index_dict[x]))

    acc = {}

    quit = False
    for q in query:
        if quit == True:
            break

        posting_list = index_dict[q]
        for doc_id in posting_list.keys():
            if not doc_id in filtered_docs:
                continue
            if doc_id in acc:
                f_td    = len(index_dict[q][doc_id])
                l_d     = doc_len[doc_id]
                lam = 0.5
                q_t = 1
                l_C = sum(doc_len.values())
                l_t = len(index_dict[q].keys())
                N = len(doc_len.keys())
                if rel_measure == 'LMJM':
                    LMJM = q_t * math.log(1 + ((1-lam)/lam) * (f_td/l_d) * (l_C/l_t), 2)
                    acc[doc_id] += LMJM
                else:
                    DFR = q_t * (math.log(1 + (l_t / N)) + (f_td * math.log(1 + (N / l_t)))) / (f_td + 1)
                    acc[doc_id] += DFR

            else:
                if len(acc) >= num_acc:
                    quit = True
                    break
                else:
                    acc[doc_id] = 0
                    f_td    = len(index_dict[q][doc_id])
                    l_d     = doc_len[doc_id]
                    lam = 0.5
                    q_t = 1
                    l_C = sum(doc_len.values())
                    l_t = len(index_dict[q].keys())
                    N = len(doc_len.keys())
                    if rel_measure == 'LMJM':
                        LMJM = q_t * math.log(1 + ((1-lam)/lam) * (f_td/l_d) * (l_C/l_t), 2)
                        acc[doc_id] += LMJM
                    else:
                        DFR = q_t * (math.log(1 + (l_t / N)) + (f_td * math.log(1 + (N / l_t)))) / (f_td + 1)
                        acc[doc_id] += DFR


        else:
            pass


    acc = dict(sorted(acc.items(), key=lambda item: item[1], reverse=True))

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time} seconds")

    print("Doc\tScore")
    l = list(acc.keys())
    for k in l[:num_results]:
        print(f"{k}\t{acc[k]}")

    if (len(acc) < num_results):
        i = num_results - len(acc)
        for d in doc_len.keys():
            if i == 0:
                break
            if d not in acc:
                print(f"{d}\t{0}")
                i -= 1

    join_q = '_'.join(query)
    outfile = open(f"trec_top_file_{join_q}_{rel_measure}.txt", "w")

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
    outfile.close()

    return

# ------------------------------------------------------------------------------

"""
Our main(). Runs all of the other functions.
"""
if __name__ == "__main__":
    # check for valid command line arguments
    # print_commandline_args()
    if (len(sys.argv) < 4):     # invalid numb of commandline args
        print("Error: Invalid number of arguments. At least 4 arguements required.")
        print("Here is a sample command \"python ConjunctiveRank.py my_corpus 5 good_dog bad cat\".\n")

    else:                       # valid numb of commandline args exist
        # create inverted index
        inverted_index()
        term_rank()
