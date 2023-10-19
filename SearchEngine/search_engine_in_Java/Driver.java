import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.file.Path;

/**
 * Class responsible for running this project based on the provided command-line
 * arguments. See the README for details.
 *
 * @author CS 212 Software Development
 * @author University of San Francisco
 * @version Fall 2019
 */
public class Driver {

	/**
	 * Initializes the classes necessary based on the provided command-line
	 * arguments. This includes (but is not limited to) how to build or search an
	 * inverted index.
	 *
	 * @param args flag/value pairs used to start this program
	 */
	public static void main(String[] args) {
		ArgumentParser parser = new ArgumentParser(args);
		InvertedIndex index = null;
		ThreadSafeInvertedIndex threadIndex = null;
		InvertedIndexBuilder indexBuilder = null;
		QueryInterface queryParser;
		WorkQueue queue = null;
		int threads = 1;
		Boolean threadNeed = parser.hasFlag("-threads");
		WebCrawler webCrawler = null;
		SearchEngine searchEngine = null;

		if (parser.hasFlag("-url") || parser.hasFlag("-port")) {
			threadNeed = true;
		}

		if (threadNeed) {
			threadIndex = new ThreadSafeInvertedIndex();
			threads = Integer.parseInt(parser.getString("-threads", "5"));
			queue = new WorkQueue(threads);
			index = threadIndex;
			indexBuilder = new MultiThreadIndexBuilder(threadIndex, queue);
			queryParser = new MultiThreadQueryParser(queue, threadIndex);
			webCrawler = new WebCrawler(queue, threadIndex);
		} else {
			index = new InvertedIndex();
			queryParser = new QueryParser(index);
			indexBuilder = new InvertedIndexBuilder(index);
			queue = null;
		}

		if (parser.hasFlag("-url")) {
			String seedStr = parser.getString("-url");
			URL seed;
			int limit;
			try {
				seed = new URL(parser.getString("-url"));
				limit = Integer.parseInt(parser.getString("-limit", "50"));
			} catch (MalformedURLException e) {
				System.err.println("Illegal url: " + seedStr + " please check your argument");
				return;
			} catch (NumberFormatException numEx) {
				System.err.println("Illegal limit number: " + parser.getString("-limit", "50"));
				return;
			}
			webCrawler.crawl(seed, limit);
		}

		if (parser.hasFlag("-path")) {
			Path path = parser.getPath("-path");

			if (path == null) {
				System.out.println("Missing value for the -path flag");
				return;
			}
			try {
				indexBuilder.buildInvertedIndex(path);
			} catch (IOException e) {
				System.err.print("Unable to build the inverted index at: " + path.toString());
			}
		}

		if (parser.hasFlag("-index")) {
			Path path = parser.getPath("-index", Path.of("index.json"));
			try {
				index.writeIndexJson(path);
			} catch (IOException e) {
				System.err.print("Unable to write the inverted index to JSON file at: " + path.toString());
			}
		}

		if (parser.hasFlag("-counts")) {
			Path path = parser.getPath("-counts", Path.of("counts.json"));
			try {
				index.writeCountJson(path);
			} catch (IOException e) {
				System.err.print("Unable to write the count map to JSON file at: " + path.toString());
			}

		}

		if (parser.hasFlag("-port")) {
			int port = Integer.parseInt(parser.getString("-port", "8080"));
			searchEngine = new SearchEngine(threadIndex, port);
			try {
				searchEngine.start();
			} catch (Exception e) {
				System.err.println("Exception happened.");
			}
		}

		if (parser.hasFlag("-query")) {
			Path path = parser.getPath("-query");

			if (path == null) {
				System.out.println("Missing value for the -query flag");
				return;
			}
			boolean exact = parser.hasFlag("-exact");

			try {
				queryParser.search(path, exact);
			} catch (IOException e) {
				System.err.print("Unable to search file at: " + path.toString());
			}
		}

		if (parser.hasFlag("-results")) {
			Path path = parser.getPath("-results", Path.of("results.json"));
			try {
				queryParser.writeResultJson(path);
			} catch (IOException e) {
				System.err.print("Unable to write the result map to JSON file at: " + path.toString());
			}
		}

		if (queue != null) {
			queue.shutdown();
		}

	}
}