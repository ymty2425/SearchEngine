import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Map;
import java.util.TreeMap;
import java.util.TreeSet;

/**
 * Clean and parse each query line, remove duplicate query word stems, and then
 * sort the unique words for each query alphabetically. Then add to search
 * result.
 *
 * @author zhengyuan
 */
public class QueryParser implements QueryInterface {

	/**
	 * Stores search word and its result list
	 */
	private final Map<String, ArrayList<InvertedIndex.Result>> resultMap;

	/**
	 * Stores words in inverted index structure
	 */
	private final InvertedIndex index;

	/**
	 * Initialize constructor
	 * 
	 * @param index the index used for searching
	 */
	public QueryParser(InvertedIndex index) {
		this.resultMap = new TreeMap<>();
		this.index = index;
	}

	/**
	 * Get result map
	 * 
	 * @return return resultMap
	 */
	public Map<String, ArrayList<InvertedIndex.Result>> getResult() {
		return this.resultMap;
	}

	/**
	 * Clean and parse a single line, then Perform exact or partial search results
	 * from the inverted index,
	 * 
	 * @param line  the line to clean and parse
	 * @param exact if it is exact search or partial search
	 */
	@Override
	public void search(String line, boolean exact) {
		TreeSet<String> stems = TextFileStemmer.uniqueStems(line);
		if (stems.isEmpty()) {
			return;
		}
		String joined = String.join(" ", stems);
		if (resultMap.containsKey(joined)) {
			return;
		}
		resultMap.put(joined, index.search(stems, exact));
	}

	/**
	 * write exact or partial result map in a Json format file.
	 *
	 * @param path the path found in args.
	 * @throws IOException
	 */
	@Override
	public void writeResultJson(Path path) throws IOException {
		JsonWriter.asResultObject(resultMap, path);
	}
}
