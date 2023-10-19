'''
Author: Prithvijit Dasgupta
This file is a template code file for piecing together the different parts of the system.
'''
from __future__ import annotations
from models import BaseSearchEngine, SearchResponse

# delete the next line before final submission
from sample_data import SAMPLE_DOCS

# your library imports go here
from document_preprocessor import RegexTokenizer
from indexing import Indexer, IndexType
from ranker import Ranker, SampleScorer


class SearchEngine(BaseSearchEngine):
    def __init__(self, index_name: str, **kwargs) -> None:
        # initialize the document tokenizer
        document_preprocessor = RegexTokenizer("multi_word_expressions.txt")
        # initialize the index
        # Note: dataset_path should be a path to your dataset rather than a Python object.
        self.index = Indexer.create_index(
            index_name, IndexType.InvertedIndex, kwargs['dataset_path'], document_preprocessor, False, 0)
        # initialize the search algorithm and rank using the index
        self.ranker = Ranker(self.index, document_preprocessor, False, SampleScorer(self.index, {'hyperparam1': 100, 'hyperparam2': 2}))

    def search(self, query: str) -> list[SearchResponse]:
        # here the ranker should score, sort and return a bunch of docids as results
        results = self.ranker.query(query)
        # SearchResponse is a FastAPI/Pydantic model which essentially helps creates the UI.
        # the expectation is to create a list of SearchResponses where the id is the rank of the document, docid is the Wikipedia document id and score is the score of the document.
        # As a sample, we have hardcoded the docid to a magical wikipedia doc and it has to be changed in your final implementation
        return [SearchResponse(id=idx+1, docid=result['docid'], score=result['score']) for idx, result in enumerate(results)]


def initialize():
    # initializing the search engine
    index_name = 'sample_index'
    search_obj = SearchEngine(index_name, dataset_path=SAMPLE_DOCS)
    return search_obj
