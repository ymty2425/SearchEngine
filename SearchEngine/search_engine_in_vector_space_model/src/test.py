from document_preprocessor import SpaCyTokenizer, RegexTokenizer, SplitTokenizer
from indexing import Indexer, InvertedIndex, BasicInvertedIndex, IndexType
import time
import json

SAMPLE_DOCS = [{'docid': 31740,
         'text': 'The University of Michigan (U-M, UMich, or just Michigan) is a public research university in Ann Arbor, Michigan, United States. Founded in 1817, the university is the oldest and largest in Michigan; it was established twenty years before the territory became a state. Michigan is a founding member of the Association of American Universities. Since 1871, Michigan has been a coeducational institution. Today it enrolls approximately 32,000 undergraduate students and 18,000 graduate students.'},
        {'docid': 302260,
         'text': 'Wayne State University (WSU or simply Wayne) is a public research university in Detroit, Michigan. It is Michigan\'s third-largest university. Founded in 1868, Wayne State consists of 13 schools and colleges offering approximately 350 programs to nearly 24,000 graduate and undergraduate students. Wayne State is classified among "R1: Doctoral Universities ? Very high research activity".'},
        {'docid': 30608136,
         'text': 'Ann Arbor is a city in the U.S. state of Michigan and the seat of government of Washtenaw County. The 2020 census recorded its population to be 123,851, making it the fifth-largest city in Michigan. It is the principal city of the Ann Arbor Metropolitan Statistical Area, which encompasses all of Washtenaw County. Ann Arbor is also included in the Greater Detroit Combined Statistical Area and the Great Lakes megalopolis, the most populated and largest megalopolis in North America. Ann Arbor is home to the University of Michigan. The university significantly shapes Ann Arbor\'s economy as it employs about 30,000 workers, including about 12,000 in its medical center. The city\'s economy is also centered on high technology, with several companies drawn to the area by the university\'s research and development infrastructure.'}, 
        {'docid': 463734,
         'text': 'The definition of health is vague and there are many conceptualizations. Public health practitioners definition of health can different markedly from members of the public or clinicians. This can mean that members of the public view the values behind public health interventions as alien which can cause resentment amongst the public towards certain interventions. Such vagueness can be a problem for health promotion. Critics have argued that public health tends to place more focus on individual factors associated with health at the expense of factors operating at the population level.'}, 
        {'docid': 17948, 
         'text': 'Lake Michigan is the only one of the five Great Lakes located fully in the United States; the other four are shared between the United States and Canada. Lake Michigan is the world\'s largest lake by area located fully in one country. It is shared, from west to east, by the U.S. states of Wisconsin, Illinois, Indiana, and Michigan. Ports along its shores include Chicago in Illinois, Gary in Indiana, Milwaukee and Green Bay in Wisconsin, and Muskegon in Michigan.'},
        {'docid': 4877703,
         'text': 'The University of Michigan School of Information (UMSI or iSchool) is the informatics and information science school of the University of Michigan, a public research university in Ann Arbor, Michigan.'}, 
        {'docid': 22329761, 
         'text': 'The United States is serviced by a wide array of public transportation, including various forms of bus, rail, ferry, and sometimes, airline services. Most established public transit systems are located in central, urban areas where there is enough density and public demand to require public transportation. In more auto-centric suburban localities, public transit is normally, but not always, less frequent and less common. Most public transit services in the United States are either national, regional/commuter, or local, depending on the type of service. Sometimes "public transportation" in the United States is an umbrella term used synonymously with "alternative transportation", meaning any form of mobility that excludes driving alone by automobile.'},
        {'docid': 52751551, 
         'text': 'Cherry production in Michigan is a major part of the agriculture industry in the state. Harvesting over 90,000 tons of cherries each year, Michigan is the nation\'s leading producer of tart cherries. The Montmorency cherry is the variety of tart, or sour, cherry most commonly grown in the state. A Hungarian sour cherry cultivar, Balaton, has been commercially produced in Michigan since 1998. Michigan\'s cherry industry is highly vulnerable to a late spring frost, which can wipe out a season\'s harvest. This occurred most recently in 2012, when over 90% of the crop was lost.'},
        {'docid': 1640986, 
         'text': 'A public university or public college is a university or college that is owned by the state or receives significant funding from a government. Whether a national university is considered public varies from one country (or region) to another, largely depending on the specific education landscape.'},
        {'docid': 241128, 
         'text': 'Michigan State University (Michigan State or MSU) is a public land-grant research university in East Lansing, Michigan. It was founded in 1855 as the Agricultural College of the State of Michigan, the first of its kind in the United States. After the introduction of the Morrill Act in 1862, the state designated the college a land-grant institution in 1863, making it the first of the land-grant colleges in the United States. The college became coeducational in 1870. In 1955, the state officially made the college a university, and the current name was adopted in 1964. Today, Michigan State has rapidly expanded its footprint across the state of Michigan with facilities all across the state and one of the largest collegiate alumni networks with 634,000 members.'}]

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

FILE_PATH = "wikipedia_1M_dataset.jsonl"
MULTIWORD_PATH = "multi_word_expressions.txt"

# Initialize the Tokenizer
tokenizer = SpaCyTokenizer(MULTIWORD_PATH)
reTokenizer = RegexTokenizer(MULTIWORD_PATH)
sTokenizer = SplitTokenizer(MULTIWORD_PATH)

stopword_filtering = True
minimum_word_frequency = 2
# Tokenize a sample text
# tokens = reTokenizer.tokenize("RegexTokenizer can split on punctuation like this: test!")
# print(tokens)

tokens = ['Apple', 'is', 'the', 'company', 'with', 'apple', 'logo.']

# Your data
data = [
    {'docid': 31740, 'text': 'apple apple apple apple apple apple'},
    {'docid': 302260, 'text': 'cat dog cat dog bird bird'}
]

# with open('test.jsonl', 'w', encoding='utf-8') as file:
#     for entry in data:
#         json_str = json.dumps(entry)
#         file.write(json_str + "\n")  


# index = Indexer.create_index('my_index', IndexType.OnDiskInvertedIndex, "test.jsonl", reTokenizer,
#                                     stopword_filtering, minimum_word_frequency)

TEST_PATH = "test.jsonl"

stopword_filtering = True

document_preprocessor = RegexTokenizer(MULTIWORD_PATH)

# index = Indexer.create_index('BasicInvertedIndex', IndexType.InvertedIndex, TEST_PATH, document_preprocessor, stopword_filtering, 2)

# # index.add_doc(31750, ["The", "quick", "fox", "jumps", "over", "the", "lazy", "dog"])
# index.remove_doc(31740)
# print_result(index)
# index.load()
# print(index.get_postings("apple"))
# print_result(index)

# times = 0
# FILE_PATH_JSON = "wikipedia_1M_dataset.jsonl"x

# start_time = time.time()
# with open(FILE_PATH_JSON, 'r') as file:
#     for i, line in enumerate(file):
            
#         doc = json.loads(line)
#         print(doc['text'])
        
#         sTokenizer.tokenize(doc['text'])
#         break
# end_time = time.time()
# times = end_time - start_time
# print(times)
