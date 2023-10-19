import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Map;
import java.util.TreeMap;
import java.util.TreeSet;

/**
 * A multithread version of query parser.
 * 
 * @author zhengyuan
 */
public class MultiThreadQueryParser implements QueryInterface {

	/**
	 * workqueue
	 */
	private final WorkQueue queue;

	/**
	 * Stores search word and its result list
	 */
	private final Map<String, ArrayList<InvertedIndex.Result>> resultMap;

	/**
	 * Thread safe inverted index
	 */
	private final ThreadSafeInvertedIndex threadIndex;

	/**
	 * Constructor initialize work queue and thread safe index.
	 * 
	 * @param queue
	 * @param threadIndex
	 */
	public MultiThreadQueryParser(WorkQueue queue, ThreadSafeInvertedIndex threadIndex) {
		this.resultMap = new TreeMap<>();
		this.threadIndex = threadIndex;
		this.queue = queue;
	}

	/**
	 * Read each line from the path found in the args, and perform search function
	 * 
	 * @param path  the path found in the args
	 * @param exact if it is exact search or partial search
	 * @throws IOException
	 */
	@Override
	public void search(Path path, boolean exact) throws IOException {
		QueryInterface.super.search(path, exact);
		queue.finish();
	}

	/**
	 * Read each line from the path found in the args, and perform search function.
	 * 
	 * @param line  the line to look up
	 * @param exact if it is exact search or partial search
	 */
	@Override
	public void search(String line, boolean exact) {
		queue.execute(new QueryLineTask(line, exact));
	}

	/**
	 * write exact or partial result map in a Json format file.
	 *
	 * @param path the path found in args.
	 * @throws IOException
	 */
	@Override
	public void writeResultJson(Path path) throws IOException {
		synchronized (resultMap) {
			JsonWriter.asResultObject(resultMap, path);
		}
	}

	/**
	 * Parse each line and perform search
	 */
	private class QueryLineTask implements Runnable {

		/**
		 * line to parse
		 */
		private String line;

		/**
		 * whether is exact search or partial search
		 */
		private boolean exact;

		/**
		 * Thread safe inverted index
		 * 
		 * @param line
		 * @param exact
		 */
		public QueryLineTask(String line, boolean exact) {
			this.line = line;
			this.exact = exact;
		}

		@Override
		public void run() {
			TreeSet<String> stems = TextFileStemmer.uniqueStems(line);
			if (stems.isEmpty()) {
				return;
			}
			String queryline = String.join(" ", stems);
			synchronized (resultMap) {
				if (resultMap.containsKey(queryline)) {
					return;
				}
			}
			var result = threadIndex.search(stems, exact);
			synchronized (resultMap) {
				resultMap.put(queryline, result);
			}
		}
	}

}