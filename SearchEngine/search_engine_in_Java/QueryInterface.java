import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * the interface for one thread query search and multi-thread query search.
 * 
 * @author zhengyuan
 */
public interface QueryInterface {

	/**
	 * the search general output method
	 * 
	 * @param path of queries
	 * @throws IOException
	 */
	void writeResultJson(Path path) throws IOException;

	/**
	 * the search general search method
	 * 
	 * @param path  of queries
	 * @param exact search methods
	 * @throws IOException
	 */
	public default void search(Path path, boolean exact) throws IOException {
		try (BufferedReader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8);) {
			String line = null;
			while ((line = reader.readLine()) != null) {
				search(line, exact);
			}
		}
	}

	/**
	 * Read each line from the path found in the args, and perform search function
	 * 
	 * @param line  the line to look up
	 * @param exact whether it is exact or not
	 */
	public void search(String line, boolean exact);
}
