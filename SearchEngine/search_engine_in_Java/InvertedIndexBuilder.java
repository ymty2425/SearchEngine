import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Iterator;

import opennlp.tools.stemmer.snowball.SnowballStemmer;

/**
 * traverse directories and parse each file to build inverted index
 * 
 * @author zhengyuan
 */
public class InvertedIndexBuilder {

	/**
	 * Index to build.
	 */
	private final InvertedIndex index;

	/**
	 * Constructor initialize index.
	 * 
	 * @param index the index to build
	 */
	public InvertedIndexBuilder(InvertedIndex index) {
		this.index = index;
	}

	/**
	 * traverse the directory and add each file to build inverted index.
	 * 
	 * @param path the path found in the args
	 * @throws IOException
	 */
	public void buildInvertedIndex(Path path) throws IOException {
		recursiveBuild(path);
	}

	/**
	 * traverse the directory and add each file to build inverted index.
	 * 
	 * @param path the path found in the args
	 * @throws IOException
	 */
	private void recursiveBuild(Path path) throws IOException {
		if (Files.isDirectory(path)) {
			try (DirectoryStream<Path> list = Files.newDirectoryStream(path)) {
				Iterator<Path> directoryStreamIt = list.iterator();
				while (directoryStreamIt.hasNext()) {
					recursiveBuild(directoryStreamIt.next());
				}
			}
		} else if (isTextFile(path)) {
			addData(path);
		}
	}

	/**
	 * Handle 1 file, parse and stem words per line, then add data to inverted index
	 * structure.
	 * 
	 * @param path the path found in the args
	 * @throws IOException
	 */
	public void addData(Path path) throws IOException {
		addData(path, this.index);
	}

	/**
	 * Check whether the file is text file.
	 *
	 * @param path the path after traversing
	 * @return {@true} if the path is a text file
	 */
	public static boolean isTextFile(Path path) {
		String filename = path.toString().toLowerCase();
		return filename.endsWith(".txt") || filename.endsWith(".text");
	}

	/**
	 * Handle 1 file, parse and stem words per line, then add data to inverted index
	 * structure.
	 *
	 * @param filename the file to parse
	 * @param index    the index store parsed words
	 * @throws IOException
	 */
	public static void addData(Path filename, InvertedIndex index) throws IOException {
		SnowballStemmer stemmer = new SnowballStemmer(SnowballStemmer.ALGORITHM.ENGLISH);
		try (BufferedReader reader = Files.newBufferedReader(filename, StandardCharsets.UTF_8)) {
			String line = null;
			int indexcount = 1;
			String file = filename.toString();
			while ((line = reader.readLine()) != null) {
				String[] parsedwords = TextParser.parse(line);
				for (String words : parsedwords) {
					index.add(stemmer.stem(words).toString(), file, indexcount);
					indexcount++;
				}
			}
		}
	}
}
