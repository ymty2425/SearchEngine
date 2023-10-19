import java.io.IOException;
import java.nio.file.Path;

/**
 * A multithread version of inverted index builder.
 * 
 * @author zhengyuan
 */
public class MultiThreadIndexBuilder extends InvertedIndexBuilder {

	/**
	 * Thread safe inverted index
	 */
	private final ThreadSafeInvertedIndex index;

	/**
	 * workqueue
	 */
	private final WorkQueue workQueue;

	/**
	 * Constructor initialize thread safe index and work queue.
	 * 
	 * @param index
	 * @param workQueue
	 */
	public MultiThreadIndexBuilder(ThreadSafeInvertedIndex index, WorkQueue workQueue) {
		super(index);
		this.index = index;
		this.workQueue = workQueue;
	}

	/**
	 * Build the inverted index
	 * 
	 * @param path path found in the args
	 * @throws IOException
	 */
	@Override
	public void buildInvertedIndex(Path path) throws IOException {
		super.buildInvertedIndex(path);
		workQueue.finish();
	}

	@Override
	public void addData(Path path) throws IOException {
		workQueue.execute(new DataAdder(index, path));
	}

	/**
	 * Adding the index of each single file to the inverted index.
	 */
	private class DataAdder implements Runnable {

		/**
		 * single file
		 */
		private final Path path;

		/**
		 * Constructor initialize index and path.
		 * 
		 * @param index the index to build
		 * @param path  the path found in the args
		 */
		public DataAdder(ThreadSafeInvertedIndex index, Path path) {
			this.path = path;
		}

		@Override
		public void run() {
			try {
				InvertedIndex local = new InvertedIndex();
				addData(path, local);
				index.addAll(local);
			} catch (IOException e) {
				System.err.println("Unable to stem file: " + path.toString());
			}

		}
	}
}