"""
This is the template for implementing the rankers for your search engine.
You will be implementing WordCountCosineSimilarity, DirichletLM, TF-IDF, BM25, Pivoted Normalization, and your own ranker.
"""

from sample_data import SAMPLE_DOCS  # sample document import
import math
from collections import Counter
import numpy as np

class Ranker:
    # TODO implement this class properly. This is responsible for returning a list of sorted relevant documents.
    def __init__(self, index, document_preprocessor, stopword_filtering: bool, scorer: 'RelevanceScorer') -> None:
        self.index = index
        self.tokenize = document_preprocessor.tokenize
        if isinstance(scorer, type):
            scorer = scorer(index)
        self.scorer = scorer
        self.stopword_filtering = stopword_filtering

    def query(self, query: str) -> list[dict[str, int]]:

        # 1. Tokenize query

        # 2. Fetch a list of possible documents from the index

        # 2. Run RelevanceScorer (like BM25 from below classes) (implemented as relevance classes)

        # 3. Return **sorted** results as format [{docid: 100, score:0.5}, {{docid: 10, score:0.2}}]
        query_parts = self.tokenize(query)

        if self.stopword_filtering:
            temp = []
            with open('stopwords.txt', 'r') as f:
                STOPWORDS = set([line.strip().lower() for line in f])
        
                for term in query_parts:
                    if term is None:
                        continue
                    
                    if term.lower() in STOPWORDS:
                        temp.append(None)
                    else:
                        temp.append(term)
            query_parts = temp
        
        possible_docs = set()
        for term in query_parts:
            if term is None:
                continue
            possible_docs.update(doc_id for doc_id, _ in self.index.get_postings(term))
        
        results = []
        for doc_id in possible_docs:
            score = self.scorer.score(doc_id, query_parts)
            results.append(score)

        sorted_results = sorted(results, key=lambda x: (x['score']), reverse=True)
        return sorted_results

class RelevanceScorer:
    '''
    This is the base interface for all the relevance scoring algorithm.
    It will take a document and attempt to assign a score to it.
    '''
    # TODO Implement the functions in the child classes (WordCountCosineSimilarity, DirichletLM, BM25, PivotedNormalization, TF_IDF) 
    #      and not in this one
    
    def __init__(self, index, parameters) -> None:
        self.index = index
        self.parameters = parameters

    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        pass


class SampleScorer(RelevanceScorer):
    def __init__(self, index, parameters) -> None:
        pass

    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:

        # Print randomly ranked results
        return {'docid': docid, 'score': 10}

# TODO Implement unnormalized cosine similarity on word count vectors
class WordCountCosineSimilarity(RelevanceScorer):
    def __init__(self, index, parameters: dict = {}) -> None:
        self.index = index
        # 1. Find the dot product of the word count vector of the document and the word count vector of the query
        
        # 2. Return the score
    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        score = 0
        for term in query_parts:
            postings_list = self.index.get_postings(term)
            for doc, term_frequency in postings_list:
                if doc == docid:
                    score += term_frequency
                    break
        return {'docid': docid, 'score': score} 

# TODO: Implement DirichletLM
class DirichletLM(RelevanceScorer):
    def __init__(self, index, parameters: dict = {'mu': 2000}) -> None:
        self.index = index
        self.mu = parameters.get('mu', 2000)
    
    # 1. Get necessary information from index

    # 2. Compute additional terms to use in algorithm

    # 3. For all query_parts, compute score

    # 4. Return the score 
    
    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        doc_score = 0
        total_tokens = self.index.get_statistics()['total_token_count']
        query_tf_dict = dict(Counter(query_parts))
        
        for term in query_tf_dict.keys():
            term_freq_in_doc = self.index.get_postings(term)
            
            doc_term_freq = next((freq for doc, freq in term_freq_in_doc if doc == docid), 0)
            
            term_freq_in_query = query_tf_dict[term]
            
            word_prob_in_ref = self.index.get_term_metadata(term)['total_term_frequency'] / total_tokens
            if word_prob_in_ref == 0:
                continue
            
            doc_score += term_freq_in_query * np.log(1 + doc_term_freq / (self.mu * word_prob_in_ref))
        
        query_len = len(query_parts)
        doc_len = self.index.get_doc_metadata(docid)['length']
        doc_score += query_len * np.log(self.mu / (doc_len + self.mu))
        
        return {"docid": docid, "score": doc_score}

# TODO: Implement BM25
class BM25(RelevanceScorer):
    def __init__(self, index, parameters: dict = {'b': 0.75, 'k1': 1.2, 'k3': 8}) -> None:
        self.index = index
        self.b = parameters.get('b', 0.75)
        self.k1 = parameters.get('k1', 1.2)
        self.k3 = parameters.get('k3', 8)
    # 1. Get necessary information from index

    # 2. Compute additional terms to use in algorithm

    # 3. For all query parts, compute the TF, IDF, and QTF values to get a score

    # 4. Return the score   
    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        doc_score = 0
        query_tf_dict = dict(Counter(query_parts))

        doc_len = self.index.get_doc_metadata(docid)['length']
        total_docs = self.index.get_statistics()['number_of_documents']
        avg_doc_len = (self.index.get_statistics()['mean_document_length']if self.index.get_statistics()['number_of_documents'] != 0 else 0)
        
        for term in query_tf_dict.keys():
            term_freq_in_doc = self.index.get_postings(term)
            
            doc_term_freq = next((freq for doc, freq in term_freq_in_doc if doc == docid), 0)
            
            doc_freq = self.index.get_term_metadata(term)['document_frequency']

            term_freq_in_query = query_tf_dict[term]

            bm_1 = np.log((total_docs - doc_freq + 0.5) / (doc_freq + 0.5))
            bm_2 = (self.k1 + 1) * doc_term_freq / (self.k1 * (1 - self.b + self.b * doc_len / avg_doc_len) + doc_term_freq)
            bm_3 = (self.k3 + 1) * term_freq_in_query / (self.k3 + term_freq_in_query)
            doc_score += bm_1 * bm_2 * bm_3
            
        return {"docid": docid, "score": doc_score}

# TODO: Implement Pivoted Normalization
class PivotedNormalization(RelevanceScorer):
    def __init__(self, index, parameters: dict = {'b': 0.2}) -> None:
        self.index = index
        self.b = parameters.get('b', 0.2)
    
    # 1. Get necessary information from index

    # 2. Compute additional terms to use in algorithm

    # 3. For all query parts, compute the TF, IDF, and QTF values to get a score

    # 4. Return the score  
    
    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        score = 0
        query_tf_dict = dict(Counter(query_parts))
        avg_doc_len = (self.index.get_statistics()['mean_document_length'] if self.index.get_statistics()['number_of_documents'] != 0 else 0)
        total_docs = self.index.get_statistics()['number_of_documents']
        doc_len = self.index.get_doc_metadata(docid)['length']
        
        for term in query_tf_dict.keys():
            term_freq_in_doc = self.index.get_postings(term)
            
            doc_term_freq = next((freq for doc, freq in term_freq_in_doc if doc == docid), 0)
            
            term_freq_in_query = query_tf_dict[term]
            
            doc_count_with_term = self.index.get_term_metadata(term)['document_frequency']
            if doc_count_with_term == 0 or doc_term_freq == 0:
                continue

            middle_part = (1 + np.log(1 + np.log(doc_term_freq))) / (1 - self.b + self.b * doc_len / avg_doc_len)
            score += term_freq_in_query * middle_part * np.log((total_docs + 1) / doc_count_with_term)
            
        return {"docid": docid, "score": score}


# TODO: Implement TF-IDF
class TF_IDF(RelevanceScorer):
    def __init__(self, index, parameters: dict = {}) -> None:
        self.index = index
    # 1. Get necessary information from index

    # 2. Compute additional terms to use in algorithm

    # 3. For all query parts, compute the TF and IDF to get a score

    # 4. Return the score
    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        score = 0
        
        for term in query_parts:
            tf = self.index.get_TF(term, docid)
            idf = self.index.get_IDF(term)
            
            score += tf * idf
        
        return {'docid': docid, 'score': score}

# TODO: Implement your own ranker with proper heuristics
class YourRanker(RelevanceScorer):
    def __init__(self, index, parameters: dict = {'b': 0.75}) -> None:
        self.index = index
        self.b = parameters.get('b', 0.75)
    
    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        doc_length = self.index.get_doc_metadata(docid).get('length', 0)
        avg_doc_length = self.index.get_statistics().get('mean_document_length', 0)
        N = self.index.get_statistics().get('number_of_documents', 0)
        
        score = 0
        
        for term in query_parts:
            tf = self.index.get_TF(term, docid)
            tf = tf[0] if tf else 0 
            idf = self.index.get_IDF(term)
            if avg_doc_length == 0:
                continue
            
            score += (math.log(1 + tf, 10) * idf * (1 - self.b + self.b * (doc_length/avg_doc_length)))
        
        return {'docid': docid, 'score': score}

if __name__ == '__main__':
    from document_preprocessor import RegexTokenizer
    from indexing import Indexer, IndexType

    def print_result(index):
        # Print Document Metadata
        print("Document Metadata:")
        for doc_id, metadata in index.document_metadata.items():
            print(f"Document ID: {doc_id}, Metadata: {metadata}")

        # Print Index
        print("\nIndex Content:")
        for term, postings_list in index.index.items():
            print(f"Term: {term}, Postings List: {index.get_postings(term)}")

        # Print Statistics
        print("\nIndex Statistics:")
        print(index.get_statistics())
    
    document_preprocessor = RegexTokenizer("multi_word_expressions.txt")
    stopword_filtering = True
    FILE_PATH = "wikipedia_1M_dataset.jsonl"
    
    index = Indexer.create_index('InvertedIndex', IndexType.InvertedIndex, FILE_PATH, document_preprocessor, stopword_filtering, 0)

    # ranker = Ranker(index, document_preprocessor, stopword_filtering, WordCountCosineSimilarity(index, {}))
    ranker = Ranker(index, document_preprocessor, stopword_filtering, TF_IDF(index, {}))
    # ranker = Ranker(index, document_preprocessor, stopword_filtering, DirichletLM(index, {'mu': 0.2}))
    # ranker = Ranker(index, document_preprocessor, stopword_filtering, PivotedNormalization(index, {'b': 0.2}))
    # ranker = Ranker(index, document_preprocessor, stopword_filtering, BM25(index, { 'b': 0.75,'k1': 1.2,'k3': 8 }))
    # ranker = Ranker(index, document_preprocessor, stopword_filtering, DirichletLM)
    query = "AI chatbots and vehicles"

    # print_result(index)
    print(ranker.query(query))