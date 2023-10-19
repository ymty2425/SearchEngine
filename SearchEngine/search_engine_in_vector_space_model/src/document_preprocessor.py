"""
This is the template for implementing the tokenizer for your search engine.
You will be testing some tokenization techniques and build your own tokenizer.
"""
from __future__ import annotations
import nltk
import spacy
import re
import time
import json
# import matplotlib.pyplot as plt

class Tokenizer:
    def __init__(self, file_path: str) -> None:
        # Open the file that contains multi-word expressions and initialize a list of multi-word expressions.
        self.multi_word_expressions = []
        try:
            with open(file_path, 'r') as file:
                self.multi_word_expressions = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print(f"File at {file_path} not found. Multi-word expressions list is empty.")

    def replace_multi_word_expressions(self, text: str) -> str:
        sorted_expressions = sorted(self.multi_word_expressions, key=len, reverse=True)
        
        for expression in sorted_expressions:
            single_token = expression.replace(" ", "_")  
            text = text.replace(expression, single_token)  
        
        return text


'''
class SampleTokenizer(Tokenizer):
    def tokenize(self, text: str) -> list[str]:
        """This is a dummy tokenizer.

        Parameters:

        text [str]: This is an input text you want to tokenize.
        """
        return ['token_1', 'token_2', 'token_3']  # This is not correct; it is just a placeholder.
'''

class SplitTokenizer(Tokenizer):
    def tokenize(self, text: str) -> list[str]:
        # Implement a tokenizer that uses the split function.
        """Split a string into a list of tokens using whitespace as a delimiter.

        Parameters:

        text [str]: This is an input text you want to tokenize.
        """
        text = self.replace_multi_word_expressions(text)
        
        tokens = text.split()
            
        tokens = [token.replace("_", " ") for token in tokens]
        return tokens


class RegexTokenizer(Tokenizer):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.tokenizer = nltk.RegexpTokenizer(r'\w+')
        # self.tokenizer = nltk.RegexpTokenizer(r'\w+')

    def tokenize(self, text: str) -> list[str]:
        # Implement a tokenizer that uses NLTK’s RegexTokenizer
        """Use NLTK’s RegexTokenizer and regular expression patterns to tokenize a string.

        Parameters:

        text [str]: This is an input text you want to tokenize.
        """
        text = self.replace_multi_word_expressions(text)
        
        tokens = self.tokenizer.tokenize(text)
            
        tokens = [token.replace("_", " ") for token in tokens]
            
        return tokens
        

class SpaCyTokenizer(Tokenizer):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.nlp = spacy.load('en_core_web_sm')
    
    def tokenize(self, text: str) -> list[str]:
        # Implement a tokenizer that uses spaCy to process named entities as single words
        """Use a spaCy tokenizer to convert named entities into single words.
        Check the spaCy documentation to learn about the feature that supports named entity recognition.

        Parameters:

        text [str]: This is an input text you want to tokenize.
        """
    
        text = self.replace_multi_word_expressions(text)
        # Tokenize the text using spaCy and process named entities as single words.
        doc = self.nlp(text)
        tokens = []
        for token in doc:
            if token.ent_iob_ == 'B':  # Beginning of a named entity
                entity = "_".join([t.text for t in doc[token.i: token.i + len(list(doc[token.i: token.ent_iob == 'I'])) + 1]])
                tokens.append(entity)
            elif token.ent_iob_ == 'O':  # Outside of a named entity
                tokens.append(token.text)
        
        tokens = [token.replace("_", " ") for token in tokens]
        return tokens

        # def tokenize(self, text: str) -> list[str]:
        #     doc = self.nlp(text)
        #     tokens = []
        #     for token in doc:
        #         if token.ent_type_:
        #             tokens.append(re.sub(r'\s+', '_', token.text))
        #         else:
        #             tokens.append(token.text)
        #     return tokens

# TODO tokenize the first 1000 documents and record the time. Make a plot showing the time taken for each.
if __name__=='__main__':
    import matplotlib.pyplot as plt

    FILE_PATH = "wikipedia_1M_dataset.jsonl"
    MULTIWORD_PATH = "multi_word_expressions.txt"

    split_tokenizer = SplitTokenizer(MULTIWORD_PATH)
    regex_tokenizer = RegexTokenizer(MULTIWORD_PATH)
    spacy_tokenizer = SpaCyTokenizer(MULTIWORD_PATH)

    tokenizers = [split_tokenizer, regex_tokenizer, spacy_tokenizer]
    tokenizer_names = ['SplitTokenizer', 'RegexTokenizer', 'SpaCyTokenizer']

    times = {name: 0 for name in tokenizer_names}

    with open(FILE_PATH, 'r') as file:
        for i, line in enumerate(file):
            if i >= 1000: 
                break
                
            doc = json.loads(line)
            
            for tokenizer, name in zip(tokenizers, tokenizer_names):
                start_time = time.time()
                tokenizer.tokenize(doc['text'])
                end_time = time.time()
                times[name] += end_time - start_time

    names = list(times.keys())
    values = list(times.values())

    print(times)
    plt.figure(figsize=(10, 5))
    plt.bar(names, values, color=['blue', 'green', 'red'], log=True)
    plt.title('Time taken by each tokenizer for the first 1000 documents')
    plt.show()

# Initialize the Tokenizer with the multi-word expressions file
# tokenizer = SpaCyTokenizer('multi_word_expressions.txt')

# with open('path_to_documents.json', 'r') as file:
#     documents = json.load(file)

# for doc in SAMPLE_DOCS:
#     print(doc['text'])
#     tokens = tokenizer.tokenize(doc['text'])
#     print(tokens)
