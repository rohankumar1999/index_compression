import math
import os
import string
import sys
import time


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
vectors = {}            # this is dict of all the vectors of q and doc_id

# ------------------------------------------------------------------------------

"""
Given the above datatype, return the first occurance of a word.
Returns -1 if invalid
"""
def first(term):
    if term in index_dict:   # term exists in dict
        keysList    = list(index_dict[term].keys())     # list of doc_id
        u           = keysList[0]                       # first doc_id
        v           = index_dict[term][u][0]            # first pos
        return [u, v]
    else:               # term not in dict
        return -1

def test_first():
    print("\n\nTesting First:")
    str = "a"
    print(f"\t{str:<15}{first(str)}")
    str = "document"
    print(f"\t{str:<15}{first(str)}")
    return

# ------------------------------------------------------------------------------

"""
Given the above datatype, return the last occurance of a word.
Returns -1 if invalid
"""
def last(term):
    if term in index_dict:   # term exists in dict
        keysList    = list(index_dict[term].keys())         # list of doc_id
        u           = keysList[len(keysList) - 1]           # last doc_id
        list_len    = len(index_dict[term][u])              # len of list of pos
        v           = index_dict[term][u][list_len - 1]     # last pos
        return [u, v]
    else:               # term not in dict
        return -1

def test_last():
    print("\n\nTesting Last:")
    str = "a"
    print(f"\t{str:<15}{last(str)}")
    str = "document"
    print(f"\t{str:<15}{last(str)}")
    str = "first"
    print(f"\t{str:<15}{last(str)}")
    return

# ------------------------------------------------------------------------------

"""
Given a word and the current document as well as position
this returns the next occurance of a word.
Returns -1 if invalid
"""
def next(term, current_doc_id, current_pos):
    for doc_id, positions in index_dict.get(term, {}).items():
        if doc_id == current_doc_id:
            for position in positions:
                if position > current_pos:
                    return [doc_id, position]
        elif doc_id > current_doc_id:
            if positions:
                return [doc_id, positions[0]]
    return -1

def test_next():
    print("\n\nTesting Next:")
    str = "a"
    print(f"\t{str:<15}{next(str,1, 8)}")
    str = "document"
    print(f"\t{str:<15}{next(str,1, 16)}")
    str = "first"
    print(f"\t{str:<15}{next(str,1, 10)}")
    return

# ------------------------------------------------------------------------------

"""
Given a word and the current document as well as position
this returns the previous occurance of a word.
Returns -1 if invalid
"""
def prev(term, current_doc_id, current_pos):
    if term in index_dict:
        if current_doc_id in index_dict[term]:
            positions = index_dict[term][current_doc_id]
            for i in range(len(positions)-1, -1, -1):
                if positions[i] < current_pos:
                    return [current_doc_id, positions[i]]
        prev_doc_id = max([doc_id for doc_id in index_dict[term].keys() if doc_id < current_doc_id], default=None)
        if prev_doc_id is not None:
            return [prev_doc_id, max(index_dict[term][prev_doc_id])]
    return -1

def test_prev():
    print("\n\nTesting Previous:")
    str = "a"
    print(f"\t{str:<15}{prev(str, 3, 0)}")
    str = "document"
    print(f"\t{str:<15}{prev(str, 2, 15)}")
    str = "first"
    print(f"\t{str:<15}{prev(str, 3, 40)}")
    str = "line"
    print(f"\t{str:<15}{prev(str, 3, 32)}")
    return

# ------------------------------------------------------------------------------

"""
You should first modify the pseudo-code of nextPhrase, the input remains a
sequence of terms t[1],...,t[n] and a position, for example, "The", "quick",
"brown", "fox", 57. Now, however, we assume first, next, prev, last, operate
on an inverted index as described above, and that positions are pairs u:v where
u is a doc_id and v is a character offset into the document where strings of
only whitespace, punctuation, numbers, etc. are treated as in Hw1 (So "Hi9..
There" would be converted to "hi there" before additional processing). Put
pseudo-code for this revised nextPhrase in a file next_phrase.txt that submit
along with the homework.
"""
def next_phrase(terms, position):
    u1, v1 = position

    for term in terms:  # iterate through terms
        result = next(term, u1, v1)     # get loction of next term
        if result == -1:                # no next term --> terminate
            return (float('inf'), float('inf'))
        if result[0] > u1:              # term is in new doc --> terminate
            return (float('inf'), float('inf'))
        u1, v1 = result

    u2, v2 = u1, v1

    for i in range(len(terms)-2, -1, -1):
        u2, v2 = prev(terms[i], u2, v2)
        v1 += len(terms[-1])

    if (u1 == u2 and v1 - v2 == sum(len(term) + 1 for term in terms)-1): # valid
        return ((u2, v2), (u1, v1))
    else:   # invalid --> keep searching
        return next_phrase(terms, (u2, v2))

def test_next_phrase():
    print("\n\nTesting Next Phrase:")
    terms       = ["first", "line"]
    position    = (3, 0)  # Assuming starting position is (doc_id, offset)
    result      = next_phrase(terms, position)
    print(f"\tTerms: {terms}")
    print(f"\tStarting Position: {position}")
    print(f"\tResult: {result}")
    return

# ------------------------------------------------------------------------------

"""
This is identical to our above implementation of next_phrase but reverse.
It uses swaps the uses of prev and next and iterates in reverse. Otherwise the
underlying psuedocode is nearly identical.
"""
def prev_phrase(terms, position):
    u1, v1 = position
    t = terms.copy()    # make copy so we aren't editting the og list
    t.reverse()         # reverse list since we are starting at the back

    for term in t:  # iterate through terms
        result = prev(term, u1, v1)     # get loction of prev term
        if result == -1:                # no next term --> terminate
            return (float('inf'), float('inf'))
        if result[0] > u1:              # term is in new doc --> terminate
            return (float('inf'), float('inf'))
        u1, v1 = result

    u2, v2 = u1, v1

    for i in range(len(t)-2, -1, -1):
        u2, v2 = next(t[i], u2, v2)
        v2 += len(t[i])

    if (u1 == u2 and v2 - v1 == sum(len(term) + 1 for term in t)-1): # valid
        return ((u1, v1), (u2, v2))
    else:   # invalid --> keep searching
        return prev_phrase(terms, (u2, v2)) # note og list "terms" not "t"

def test_prev_phrase():
    print("\n\nTesting Prev Phrase:")
    terms       = ["first", "line"]
    position    = (3, 0)  # Assuming starting position is (doc_id, offset)
    result      = prev_phrase(terms, position)
    print(f"\tTerms: {terms}")
    print(f"\tStarting Position: {position}")
    print(f"\tResult: {result}")

    terms       = ["first", "line"]
    position    = (3, 40)  # Assuming starting position is (doc_id, offset)
    result      = prev_phrase(terms, position)
    print(f"\n\tTerms: {terms}")
    print(f"\tStarting Position: {position}")
    print(f"\tResult: {result}")
    return

# ------------------------------------------------------------------------------

"""
docRight is based off our psuedocode in positive.txt. It returns the next
occurance of a term or phrase in a next document.
"""
def doc_right(terms, position):
    if type(terms) == str:      # single term
        [u, v] = position
        result = next(terms, u+1, 0)
        return result
    elif type(terms) == list:   # phrase (list of str)
        [u, v] = position
        result = next_phrase(terms, [u+1, 0])
        return result
    else:                       # error, not a str or phrase (list of str)
        return -1

def test_doc_right():
    print("\n\nTesting doc_right:")
    terms       = "first"
    position    = (0, 0)
    result      = doc_right(terms, position)
    print(f"\tTerms: {terms}")
    print(f"\tStarting Position: {position}")
    print(f"\tResult: {result}")

    terms       = "first"
    position    = result
    result      = doc_right(terms, position)
    print(f"\n\tTerms: {terms}")
    print(f"\tStarting Position: {position}")
    print(f"\tResult: {result}")

    terms       = "next"
    position    = (0, 0)
    result      = doc_right(terms, position)
    print(f"\n\tTerms: {terms}")
    print(f"\tStarting Position: {position}")
    print(f"\tResult: {result}")

    terms       = ["first", "document"]
    position    = (0, 0)
    result      = doc_right(terms, position)
    print(f"\n\tTerms: {terms}")
    print(f"\tStarting Position: {position}")
    print(f"\tResult: {result}")
    return

# ------------------------------------------------------------------------------

"""
docLeft is based off our psuedocode in positive.txt. It returns the prev
occurance of a term or phrase in a prev document.
"""
def doc_left(terms, position):
    if type(terms) == str:      # single term
        [u, v] = position
        if (u > 1):
            l = doc_len[u-1]
            result = prev(terms, u-1, l)
            return result
        else:
            return -1
    elif type(terms) == list:   # phrase (list of str)
        [u, v] = position
        if (u > 1):
            l = doc_len[u-1]
            result = prev_phrase(terms, [u-1, l])
            return result
        else:
            return -1
    else:                       # error, not a str or phrase (list of str)
        return -1

def test_doc_left():
    print("\n\nTesting doc_left:")
    terms       = "first"
    position    = (0, 0)
    result      = doc_left(terms, position)
    print(f"\tTerms: {terms}")
    print(f"\tStarting Position: {position}")
    print(f"\tResult: {result}")

    terms       = "first"
    position    = (2, 0)
    result      = doc_left(terms, position)
    print(f"\n\tTerms: {terms}")
    print(f"\tStarting Position: {position}")
    print(f"\tResult: {result}")

    terms       = "next"
    position    = (4, 0)
    result      = doc_left(terms, position)
    print(f"\n\tTerms: {terms}")
    print(f"\tStarting Position: {position}")
    print(f"\tResult: {result}")

    terms       = ["first", "document"]
    position    = (3, doc_len[3])
    result      = doc_left(terms, position)
    print(f"\n\tTerms: {terms}")
    print(f"\tStarting Position: {position}")
    print(f"\tResult: {result}")

    terms       = ["first", "line"]
    position    = (4, 0)
    result      = doc_left(terms, position)
    print(f"\n\tTerms: {terms}")
    print(f"\tStarting Position: {position}")
    print(f"\tResult: {result}")
    return

# ------------------------------------------------------------------------------

"""
Dot product used to calculate cosine similarity between two functions.
Code borrowed from https://iq.opengenus.org/dot-product-in-python/
"""
def dot_product(vector1, vector2):
    if len(vector1) != len(vector2):
        raise ValueError("Vectors must have the same length")

    # Calculate the dot product
    dp = 0
    for i in range(len(vector1)):
        dp += vector1[i] * vector2[i]

    return dp

# ------------------------------------------------------------------------------

"""
A function to normalize vectors before we take their cosine similarity.
"""
def normalize(vector):
    magnitude = math.sqrt(sum(pow(element, 2) for element in vector))
    if magnitude > 0:
        normal = [i/magnitude for i in vector]
        return normal
    else:
        return vector

# ------------------------------------------------------------------------------

"""
This is a collection of commands that prints information inputted, created,
stored, etc by this program. It is meant to help with debugging.
"""
def print_commandline_args():
    print('\nNumber of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))
    return

def print_index_list():
    print("\n\nDict:")
    for key in index_dict:
        print (f"{key:<20}{index_dict[key]}")
    return

def print_sorted_index_list():
    print("\n\nAlphabetical Posting List:")
    for key in sorted_index_dict:
        print (f"{key:<20}{sorted_index_dict[key]}")
    return

def print_doc_len():
    print("\n\nLength of Every Doc:")
    for key in doc_len:
        print (f"{key:<5}{doc_len[key]}")
    return

def print_vectors():
    print("\n\nVectors List:")
    for key in vectors:
        print (f"{key:<7}{vectors[key]}")
    return

# ------------------------------------------------------------------------------

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

    return

# ------------------------------------------------------------------------------

"""

"""
def term_rank():
    num_results         = int(sys.argv[2])  # num_results of output table (k)
    num_acc             = int(sys.argv[3])  # number of acc to limit (limits num of doc)
    unfiltered_query    = sys.argv[4:]      # query starts at 3rd cmdline arg and onwards
    query               = []                # actual query var
    N                   = len(doc_len)      # N, document count
    start_time          = time.perf_counter()
    rel_measure = 'DFR'

    # calulcate the average doc length (l_avg)
    sum_len = 0
    for key in doc_len:
        sum_len += key
    l_avg = sum_len / len(doc_len)              # average length of docs in corpus

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

        """
        # test prints
        print_index_list()
        print_sorted_index_list()
        print_doc_len()
        #print_vectors()


        # tests
        test_first()
        test_last()
        test_next()
        test_prev()
        test_next_phrase()
        test_prev_phrase()
        test_doc_right()
        test_doc_left()
        """
