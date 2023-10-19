import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Set;

/**
 * A thread-safe version of {@link InvertedIndex} using a read/write lock.
 *
 * @see InvertedIndex
 * @see SimpleReadWriteLock
 */
public class ThreadSafeInvertedIndex extends InvertedIndex {

	/** The lock used to protect concurrent access to the underlying set. */
	private final SimpleReadWriteLock lock;

	/**
	 * Initializes an unsorted thread-safe indexed set.
	 */
	public ThreadSafeInvertedIndex() {
		super();
		this.lock = new SimpleReadWriteLock();
	}

	@Override
	public void add(String word, String path, int position) {
		lock.writeLock().lock();

		try {
			super.add(word, path, position);
		} finally {
			lock.writeLock().unlock();
		}
	}

	@Override
	public void addAll(InvertedIndex index) {
		lock.writeLock().lock();
		try {
			super.addAll(index);
		} finally {
			lock.writeLock().unlock();
		}
	}

	@Override
	public int size(String word) {
		lock.readLock().lock();

		try {
			return super.size(word);
		} finally {
			lock.readLock().unlock();
		}
	}

	@Override
	public boolean contains(String word) {
		lock.readLock().lock();

		try {
			return super.contains(word);
		} finally {
			lock.readLock().unlock();
		}
	}

	@Override
	public boolean contains(String word, String location) {
		lock.readLock().lock();

		try {
			return super.contains(word, location);
		} finally {
			lock.readLock().unlock();
		}
	}

	@Override
	public boolean contains(String word, String location, int position) {
		lock.readLock().lock();

		try {
			return super.contains(word, location, position);
		} finally {
			lock.readLock().unlock();
		}
	}

	@Override
	public Collection<String> getWords() {
		lock.readLock().lock();

		try {
			return super.getWords();
		} finally {
			lock.readLock().unlock();
		}
	}

	@Override
	public Collection<String> getLocations(String word) {
		lock.readLock().lock();

		try {
			return super.getLocations(word);
		} finally {
			lock.readLock().unlock();
		}
	}

	@Override
	public Collection<Integer> getPositions(String word, String location) {
		lock.readLock().lock();

		try {
			return super.getPositions(word, location);
		} finally {
			lock.readLock().unlock();
		}
	}

	@Override
	public String toString() {
		lock.readLock().lock();

		try {
			return super.toString();
		} finally {
			lock.readLock().unlock();
		}
	}

	@Override
	public int getCount(String location) {
		lock.readLock().lock();

		try {
			return super.getCount(location);
		} finally {
			lock.readLock().unlock();
		}
	}

	@Override
	public void writeCountJson(Path filename) throws IOException {
		lock.readLock().lock();

		try {
			super.writeCountJson(filename);
		} finally {
			lock.readLock().unlock();
		}
	}

	@Override
	public void writeIndexJson(Path filename) throws IOException {
		lock.readLock().lock();

		try {
			super.writeIndexJson(filename);
		} finally {
			lock.readLock().unlock();
		}
	}

	@Override
	public ArrayList<Result> searchExact(Set<String> queryList) {
		lock.readLock().lock();

		try {
			return super.searchExact(queryList);
		} finally {
			lock.readLock().unlock();
		}
	}

	@Override
	public ArrayList<Result> searchPartial(Set<String> queryList) {
		lock.readLock().lock();

		try {
			return super.searchPartial(queryList);
		} finally {
			lock.readLock().unlock();
		}
	}
}