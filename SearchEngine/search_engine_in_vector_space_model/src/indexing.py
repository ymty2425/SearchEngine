'''
Here you will be implemeting the indexing strategies for your search engine. You will need to create, persist and load the index.
This will require some amount of file handling.
Use libraries such as tqdm, orjson, collections.Counter, shelve if you need them.
DO NOT use the pickle module.
'''
from enum import Enum
import bisect
import shelve
import pickle
import json
import sys
import time
import os
import numpy as np
from sample_data import SAMPLE_DOCS
from tqdm import tqdm
from collections import Counter

class IndexType(Enum):
    # the three types of index currently supported are InvertedIndex, PositionalIndex and OnDiskInvertedIndex
    PositionalIndex = 'PositionalIndex'
    InvertedIndex = 'InvertedIndex'
    OnDiskInvertedIndex = 'OnDiskInvertedIndex'
    SampleIndex = 'SampleIndex'


class InvertedIndex:
    '''
    The base interface representing the data structure for all index classes.
    The functions are meant to be implemented in the actual index classes and not as part of this interface.
    '''

    def __init__(self, index_name) -> None:
        self.index_name = index_name  # name of the index
        self.statistics = {'vocab': {}}  # the central statistics of the index
        self.index = {}  # the index
        self.vocabulary = set()  # the vocabulary of the collection
        # metadata like length, number of unique tokens of the documents
        self.document_metadata = {}
        # OPTIONAL if using SPIMI, use this variable to keep track of the index segments.
        self.index_segment = 0

    
    # NOTE: The following functions have to be implemented in the three inherited classes and not in this class

    def remove_doc(self, docid: int) -> None:
        # TODO implement this to remove a document from the entire index and statistics
        pass

    def add_doc(self, docid: int, tokens: list[str]) -> None:
        # TODO implement this to add documents to the index
        pass

    def get_postings(self, term: str) -> list:
        # TODO implement this to fetch a term's postings from the index
        return self.index.get(term, [])

    def get_doc_metadata(self, doc_id: int) -> dict[str, int]:
        # TODO implement to fetch a particular documents stored metadata
        return self.document_metadata.get(doc_id, {})

    def get_term_metadata(self, term: str) -> dict[str, int]:
        # TODO implement to fetch a particular terms stored metadata
        postings_list = self.get_postings(term)
        document_frequency = len(postings_list)
        total_term_frequency = sum(freq for _, freq in postings_list)
        return {'total_term_frequency': total_term_frequency, 'document_frequency': document_frequency}

    def get_statistics(self) -> dict[str, int]:
        # TODO calculate statistics like 'unique_token_count', 'total_token_count', 'number_of_documents', 'mean_document_length' and any other relevant central statistic.
        total_document_length = sum(doc_meta['length'] for doc_meta in self.document_metadata.values())
        mean_document_length = total_document_length / len(self.document_metadata) if self.document_metadata else 0
        
        return {
            'mean_document_length': mean_document_length,
            'number_of_documents': len(self.document_metadata),
            'total_token_count': total_document_length,
            'unique_token_count': len(self.vocabulary)
        }
    
    def get_TF(self, term: str, docid: int) -> int:
        """
        Get term frequency of a term in a document.
        """
        postings_list = self.get_postings(term)
        for doc, freq in postings_list:
            if doc == docid:
                return np.log(freq + 1)
        return 0
    
    def get_IDF(self, term: str) -> float:
        """
        Get inverse document frequency of a term.
        """
        N = self.get_statistics()['number_of_documents'] 
        df_t = len(self.get_postings(term))
        return 1 + np.log(N / df_t) if df_t > 0 else 0

    def save(self) -> None:
        # TODO save the index files to disk
        if not os.path.exists(self.index_name):
            os.makedirs(self.index_name)
        
        with open(os.path.join(self.index_name, "index.json"), "w", encoding='utf-8') as index_file:
            json.dump(self.index, index_file, ensure_ascii=False, indent=4)

    def load(self) -> None:
        # TODO load the index files from disk to a Python object
        with open(os.path.join(self.index_name, "index.json"), "r", encoding='utf-8') as index_file:
            self.index = json.load(index_file)

    def flush_to_disk(self) -> None:
        # OPTIONAL TODO flush index segments created using SPIMI strategy to disk and increment the segment number
        segment_name = f"{self.index_name}_segment_{self.index_segment}"
    
        with open(f"{segment_name}_index.json", "w", encoding='utf-8') as index_file:
            json.dump(self.index, index_file, ensure_ascii=False, indent=4)
        
        self.index = {}
        self.index_segment += 1


class BasicInvertedIndex(InvertedIndex):
    def __init__(self, index_name) -> None:
        super().__init__(index_name)
        self.statistics['index_type'] = 'BasicInvertedIndex'
    # TODO implement all the functions mentioned in the interface
    # This is the typical inverted index where each term keeps track of documents and the term count per document.

    def remove_doc(self, docid: int) -> None:
        doc_tokens = [term for term, postings in self.index.items() if any(doc[0] == docid for doc in postings)]
        
        for token in doc_tokens:
            postings_list = self.index[token]
            postings_list = [(d, f) for d, f in postings_list if d != docid]
            
            if not postings_list:
                del self.index[token]
                self.vocabulary.remove(token)
            else:
                self.index[token] = postings_list
        
        doc_meta = self.document_metadata.pop(docid, {})

    # def add_doc(self, docid: int, tokens: list[str]) -> None:
    #     self.document_metadata[docid] = {
    #         'length': len(tokens), 
    #         'unique_tokens': len(set(tokens))
    #     }
        
    #     for token in tokens:
    #         if token is None:
    #             continue
            
    #         if token not in self.index:
    #             self.index[token] = []
    #             self.vocabulary.add(token)
            
    #         postings_list = self.index[token]
    #         doc_entry = next((entry for entry in postings_list if entry[0] == docid), None)
            
    #         if doc_entry:
    #             postings_list.remove(doc_entry)
    #             freq = doc_entry[1] + 1
    #         else:
    #             freq = 1
            
    #         postings_list.append((docid, freq))
    #         postings_list.sort()

    def add_doc(self, docid: int, tokens: list[str]) -> None:
        self.document_metadata[docid] = {
            'length': len(tokens),
            'unique_tokens': len(set(tokens))
        }

        token_freqs = Counter(tokens)

        for token, freq in token_freqs.items():
            if token is None:
                continue
            
            if token not in self.index:
                self.index[token] = []

            self.index[token].append((docid, freq))
            
            self.vocabulary.add(token)

    def get_postings(self, term: str) -> list:
        return super().get_postings(term)
    
    def get_doc_metadata(self, doc_id: int) -> dict[str, int]:
        return super().get_doc_metadata(doc_id)
    
    def get_term_metadata(self, term: str) -> dict[str, int]:
        return super().get_term_metadata(term)
    
    def get_statistics(self) -> dict[str, int]:
        return super().get_statistics()
    
    def save(self) -> None:
        return super().save()
    
    def load(self) -> None:
        return super().load()
    
    def flush_to_disk(self) -> None:
        return super().flush_to_disk()

class PositionalInvertedIndex(InvertedIndex):
    def __init__(self, index_name) -> None:
        super().__init__(index_name)
        self.statistics['index_type'] = 'PositionalInvertedIndex'
    # TODO implement all the functions mentioned in the interface
    # This is the positional inverted index where each term keeps track of documents and positions of the terms occring in the document.

    def remove_doc(self, docid: int) -> None:
        if docid not in self.document_metadata:
            return
        terms_to_delete = []
        for term, postings_list in self.index.items():
            for i, (d, _, _) in enumerate(postings_list):
                if d == docid:
                    del postings_list[i]
                    break
            if not postings_list:
                terms_to_delete.append(term)
        for term in terms_to_delete:
            del self.index[term]
            self.vocabulary.remove(term)
        del self.document_metadata[docid]

    def add_doc(self, docid: int, tokens: list[str]) -> None:
        self.document_metadata[docid] = {
            'length': len(tokens),
            'unique_tokens': len(set(tokens))
        }
        
        for position, token in enumerate(tokens):
            # None token
            if token is None:
                continue

            if token not in self.index:
                self.index[token] = []
                self.vocabulary.add(token)
            
            insert_pos = bisect.bisect_left(self.index[token], (docid,))

            if insert_pos == len(self.index[token]) or self.index[token][insert_pos][0] != docid:
                self.index[token].insert(insert_pos, (docid, 1, [position]))
            else:
                _, freq, positions = self.index[token][insert_pos]
                self.index[token][insert_pos] = (docid, freq + 1, positions + [position])
        
    def get_postings(self, term: str) -> list:
        return super().get_postings(term)

    def get_doc_metadata(self, doc_id: int) -> dict[str, int]:
        return super().get_doc_metadata(doc_id)
    
    def get_term_metadata(self, term: str) -> dict[str, int]:
        postings_list = self.get_postings(term)
        doc_frequency = len(postings_list)
        total_term_frequency = sum(freq for _, freq, _ in postings_list)
        return {'document_frequency': doc_frequency, 'total_term_frequency': total_term_frequency}

    def get_statistics(self) -> dict[str, int]:
        return super().get_statistics()
    
    def save(self) -> None:
        return super().save()
    
    def load(self) -> None:
        return super().load()
    
    def flush_to_disk(self) -> None:
        return super().flush_to_disk()

class OnDiskInvertedIndex(InvertedIndex):
    def __init__(self, index_name) -> None:
        super().__init__(index_name)
        self.statistics['index_type'] = 'OnDiskInvertedIndex'
        self.postings_db_path = os.path.join(self.index_name, "postings_db")
        os.makedirs(self.index_name, exist_ok=True)
    
    def remove_doc(self, docid: int) -> None:
        if docid in self.document_metadata:
            del self.document_metadata[docid]
        
        with shelve.open(self.postings_db_path, writeback=True) as postings_db:         
            for token in list(self.vocabulary):
                postings_list = postings_db.get(token, {})
                if docid in postings_list:
                    del postings_list[docid]
                
                    if postings_list:
                        postings_db[token] = postings_list
                    else:
                        del postings_db[token]
                        self.vocabulary.remove(token)
                        del self.index[token]

    
    def add_doc(self, docid: int, tokens: list[str]) -> None:
        self.document_metadata[docid] = {
            'length': len(tokens), 
            'unique_tokens': len(set(tokens))
        }
        
        with shelve.open(self.postings_db_path, writeback=True) as postings_db:
            for token in tokens:
                if token is None:
                    continue
                
                if token not in self.index:
                    self.index[token] = {}
                        
                if docid in self.index[token]:
                    self.index[token][docid] += 1
                else:
                    self.index[token][docid] = 1
                    self.vocabulary.add(token)
                
                postings_list = postings_db.get(token, {})
                postings_list[docid] = postings_list.get(docid, 0) + 1
                postings_db[token] = postings_list
    
    def get_postings(self, term: str) -> list:
        # with shelve.open(self.postings_db_path, writeback=False) as postings_db:
        #     postings_dict = postings_db.get(term, {})
        #     return [(docid, freq) for docid, freq in postings_dict.items()]
        postings_list = self.index.get(term, {})
        postings = [(docid, freq) for docid, freq in postings_list.items()]
        return postings
    
    def get_statistics(self) -> dict[str, int]:
        return super().get_statistics()
    
    def get_term_metadata(self, term: str) -> dict[str, int]:
        postings_list = self.index.get(term, {})
        
        return {
            'total_term_frequency': sum(postings_list.values()),  
            'document_frequency': len(postings_list)
        }


    def save(self) -> None:
        # TODO save the index files to disk
        if not os.path.exists(self.index_name):
            os.makedirs(self.index_name)

        with shelve.open(os.path.join(self.index_name, "index"), 'c') as index:
            index['index'] = self.index
            index['vocabulary'] = self.vocabulary
            index['document_metadata'] = self.document_metadata
            index['statistics'] = self.statistics
    
    def load(self) -> None:
        # TODO load the index files from disk to a Python object
        with shelve.open(os.path.join(self.index_name, "index"), 'r') as index:
            self.index = index['index']
            self.vocabulary = index['vocabulary']
            self.document_metadata = index['document_metadata']
            self.statistics = index['statistics']
    
    def flush_to_disk(self) -> None:
        # OPTIONAL TODO flush index segments created using SPIMI strategy to disk and increment the segment number
        segment_name = f"{self.index_name}_segment_{self.index_segment}"
        with shelve.open(segment_name) as segment_db:
            segment_db.update(self.index)

        self.index_segment += 1
        self.index = {}

class Indexer:
    '''The Indexer class is responsible for creating the index used by the search/ranking algorithm.
    '''

    @staticmethod
    def create_index(index_name: str, index_type: IndexType, dataset_path: str, document_preprocessor, stopword_filtering: bool, minimum_word_frequency: int) -> InvertedIndex:
        '''
        The Index class' static function which is responsible for creating the indexes already created indexes present on disk.

        Parameters:

        index_name [str]: This is essentially the folder where you would keep all of the generated index files. The generated files may differ from student to student based on their implementation.

        index_type [IndexType]: This parameter tells you which type of index to create - Inverted index or positional index.

        dataset_path [str]: This is the path to your dataset

        document_preprocessor: This is a class which has a 'tokenize' function which would read each document's text and return back a list of valid tokens.

        stop_word_filtering [bool]: This is an optional configuration where you could enable or disable stop word filtering.

        minimum_word_frequency [int]: This is also an optional configuration which sets the minimum word frequency of a particular token to be indexed. If the token does not appear in the document atleast for the set frequency, it will not be indexed. Setting a value of 0 will completely ignore the parameter.

        '''
        # TODO implement this class properly. This is responsible for going through the documents one by one and inserting them into the index after tokenizing the document
        if index_type == IndexType.PositionalIndex:
            index = PositionalInvertedIndex(index_name)
        elif index_type == IndexType.InvertedIndex:
            index = BasicInvertedIndex(index_name)
        elif index_type == IndexType.OnDiskInvertedIndex:
            index = OnDiskInvertedIndex(index_name)
        else:
            raise ValueError(f"Unknown index_type: {index_type}")
        
        if stopword_filtering:
            with open('stopwords.txt', 'r') as f:
                stopwords = set(f.read().splitlines())
        
        with open(dataset_path, 'r', encoding='utf-8') as file:
            for count, line in tqdm(enumerate(file)):
                # if count >= 5:
                #     break
                doc = json.loads(line.strip())
                tokens = document_preprocessor.tokenize(doc['text'])

                if stopword_filtering or minimum_word_frequency > 1:
                    lower_tokens = [token.lower() if token is not None else None for token in tokens]
                    
                    token_freq = {}
                    for token in lower_tokens:
                        if token:
                            token_freq[token] = token_freq.get(token, 0) + 1
                    #print(token_freq)
                    filtered_tokens = []

                    for token, lower_token in zip(tokens, lower_tokens):
                        if stopword_filtering and lower_token in stopwords:
                            filtered_tokens.append(None)
                        elif minimum_word_frequency > 1 and token_freq.get(lower_token, 0) < minimum_word_frequency:
                            filtered_tokens.append(None)
                        else:
                            filtered_tokens.append(token)
                else:
                    filtered_tokens = tokens
                # print(filtered_tokens)
                index.add_doc(doc['docid'], filtered_tokens)
        
        index.save()       
        return index

# TODO for each inverted index implementation, use the Indexer to create an index with the first 10, 100, 1000, and 10000 documents in the collection (what was just preprocessed). At each size, record (1) how
# long it took to index that many documents and (2) using the get memory footprint function provided, how much memory the index consumes. Record these sizes and timestamps. Make
# a plot for each, showing the number of documents on the x-axis and either time or memory
# on the y-axis.

'''
The following class is a stub class with none of the essential methods implemented. It is merely here as an example.
'''


class SampleIndex(InvertedIndex):
    '''
    This class does nothing of value
    '''

    def add_doc(self, docid, tokens):
        """Tokenize a document and add term ID """
        for token in tokens:
            if token not in self.index:
                self.index[token] = {docid: 1}
            else:
                self.index[token][docid] = 1
    
    def save(self):
        print('Index saved!')

def get_memory_footprint(obj, seen=None):

    size = sys.getsizeof(obj)
    obj_id = id(obj)
    if seen is None:
        seen = set()
    elif obj_id in seen:
        return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_memory_footprint(v, seen) for v in obj.values()])
        size += sum([get_memory_footprint(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_memory_footprint(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_memory_footprint(i, seen) for i in obj])
    return size

if __name__=='__main__':
    
    import matplotlib.pyplot as plt
    from document_preprocessor import RegexTokenizer

    FILE_PATH = "wikipedia_1M_dataset.jsonl"
    MULTIWORD_PATH = "multi_word_expressions.txt"

    document_preprocessor = RegexTokenizer(MULTIWORD_PATH)
    index_name = "my_index"
    index_type = IndexType.OnDiskInvertedIndex
    stopword_filtering = True
    minimum_word_frequency = 2
    
    doc_sizes = [10, 100, 1000, 10000]
    indexing_times = []
    memory_usages = []
    
    for doc_size in doc_sizes:
        # NOTE: The dataset should be preprocessed to have subsets for 10, 100, 1000, 10000 documents
        start_time = time.time()
        index = Indexer.create_index(index_name + f"_{doc_size}", index_type, FILE_PATH, 
                                     document_preprocessor, stopword_filtering, minimum_word_frequency, doc_size)
        end_time = time.time()
        
        indexing_times.append(end_time - start_time)
        memory_usages.append(get_memory_footprint(index))
    
    plt.figure(figsize=(10, 6))
    plt.plot(doc_sizes, indexing_times, marker='o', linestyle='-')
    plt.title('Time vs Number of Documents Indexed')
    plt.xlabel('Number of Documents')
    plt.ylabel('Time (seconds)')
    plt.grid(True)
    plt.show()
    
    plt.figure(figsize=(10, 6))
    plt.plot(doc_sizes, memory_usages, marker='o', linestyle='-', color='r')
    plt.title('Memory Usage vs Number of Documents Indexed')
    plt.xlabel('Number of Documents')
    plt.ylabel('Memory Usage (bytes)')
    plt.grid(True)
    plt.show()
        

