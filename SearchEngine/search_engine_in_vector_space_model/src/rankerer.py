"""
This is the template for implementing the rankers for your search engine.
You will be implementing WordCountCosineSimilarity, DirichletLM, TF-IDF, BM25, Pivoted Normalization, and your own ranker.
"""

from sample_data import SAMPLE_DOCS  # sample document import
import numpy as np
from collections import Counter

class Ranker:
    # TODO implement this class properly. This is responsible for returning a list of sorted relevant documents.
    def __init__(self, index, document_preprocessor, stopword_filtering: bool, scorer: 'RelevanceScorer') -> None:
        self.index = index
        self.tokenize = document_preprocessor.tokenize
        self.stopword_filtering = stopword_filtering
        
        # self.scorer = scorer
        # NOTE: Auto-grader might pass a scorer class instead of an instance of the class. 
        if isinstance(scorer, type):
            self.scorer = scorer(index)
        else:
            self.scorer = scorer

    def query(self, query: str) -> list[dict[str, int]]:
        # 1. Tokenize query
        # 2. Fetch a list of possible documents from the index
        # 2. Run RelevanceScorer (like BM25 from below classes) (implemented as relevance classes)
        # 3. Return **sorted** results as format [{docid: 100, score:0.5}, {{docid: 10, score:0.2}}]

        results = []
        query_parts = self.tokenize(query)
        
        # Filter stopwords
        stopword_path = "./stopwords.txt"
        if self.stopword_filtering:
            tokens_filtered = []
            
            # Read stopwords
            with open(stopword_path, 'r') as file:
                stopword_lower_set = set([line.strip().lower() for line in file])
                for token in query_parts:
                    if token is None:
                        continue
                    
                    if token.lower() in stopword_lower_set: # Stopwords Filtering is case-insensitive
                        tokens_filtered.append(None)
                    else:
                        tokens_filtered.append(token)   # Append original token instead of the lower case of the token
            
            query_parts = tokens_filtered
            print(f"stopword_filtering = True, tokens_after_stopwords = {query_parts}")
        
        # # Remove terms that don't exist in the index.
        # query_parts_overlapped = []
        # for term in query_parts:
        #     if term in self.index.get_index():
        #         query_parts_overlapped.append(term)
        
        # print(f"query_parts_overlapped = {query_parts_overlapped}")
        # Result is a empty list if query_parts and index do not overlap.
        # if len(query_parts_overlapped) == 0:
        #     return []
        
        for docid in self.index.document_metadata.keys():
            # Only get score for documents that contain at least one term in query_parts.
            evaluate_doc = False
            for term in query_parts:
                term_freq_in_doc = self.index.get_postings(term)
            
                tf_in_doc = next((freq for doc, freq in term_freq_in_doc if doc == docid), 0)
                if tf_in_doc > 0:
                    evaluate_doc = True
                    break
            
            if evaluate_doc:    
                results.append(self.scorer.score(docid, query_parts))
        
        print(f"results before sort = {results}")
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        #### Test #####
        query_tf_dict = dict(Counter(query_parts))
        # print(f"index = {self.index.get_index()}")
        # print(f"query = {query}")
        # print(f"query_tf_dict = {query_tf_dict}")

        print(f"results after sort = {sorted_results}\n")
        ###################################
        
        return sorted_results


class RelevanceScorer:
    '''
    This is the base interface for all the relevance scoring algorithm.
    It will take a document and attempt to assign a score to it.
    '''
    # TODO Implement the functions in the child classes (WordCountCosineSimilarity, DirichletLM, BM25, PivotedNormalization, TF_IDF) 
    #      and not in this one
    
    def __init__(self, index, parameters) -> None:
        raise NotImplementedError

    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        raise NotImplementedError


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
        
    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        # 1. Find the dot product of the word count vector of the document and the word count vector of the query
        # 2. Return the score
        doc_score = 0
        
        query_tf_dict = dict(Counter(query_parts))
        
        for term in query_tf_dict.keys():
            tf_doc = self.index.get_term_count_in_doc(term, docid)
            doc_score += query_tf_dict[term] * tf_doc
        
        return {"docid": docid, "score": doc_score}


# TODO: Implement TF-IDF
class TF_IDF(RelevanceScorer):
    def __init__(self, index, parameters: dict = {}) -> None:
        self.index = index
        
    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        # 1. Get necessary information from index
        # 2. Compute additional terms to use in algorithm
        # 3. For all query parts, compute the TF and IDF to get a score
        # 4. Return the score
        doc_score = 0
        
        query_tf_dict = dict(Counter(query_parts))
        
        for term in query_tf_dict.keys():
            tf = self.index.get_TF(term, docid)
            idf = self.index.get_IDF(term)
            doc_score += query_tf_dict[term] * tf * idf
        
        return {"docid": docid, "score": doc_score}


# TODO: Implement DirichletLM
class DirichletLM(RelevanceScorer):
    def __init__(self, index, parameters: dict = {'mu': 2000}) -> None:
        self.index = index
        self.mu = parameters['mu']
        print(f"parameters = {parameters}")
        
    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        # 1. Get necessary information from index
        # 2. Compute additional terms to use in algorithm
        # 3. For all query_parts, compute score
        # 4. Return the score
        doc_score = 0
        query_tf_dict = dict(Counter(query_parts))
        
        for term in query_tf_dict.keys():
            if term not in self.index.get_index():
                continue
            
            term_count_in_doc = self.index.get_term_count_in_doc(term, docid)
            if term_count_in_doc == 0:
                continue
            
            term_freq_in_query = query_tf_dict[term]
            # print(f"docid = {docid}, ", end="")
            word_prob_in_ref = self.get_word_prob_in_ref(term)
            
            doc_score += term_freq_in_query * np.log(1 + term_count_in_doc / (self.mu * word_prob_in_ref))
        
        query_len = len(query_parts)
        doc_len = self.index.get_doc_metadata(docid)['length']
        doc_score += query_len * np.log(self.mu / (doc_len + self.mu))
        
        return {"docid": docid, "score": doc_score}
    
    def get_word_prob_in_ref(self, term: str) -> float:
        term_total_count = self.index.get_term_metadata(term)['total_freq']
        total_token_count = self.index.get_statistics()['total_token_count']
        # print(f"term = {term}, term_total_count = {term_total_count}, total_token_count = {total_token_count}")
        return term_total_count / total_token_count


# TODO: Implement Pivoted Normalization
class PivotedNormalization(RelevanceScorer):
    def __init__(self, index, parameters: dict = {'b': 0.2}) -> None:
        self.index = index
        self.b = parameters['b']
        print(f"parameters = {parameters}")
        
    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        # 1. Get necessary information from index
        # 2. Compute additional terms to use in algorithm
        # 3. For all query parts, compute the TF, IDF, and QTF values to get a score
        # 4. Return the score
        doc_score = 0
        query_tf_dict = dict(Counter(query_parts))
        
        for term in query_tf_dict.keys():
            term_freq_in_doc = self.index.get_postings(term)
            
            doc_term_freq = next((freq for doc, freq in term_freq_in_doc if doc == docid), 0)
            
            term_freq_in_query = query_tf_dict[term]
            doc_len = self.index.get_doc_metadata(docid)['length']
            avg_doc_len = self.index.get_statistics()['mean_document_length']
            total_doc_num = self.index.get_statistics()['number_of_documents']
            doc_count_with_term = self.index.get_term_metadata(term)['document_frequency']
            if doc_count_with_term == 0 or doc_term_freq == 0:
                continue

            middle_part = (1 + np.log(1 + np.log(doc_term_freq))) / (1 - self.b + self.b * doc_len / avg_doc_len)
            doc_score += term_freq_in_query * middle_part * np.log((total_doc_num + 1) / doc_count_with_term)
            
        return {"docid": docid, "score": doc_score}
            

# TODO: Implement BM25
class BM25(RelevanceScorer):
    def __init__(self, index, parameters: dict = {'b': 0.75, 'k1': 1.2, 'k3': 8}) -> None:
        self.index = index
        self.b = parameters['b']
        self.k1 = parameters['k1']
        self.k3 = parameters['k3']
        print(f"parameters = {parameters}")
        
    def score(self, docid: int, query_parts: list[str]) -> dict[str, int]:
        # 1. Get necessary information from index
        # 2. Compute additional terms to use in algorithm
        # 3. For all query parts, compute the TF, IDF, and QTF values to get a score
        # 4. Return the score
        doc_score = 0
        query_tf_dict = dict(Counter(query_parts))
        
        for term in query_tf_dict.keys():
            if term not in self.index.get_index():
                continue
            
            term_count_in_doc = self.index.get_term_count_in_doc(term, docid)
            if term_count_in_doc == 0:
                continue
            
            total_doc_num = self.index.get_statistics()['number_of_documents']
            term_metadata = self.index.get_term_metadata(term)
            doc_count_with_term = term_metadata['doc_freq']
            avg_doc_len = self.index.get_statistics()['mean_document_length']
            doc_len = self.index.get_doc_metadata(docid)['length']
            term_freq_in_query = query_tf_dict[term]
            # print(f"docid = {docid}, total_doc_num = {total_doc_num}, doc_count_with_term = {doc_count_with_term}, avg_doc_len = {avg_doc_len}, doc_len = {doc_len}, term_freq_in_query = {term_freq_in_query}")

            first_part = np.log((total_doc_num - doc_count_with_term + 0.5) / (doc_count_with_term + 0.5))
            middle_part = (self.k1 + 1) * term_count_in_doc / (self.k1 * (1 - self.b + self.b * doc_len / avg_doc_len) + term_count_in_doc)
            last_part = (self.k3 + 1) * term_freq_in_query / (self.k3 + term_freq_in_query)
            doc_score += first_part * middle_part * last_part
            
        return {"docid": docid, "score": doc_score}



# TODO: Implement your own ranker with proper heuristics
class YourRanker(RelevanceScorer):
    pass


if __name__ == '__main__':
    from document_preprocessor import RegexTokenizer
    from indexing import Indexer, IndexType
    
    document_preprocessor = RegexTokenizer("multi_word_expressions.txt")
    stopword_filtering = True
    FILE_PATH = "wikipedia_1M_dataset.jsonl"

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
    
    index = Indexer.create_index('InvertedIndex', IndexType.InvertedIndex, FILE_PATH, document_preprocessor, stopword_filtering, 0)
    # index = Indexer.create_index('InvertedIndex', IndexType.InvertedIndex, './wikipedia_1M_dataset.jsonl', document_preprocessor, False, 0)
    
    # ranker = Ranker(index, document_preprocessor, stopword_filtering, WordCountCosineSimilarity(index, {}))
    ranker = Ranker(index, document_preprocessor, stopword_filtering, TF_IDF(index, {}))
    # ranker = Ranker(index, document_preprocessor, stopword_filtering, DirichletLM(index, {'mu': 0.2}))
    # ranker = Ranker(index, document_preprocessor, stopword_filtering, PivotedNormalization(index, {'b': 0.2}))
    # ranker = Ranker(index, document_preprocessor, stopword_filtering, BM25(index, { 'b': 0.75,'k1': 1.2,'k3': 8 }))
    # ranker = Ranker(index, document_preprocessor, stopword_filtering, DirichletLM)
    query = "AI chatbots and vehicles"
    # query = "AI"
    # query = "noasd"
    print(ranker.query(query))

    #print_result(index)
    # print(f"query = {query}, results = {ranker.query(query)}")
    # print(ranker.query("final"))
    
    
    # a = [{'docid': 1, 'score': -0.31623109945742595}, {'docid': 2, 'score': 0}, {'docid': 3, 'score': 0.7257835477973098}, {'docid': 4, 'score': 1.5460888344441546}, {'docid': 5, 'score': -0.35318117923823517}]
    # print(sorted(a, key=lambda x: x['score'], reverse=True))
    total_token_count = 34+26+36+28+27
    # print(total_token_count)