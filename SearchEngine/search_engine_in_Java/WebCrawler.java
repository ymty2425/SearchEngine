import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashSet;

import opennlp.tools.stemmer.snowball.SnowballStemmer;

/**
 * 
 */

/**
 * @author zhengyuan
 *
 */
/**
 * Crawl the seed url base on given limit
 */
public class WebCrawler {

	private final HashSet<URL> urlSet;
	private final WorkQueue queue;
	private final ThreadSafeInvertedIndex index;

	public WebCrawler(WorkQueue queue, ThreadSafeInvertedIndex threadIndex) {
		this.queue = queue;
		this.urlSet = new HashSet<URL>();
		this.index = threadIndex;
	}

	/**
	 * Crawl the given seed
	 * 
	 * @param seed  url seed
	 * @param limit the maximum number of url to crawl
	 */
	public void crawl(URL seed, int limit) {
		urlSet.add(seed);
		queue.execute(new WebCrawlerTask(seed, limit));
		queue.finish();
	}

	/**
	 * Crawl the url and the link in this url if the limit has not exceeded
	 */
	private class WebCrawlerTask implements Runnable {

		private final URL url;
		private final int limit;

		public WebCrawlerTask(URL url, int limit) {
			this.url = url;
			this.limit = limit;
		}

		@Override
		public void run() {
			try {
				var html = HtmlFetcher.fetch(url, 3);
				if (html == null) {
					return;
				}
				InvertedIndex temp = new InvertedIndex();
				var stemmer = new SnowballStemmer(SnowballStemmer.ALGORITHM.ENGLISH);
				int start = 1;
				for (String word : TextParser.parse(HtmlCleaner.stripHtml(html))) {
					temp.add(stemmer.stem(word).toString(), url.toString(), start++);
				}
				index.addAll(temp);
				if (urlSet.size() < limit) {
					ArrayList<URL> links = LinkParser.listLinks(url, html.toString());
					for (URL link : links) {
						synchronized (urlSet) {
							if (urlSet.size() >= limit) {
								break;
							} else {
								if (!urlSet.contains(link)) {
									urlSet.add(link);
									queue.execute(new WebCrawlerTask(link, limit));
								}
							}
						}
					}
				}
			} catch (IOException e) {
				System.err.println("Unable to read the page: " + url.toString());
			}
		}
	}
}