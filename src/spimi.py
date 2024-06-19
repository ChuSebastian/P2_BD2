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

BSBIndexConstruction():
    n = 0
    while (all documents have not been processed):
    do
        n = n + 1
        token_stream = parseDocs()
        fn = SPIMI_Invert(token_stream)
    MergeBlocks(f1,...,fn;f_merged)
'''

import sys
from utils import MinHeap
from ast import literal_eval
from typing import List, Tuple, TextIO, Optional

class SPIMI:
    def __init__(self, block_limit, stop_words):
        self.block_limit = block_limit
        self.stop_words = stop_words
        self.index_file_name = "data/results/merged_index.txt"
        
    def WriteBlockToDisk(self, dictionary, prefix, block_n):
        
        file_name = f"data/blocks/{prefix}_{block_n}.txt"
        with open(file_name, "w") as f:
            sorted_terms = sorted(dictionary.items())
            for term, postings in sorted_terms:
                f.write(f"('{term}', {postings})\n")
        return file_name

    # token_stream: [(term1,termID1,freq1),
                #    (term2,termID2,freq2)...]
    # dictionary = tenemos que generar con el spimi 
                # {term1 ,  [(termID1, freq1),(termID2, freq2)],
                #    term2 ,  [(termID3, freq3),(termID4, freq4)],
                #    ... }

    def spimi_invert(self, block_n, token_stream_file):
        dictionary = {}
        block_list = []

        while sys.getsizeof(dictionary) <= self.block_limit:
            line = token_stream_file.readline()
            if not line:
                break
            term, track_id, freq = literal_eval(line.strip())
            if term not in dictionary:
                dictionary[term] = [(track_id, freq)]
            else:
                postings_list = dictionary[term]
                if postings_list[-1][0] == track_id:
                    postings_list[-1] = (track_id, postings_list[-1][1] + freq)
                else:
                    postings_list.append((track_id, freq))
                dictionary[term] = postings_list

        block_list.append(self.WriteBlockToDisk(dictionary, "block", block_n))
        return block_list
    
    def merge_blocks(self, blocks: List[str]) -> None:
        outfile = open(self.index_file_name, "w")
        min_heap = MinHeap[Tuple[str, int, List[Tuple[str, int]]]]()
        block_files: List[TextIO] = []

        for i in range(len(blocks)):
            block_files.append(open("data/blocks/"+blocks[i]))
            min_term_tuple = literal_eval(block_files[i].readline())
            min_heap.push((min_term_tuple[0], i, min_term_tuple[1]))

        last_min_term: Optional[Tuple[str, int, List[Tuple[str, int]]]] = None
        while not min_heap.empty():
            min_term_tuple = min_heap.pop()
            if last_min_term and last_min_term[0] == min_term_tuple[0]:
                last_min_term[2].extend(min_term_tuple[2])
            else:
                if last_min_term is not None:
                    term = (last_min_term[0], last_min_term[2])
                    outfile.write(str(term) + "\n")
                last_min_term = min_term_tuple

            i = min_term_tuple[1]
            line = block_files[i].readline().strip()
            if line:
                next_min_term_tuple = literal_eval(line)
                min_heap.push((next_min_term_tuple[0], i, next_min_term_tuple[1]))

        if last_min_term:
            term = (last_min_term[0], last_min_term[2])
            outfile.write(str(term) + "\n")

        outfile.close()
        for f in block_files:
            f.close()
            
    def _spimi_index_construction(self) -> None:
        n = 0
        with open(self.token_stream_file_name, mode="r") as token_stream_file:
            last_pos = token_stream_file.tell()
            line = token_stream_file.readline().strip()
            blocks = []
            while line != '':
                token_stream_file.seek(last_pos)
                n += 1
                blocks.append(f"block_{n}.txt")
                self.spimi_invert(n, token_stream_file)
                last_pos = token_stream_file.tell()
                line = token_stream_file.readline().strip()
            
            # Mostrar el contenido de los archivos de bloques generados
            #print("Archivos de bloques generados:", blocks)
            #for file_name in blocks:
            #    with open(file_name, "r") as f:
            #        print(f"Contenido de {file_name}:\n{f.read()}")
            
            self.merge_blocks(blocks)

    def create(self, token_stream_file_name):
        self.token_stream_file_name = token_stream_file_name
        self._spimi_index_construction()