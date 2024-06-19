# construccion del indice invertido
import os
from spimi import SPIMI
from preprocessing import preprocessing,preprocessing_content
import ast
import numpy as np
import struct

class IndexInverted:
    def __init__(self, file_name_data, number_of_documents, block_limit=200000, stop_words=True):
        self.file_name_data = file_name_data
        self.number_of_documents = number_of_documents
        self.block_limit = block_limit
        self.stop_words = stop_words
        self.index = {}

    def create_index_inverted(self):
        spimi = SPIMI(block_limit=self.block_limit, stop_words=self.stop_words)
        token_stream_file_name = "data/results/token_stream.txt"
        preprocessing(self.file_name_data, token_stream_file_name)
        spimi.create(token_stream_file_name)
        if os.path.exists(spimi.index_file_name):
            self.write_norm_to_disk()
            self.load_index(spimi.index_file_name)

    def load_index(self, index_file_name):
        self.index = {}
        with open(index_file_name, "r") as f:
            for line in f:
                term, postings_list = ast.literal_eval(line.strip())
                self.index[term] = postings_list

    def write_norm_to_disk(self):
        norms = {}
        with open("data/results/merged_index.txt", "r") as file_global_index:
            for line in file_global_index:
                postings_list = ast.literal_eval(line)[1]
                idf = np.log10(self.number_of_documents / len(postings_list))
                for document_id, tf in postings_list:
                    tf = np.log10(tf + 1)
                    norms[document_id] = norms.get(document_id, 0) + (tf * idf) ** 2
        with open("data/results/norms.bin", "wb") as file_norms:
            for document_id, norm in sorted(norms.items()):
                norm = round(np.sqrt(norm), 6)
                id_encode = document_id.encode("utf-8")
                norm_encode = struct.pack("f", norm)
                file_norms.write(id_encode)
                file_norms.write(norm_encode)

    def search_term(self, token):
        with open("data/results/merged_index.txt", "r") as file_global_index:
            lines = file_global_index.readlines()
        low = 0
        high = len(lines) - 1
        while low <= high:
            mid = (low + high) // 2
            line = lines[mid]
            term, postings_list = ast.literal_eval(line)
            if token == term:
                return postings_list
            elif token < term:
                high = mid - 1
            else:
                low = mid + 1
        return None

    def search_norm(self, document_id):
        with open("data/results/norms.bin", "rb") as file_norms:
            file_size = os.fstat(file_norms.fileno()).st_size
            record_size = len(document_id.encode("utf-8")) + struct.calcsize("f")
            low = 0
            high = (file_size // record_size) - 1
            while low <= high:
                mid = (low + high) // 2
                file_norms.seek(mid * record_size)
                id_encode = file_norms.read(len(document_id))
                other_document_id = id_encode.decode("utf-8")
                if document_id == other_document_id:
                    norm_encode = file_norms.read(struct.calcsize("f"))
                    norm = struct.unpack("f", norm_encode)[0]
                    return norm
                elif document_id < other_document_id:
                    high = mid - 1
                else:
                    low = mid + 1
        return None

    def cosine_similarity(self, query, topk):
        scores = {}
        query_preprocessed = preprocessing_content(query)
        norm_query = 0
        # Calculate the weighted term frequency for the query
        for token, tf_query in query_preprocessed.items():
            postings_list = self.search_term(token)
            if postings_list:
                idf = np.log10(self.number_of_documents / len(postings_list))
                tf_query = np.log10(tf_query + 1)
                wt_query = tf_query * idf
                norm_query += np.square(wt_query)
                for document_id, tf in postings_list:
                    tf = np.log10(tf + 1)
                    wt = tf * idf
                    if document_id in scores:
                        scores[document_id] += wt_query * wt
                    else:
                        scores[document_id] = wt_query * wt
        # Normalize the query vector
        norm_query = np.sqrt(norm_query)
        # Normalize the document scores
        for document_id in scores:
            norm_document = self.search_norm(document_id)
            if norm_query != 0 and norm_document != 0:
                scores[document_id] /= (norm_query * norm_document)
            else:
                scores[document_id] = 0
        # Sort the documents by their scores in descending order and take the top k
        topk_documents = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:topk]

        return topk_documents
