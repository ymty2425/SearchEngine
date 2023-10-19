import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

/**
 * Create inverted index for that stores a mapping from a word stem to the
 * file(s) the word was found, and the position(s) in that file the word is
 * located. The positions should start at 1.
 * 
 * @author zhengyuan
 * @version Fall 2019
 */
public class InvertedIndex {

	/**
	 * Stores words, path and positions.
	 */
	private final TreeMap<String, TreeMap<String, TreeSet<Integer>>> index;

	/**
	 * Stores files and total words in that file.
	 */
	private final TreeMap<String, Integer> countMap;

	/**
	 * constructor, initialize index, countMap, and resultMap.
	 */
	public InvertedIndex() {
		this.index = new TreeMap<>();
		this.countMap = new TreeMap<>();
	}

	/**
	 * Created an inverted index structure of a single path to store words, the path
	 * they appear, and position in each of the path.
	 *
	 * @param words    the parsed words in file
	 * @param path     the path that the words appear
	 * @param position the position that the words appear
	 */
	public void add(String words, String path, int position) {
		index.putIfAbsent(words, new TreeMap<>());
		index.get(words).putIfAbsent(path, new TreeSet<>());
		if (index.get(words).get(path).add(position)) {
			countMap.put(path, countMap.getOrDefault(path, 0) + 1);
		}
	}

	/**
	 * Add one index of one single file to inverted index.
	 * 
	 * @param tempIndex the index
	 */
	public void addAll(InvertedIndex tempIndex) {
		for (String word : tempIndex.index.keySet()) {
			if (!index.containsKey(word)) {
				index.put(word, tempIndex.index.get(word));
			} else {
				for (String path : tempIndex.index.get(word).keySet()) {
					if (!index.get(word).containsKey(path)) {
						index.get(word).put(path, tempIndex.index.get(word).get(path));
					} else {
						index.get(word).get(path).addAll(tempIndex.index.get(word).get(path));
					}
				}
			}
		}
		for (String location : tempIndex.countMap.keySet()) {
			if (!index.containsKey(location)) {
				countMap.put(location, tempIndex.countMap.get(location));
			} else {
				countMap.put(location, countMap.getOrDefault(location, 0) + tempIndex.countMap.get(location));
			}
		}
	}

	/**
	 * Returns the number of times a word was found (i.e. the number of locations
	 * associated with a word in the index).
	 *
	 * @param word word to look for
	 * @return number of locations the word was found
	 */
	public int size(String word) {
		return index.get(word) == null ? 0 : index.get(word).size();
	}

	/**
	 * Determines whether the word is stored in the inverted index.
	 *
	 * @param word the word to lookup
	 * @return {@true} if the element is stored in the inverted index
	 */
	public boolean contains(String word) {
		return index.containsKey(word);
	}

	/**
	 * Determines whether the word is stored in the index and the location is stored
	 * for that word.
	 *
	 * @param word     the word to lookup
	 * @param location the location of that word to lookup
	 * @return {@true} if the word and location is stored in the inverted index
	 */
	public boolean contains(String word, String location) {
		if (!contains(word)) {
			return false;
		} else {
			return index.get(word).containsKey(location);
		}
	}

	/**
	 * Determines whether the word is stored in the index and the position is stored
	 * for that word in that path.
	 *
	 * @param word     the word to lookup
	 * @param location the location to lookup
	 * @param position the position of that word to lookup
	 * @return {@true} if the word and position is stored in the inverted index
	 */
	public boolean contains(String word, String location, int position) {
		if (!contains(word, location)) {
			return false;
		} else {
			return index.get(word).get(location).contains(position);
		}
	}

	/**
	 * Returns an unmodifiable view of the words stored in the inverted index.
	 *
	 * @return an unmodifiable view of the words stored in the inverted index
	 * @see Collections#unmodifiableCollection(Collection)
	 */
	public Collection<String> getWords() {
		return Collections.unmodifiableSet(index.keySet());
	}

	/**
	 * Returns an unmodifiable view of the location stored for that word int the
	 * inverted index.
	 *
	 * @param word the word to lookup
	 * @return an unmodifiable view of the words stored in the inverted index
	 * @see Collections#unmodifiableCollection(Collection)
	 */
	public Collection<String> getLocations(String word) {
		if (!contains(word)) {
			return Collections.emptySet();
		}
		return Collections.unmodifiableSet(index.get(word).keySet());
	}

	/**
	 * Returns an unmodifiable view of the positions stored in the inverted index
	 * for the provided word, or an empty collection if the word is not in the
	 * inverted index.
	 *
	 * @param word     the word to lookup
	 * @param location the location to lookup
	 * @return an unmodifiable view of the positions stored for the word
	 * @see Collections#unmodifiableCollection(Collection)
	 */
	public Collection<Integer> getPositions(String word, String location) {
		if (!contains(word, location)) {
			return Collections.emptySet();
		}
		return Collections.unmodifiableSet(index.get(word).get(location));
	}

	/**
	 * Get the word count stored for that path.
	 * 
	 * @param location the location that words store
	 * @return the word count for that location
	 */
	public int getCount(String location) {
		return countMap.getOrDefault(location, 0);
	}

	/**
	 * Write count map in a Json format file.
	 *
	 * @param filename the filename found in args.
	 * @throws IOException
	 *
	 */
	public void writeCountJson(Path filename) throws IOException {
		JsonWriter.asObject(countMap, filename);
	}

	/**
	 * Write index in a Json format file.
	 *
	 * @param path the path found in args.
	 * @throws IOException
	 */
	public void writeIndexJson(Path path) throws IOException {
		JsonWriter.outputFiles(index, path);
	}

	/**
	 * Search helper method
	 *
	 * @param resultMap resultMap
	 * @param word      word
	 * @param list      list
	 */
	private void searchHelper(HashMap<String, Result> resultMap, String word, ArrayList<Result> list) {
		for (String path : index.get(word).keySet()) {
			if (!resultMap.containsKey(path)) {
				Result result = new Result(path);
				resultMap.put(path, result);
				list.add(result);
			}
			resultMap.get(path).update(word);
		}
	}

	/**
	 * Perform exact search results from the inverted index, such that any word stem
	 * in the inverted index that exactly matches a query word is returned.
	 *
	 * @param queries the queries to lookup
	 * @return return exact search results from the inverted index
	 */
	public ArrayList<Result> searchExact(Set<String> queries) {
		ArrayList<Result> resultList = new ArrayList<>();
		HashMap<String, Result> wordCountMap = new HashMap<>();
		for (String queryWord : queries) {
			if (index.containsKey(queryWord)) {
				searchHelper(wordCountMap, queryWord, resultList);
			}
		}
		Collections.sort(resultList);
		return resultList;
	}

	/**
	 * Perform partial search results from the inverted index, such that any word
	 * stem in the inverted index that starts with a query word is returned
	 *
	 * @param queries the queries to lookup
	 * @return return partial search results from the inverted index
	 */
	public ArrayList<Result> searchPartial(Set<String> queries) {
		ArrayList<Result> resultList = new ArrayList<>();
		HashMap<String, Result> wordCountMap = new HashMap<>();
		for (String queryWord : queries) {
			for (String word : index.tailMap(queryWord).keySet()) {
				if (word.startsWith(queryWord)) {
					searchHelper(wordCountMap, word, resultList);
				} else {
					break;
				}
			}
		}
		Collections.sort(resultList);
		return resultList;
	}

	/**
	 * Determine whether perform exact search or partial search.
	 * 
	 * @param queries the queries to lookup
	 * @param exact   whether it is exact
	 * @return {@code true} if it is a exact search
	 */
	public ArrayList<Result> search(Set<String> queries, boolean exact) {
		return exact ? searchExact(queries) : searchPartial(queries);
	}

	@Override
	public String toString() {
		return index.toString();
	}

	/**
	 * Record the total number of word stems in each text file, the total number of
	 * times any of the matching query words appear in the text file the score of
	 * the search result as the percent of words in the file that match the query
	 *
	 * @author zhengyuan
	 */
	public class Result implements Comparable<Result> {

		/**
		 * the location of words
		 */
		private final String location;

		/**
		 * the total number of times any of the matching query words appear in the text
		 * file
		 */
		private int count;

		/**
		 * the score of the search result as the percent of words in the file that match
		 * the query
		 */
		private double score;

		/**
		 * constructor, initialize location, count, total, and score
		 * 
		 * @param location the location word stores
		 */
		public Result(String location) {
			this.location = location;
			this.count = 0;
			this.score = 0;
		}

		/**
		 * Returns the score for this result.
		 * 
		 * @return the score
		 */
		public double getScore() {
			return score;
		}

		/**
		 * Return the location for this result
		 * 
		 * @return the location
		 */
		public String getLocation() {
			return location;
		}

		/**
		 * Return the count of how many matches for this result
		 * 
		 * @return the count
		 */
		public Integer getCount() {
			return count;
		}

		/**
		 * Update count and score for this result
		 * 
		 * @param word the word for this result
		 */
		private void update(String word) {
			this.count += index.get(word).get(location).size();
			this.score = (double) this.count / countMap.get(this.location);
		}

		@Override
		public int compareTo(Result other) {
			if (this.score > other.score) {
				return -1;
			} else if (this.score < other.score) {
				return 1;
			}
			if (this.getCount() > other.getCount()) {
				return -1;
			} else if (this.getCount() < other.getCount()) {
				return 1;
			}
			if (this.getLocation().compareTo(other.getLocation()) > 0) {
				return 1;
			} else if (this.getLocation().compareTo(other.getLocation()) < 0) {
				return -1;
			}
			return 0;
		}

	}
}