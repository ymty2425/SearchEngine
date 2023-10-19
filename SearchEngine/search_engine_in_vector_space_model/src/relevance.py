import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

def map_score(actual, cut_off=10):
    # TODO Implement MAP score metric
    # Here you calculate the Mean Average Precision score for each query
    precisions = []
    relevant_docs = 0
    
    for rank, relevance in enumerate(actual[:cut_off]):
        if relevance in [1, 2]:  # Check if the document is relevant
            relevant_docs += 1
            precisions.append(relevant_docs / (rank + 1))
    
    # Ensure division is not performed by zero
    return sum(precisions) / len(precisions) if precisions else 0

def dcg_at_k(r, k):
    """Compute DCG@k for a list of relevance scores"""
    r = np.asfarray(r)[:k]
    if r.size:
        return np.sum(np.subtract(np.power(2, r), 1) / np.log2(np.arange(2, r.size + 2)))
    return 0

def ndcg_score(actual, ideal, cut_off=10):
    # TODO Implement NDCG score metric
    # Here you calculate the Normalized Discounted Cumulative Gain score for each query
    
    dcg_max = dcg_at_k(sorted(ideal, reverse=True), cut_off)
    if not dcg_max:
        return 0
    return dcg_at_k(actual, cut_off) / dcg_max

def run_relevance_tests(algorithm):
    # TODO Implement running relevance test for the whole search system for multiple queries
    '''
    This function is responsible for measuring the the performance of the whole system using metrics such as MAP and NDCG.
    
    Parameters:
    
    algorithm: This is the overall algorithm used by the system to search through the document collection.
    '''
    # 1. Load the relevance dataset.
    # 2. Run all of the dataset queries on the search algorithm.
    # 3. Get the MAP and NDCG for every single query and average them out.
    # 4. Return the scores to the calling function.
    relevance_data_path = 'relevance.csv'
    relevance_data = pd.read_csv(relevance_data_path)
    
    map_scores = []
    ndcg_scores = []

    for query_number, query in enumerate(relevance_data['query'].unique()):
        ranked_docs = algorithm.query(query)
        
        actual = [
            relevance_data.loc[
                (relevance_data['query'] == query) & 
                (relevance_data['docid'] == doc_id), 'rel'
            ].values[0] if doc_id in relevance_data['docid'].values else 0 
            for doc_id in ranked_docs
        ]

        ideal = sorted(actual, reverse=True)
        
        map_scores.append(map_score(actual))
        ndcg_scores.append(ndcg_score(actual, ideal))

    # Compute average MAP and NDCG across all queries
    avg_map = np.mean(map_scores)
    avg_ndcg = np.mean(ndcg_scores)
    
    return {'map': avg_map, 'ndcg': avg_ndcg}


def run_best_relevance_tests(algorithm):
    relevance_data_path = 'relevance.csv'
    relevance_data = pd.read_csv(relevance_data_path)
    
    query_scores = []
    
    for query in relevance_data['query'].unique():
        ranked_docs = algorithm.query(query)
        
        actual = [
            relevance_data.loc[
                (relevance_data['query'] == query) & 
                (relevance_data['docid'] == doc_id), 'rel'
            ].values[0] if doc_id in relevance_data['docid'].values else 0 
            for doc_id in ranked_docs
        ]
        ideal = sorted(actual, reverse=True)
        
        query_map = map_score(actual)
        query_ndcg = ndcg_score(actual, ideal)
        
        query_scores.append({'query': query, 'map': query_map, 'ndcg': query_ndcg})
    
    return query_scores

# TODO Score each of the ranking functions on the data we provide. Use the default
# hyperparameters in the code. Plot these scores on the y-axis and relevance function on the
# x-axis using a bar plot. Use different hues for each metric.

# TODO For the best-performing relevance function, calculate
# the MAP and NDCG scores for each query individually and plot these. Use the default
# hyperparameters in the code. Plot these scores on the y-axis and query number on the
# x-axis using a bar plot (i.e., one bar per query).

if __name__ == '__main__':
    # NOTE: You can use this file on your command line by running 'python relevance.py'
    # from pipeline import initialize
    # algorithm = initialize()
    # print(run_relevance_tests(algorithm))
    from document_preprocessor import RegexTokenizer
    from indexing import Indexer, IndexType
    from ranker import Ranker, WordCountCosineSimilarity, DirichletLM, BM25, PivotedNormalization, TF_IDF, YourRanker

    FILE_PATH = "wikipedia_1M_dataset.jsonl"
    MULTIWORD_PATH = "multi_word_expressions.txt"
    TEST_PATH = "test.jsonl"

    stopword_filtering = True

    document_preprocessor = RegexTokenizer(MULTIWORD_PATH)
    
    print("step 1")
    
    index = Indexer.create_index('BasicInvertedIndex1', IndexType.InvertedIndex, TEST_PATH, document_preprocessor, stopword_filtering, 2)

    print("step 2")

    rankers = {
        "WordCountCosineSimilarity": Ranker(index, document_preprocessor, stopword_filtering, WordCountCosineSimilarity(index, {})),
        "DirichletLM": Ranker(index, document_preprocessor, stopword_filtering, DirichletLM(index, {'mu': 0.2})),
        "BM25": Ranker(index, document_preprocessor, stopword_filtering, BM25(index, { 'b': 0.75,'k1': 1.2,'k3': 8 })),
        "PivotedNormalization": Ranker(index, document_preprocessor, stopword_filtering, PivotedNormalization(index, {'b': 0.2})),
        "TF_IDF": Ranker(index, document_preprocessor, stopword_filtering, TF_IDF(index, {})),
        # "OwnRanker": Ranker(index, document_preprocessor, stopword_filtering, YourRanker(index, {'b': 0.75}))
    }
    
    print("Problem 9")

    algorithm_scores = []

    relevance_data_path = 'relevance.csv'
    relevance_data = pd.read_csv(relevance_data_path)
    
    query_scores = {name: [] for name in rankers.keys()}

    avg_scores = {}
    scores_data = []

    for name, algorithm in tqdm(rankers.items()):
        scores = run_relevance_tests(algorithm)
        for metric, score in scores.items():
            scores_data.append({'algorithm': name, 'metric': metric, 'score': score})
    
    df = pd.DataFrame(scores_data)

    plt.figure(figsize=(10, 6))

    sns.barplot(x='algorithm', y='score', hue='metric', data=df)

    plt.title('Performance of Ranking Functions')
    plt.xlabel('Ranking Function')
    plt.ylabel('Score')
    plt.ylim(0, 1)
    plt.xticks(rotation=45)
    plt.legend(title='Metric')
    plt.tight_layout()
    plt.show()

    print("Problem 10")
    best_algorithm = "TF_IDF"

    best_scores = run_best_relevance_tests(rankers.get(best_algorithm))
    # scores_df.to_csv('my_data.csv', index=False)
    scores_df = pd.DataFrame(best_scores)
    
    fig, axes = plt.subplots(2, 1, figsize=(15, 14))

    # Plot MAP scores
    sns.barplot(x='qid', y='map', data=df, ax=axes[0], color='skyblue')
    axes[0].set_title('MAP Scores per Query')
    axes[0].set_xlabel('')
    axes[0].set_ylabel('MAP Score')
    axes[0].tick_params(axis='x', labelrotation=90)

    # Plot NDCG scores
    sns.barplot(x='qid', y='ndcg', data=df, ax=axes[1], color='salmon')
    axes[1].set_title('NDCG Scores per Query')
    axes[1].set_xlabel('Query ID')
    axes[1].set_ylabel('NDCG Score')
    axes[1].tick_params(axis='x', labelrotation=90)

    plt.tight_layout(pad=4.0)

