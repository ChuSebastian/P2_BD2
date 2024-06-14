# Modulo que implementara el algoritmo SPIMI: Indice invertido en bloques, escribiendolo en disco y fusionandolo.
'''
SPIMI_Invert(token_stream):
    output_file = NEWFILE()
    dictionary = NEWHASH()
    while (free memory avaible):
    do token = next(token_stream)
        if term(token) not in dictionary:
            then posting_list = AddToDictionary(dictionary,term(token))
            else posting_list = GetPostingsList(dictionary,term(token))
        if full (postings_list):
            then postings_list = DoublePostingsList(dictionary,term(token))
        AddToPostingsList(posting_list,docID(token))
    sorted_terms = SortTerms(dictionary)
    WriteBlockToDisk(sorted_terms,dictionary,output_file)
    return output_file
'''