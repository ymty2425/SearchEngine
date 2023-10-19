import java.io.BufferedWriter;
import java.io.IOException;
import java.io.StringWriter;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.Map;
import java.util.Map.Entry;
import java.util.TreeSet;

/**
 * Outputs several simple data structures in "pretty" JSON format where newlines
 * are used to separate elements and nested elements are indented.
 *
 * Warning: This class is not thread-safe. If multiple threads access this class
 * concurrently, access must be synchronized externally.
 *
 * @author CS 212 Software Development
 * @author University of San Francisco
 * @version Fall 2019
 */
public class JsonWriter {

	/**
	 * Writes the elements as a pretty JSON array.
	 *
	 * @param elements the elements to write
	 * @param writer   the writer to use
	 * @param level    the initial indent level
	 * @throws IOException
	 */
	public static void asResult(InvertedIndex.Result elements, Writer writer, int level) throws IOException {
		DecimalFormat FORMATTER = new DecimalFormat("0.00000000");

		indent("{", writer, level);
		writer.write('\n');
		level++;

		quote("where", writer, level);
		writer.write(": ");
		quote(elements.getLocation(), writer, 0);
		writer.write(",\n");

		quote("count", writer, level);
		writer.write(": ");
		writer.write(elements.getCount().toString());
		writer.write(",\n");

		quote("score", writer, level);
		writer.write(": ");
		writer.write(FORMATTER.format(elements.getScore()));
		writer.write("\n");

		level--;
		indent("}", writer, level);
	}

	/**
	 * Writes the elements as a pretty JSON array to file.
	 *
	 * @param elements the elements to write
	 * @param path     the file path to use
	 * @throws IOException
	 *
	 * @see #asResult(InvertedIndex.Result, Writer, int)
	 */
	public static void asResult(InvertedIndex.Result elements, Path path) throws IOException {
		try (BufferedWriter writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8)) {
			asResult(elements, writer, 0);
		}
	}

	/**
	 * Returns the elements as a pretty JSON array.
	 *
	 * @param elements the elements to use
	 * @return a {@link String} containing the elements in pretty JSON format
	 *
	 * @see #asResult(InvertedIndex.Result, Writer, int)
	 */
	public static String asResult(InvertedIndex.Result elements) {
		try {
			StringWriter writer = new StringWriter();
			asResult(elements, writer, 0);
			return writer.toString();
		} catch (IOException e) {
			return null;
		}
	}

	/**
	 * Writes the elements as a pretty JSON array.
	 *
	 * @param elements the elements to write
	 * @param writer   the writer to use
	 * @param level    the initial indent level
	 * @throws IOException
	 */
	public static void asResultArray(ArrayList<InvertedIndex.Result> elements, Writer writer, int level)
			throws IOException {
		Iterator<InvertedIndex.Result> iterator = elements.iterator();
		writer.write('[');
		if (iterator.hasNext()) {
			writer.write('\n');
			asResult(iterator.next(), writer, level + 1);
		}
		while (iterator.hasNext()) {
			writer.write(',');
			writer.write('\n');
			asResult(iterator.next(), writer, level + 1);
		}
		writer.write('\n');
		indent("]", writer, level);
	}

	/**
	 * Writes the elements as a pretty JSON array to file.
	 *
	 * @param elements the elements to write
	 * @param path     the file path to use
	 * @throws IOException
	 */
	public static void asResultArray(ArrayList<InvertedIndex.Result> elements, Path path) throws IOException {
		try (BufferedWriter writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8)) {
			asResultArray(elements, writer, 0);
		}
	}

	/**
	 * Returns the elements as a pretty JSON array.
	 *
	 * @param elements the elements to use
	 * @return a {@link String} containing the elements in pretty JSON format
	 */
	public static String asResultArray(ArrayList<InvertedIndex.Result> elements) {
		try {
			StringWriter writer = new StringWriter();
			asResultArray(elements, writer, 0);
			return writer.toString();
		} catch (IOException e) {
			return null;
		}
	}

	/**
	 * Help method for asResultObject()
	 *
	 * @param entry  the elements to write
	 * @param writer the writer to use
	 * @param level  the initial indent level
	 * @throws IOException
	 */
	public static void writeResultEntry(Entry<String, ? extends ArrayList<InvertedIndex.Result>> entry, Writer writer,
			int level) throws IOException {
		writer.write('\n');
		quote(entry.getKey(), writer, level);
		writer.write(": ");
		asResultArray(entry.getValue(), writer, level);
	}

	/**
	 * Writes the elements as a nested pretty JSON object. The generic notation used
	 * allows this method to be used for any type of map with any type of nested
	 * collection of integer objects.
	 *
	 * @param elements the elements to write
	 * @param writer   the writer to use
	 * @param level    the initial indent level
	 * @throws IOException
	 */
	public static void asResultObject(Map<String, ArrayList<InvertedIndex.Result>> elements, Writer writer, int level)
			throws IOException {
		writer.write('{');
		var iterator = elements.entrySet().iterator();
		if (iterator.hasNext()) {
			writeResultEntry(iterator.next(), writer, level + 1);
		}
		while (iterator.hasNext()) {
			writer.write(',');
			writeResultEntry(iterator.next(), writer, level + 1);
		}
		writer.write('\n');
		indent("}", writer, level - 1);
	}

	/**
	 * Writes the elements as a nested pretty JSON object to file.
	 *
	 * @param elements the elements to write
	 * @param path     the file path to use
	 * @throws IOException
	 *
	 * @see #asNestedObject(Map, Writer, int)
	 */
	public static void asResultObject(Map<String, ArrayList<InvertedIndex.Result>> elements, Path path)
			throws IOException {
		try (BufferedWriter writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8)) {
			asResultObject(elements, writer, 0);
		}
	}

	/**
	 * Help method for asArray().
	 *
	 * @param i      the integer to write
	 * @param writer the writer to use
	 * @param level  the initial indent level
	 * @throws IOException
	 */
	public static void writeInteger(Integer i, Writer writer, int level) throws IOException {
		writer.write('\n');
		indent(i, writer, level);
	}

	/**
	 * Writes the elements as a pretty JSON array.
	 *
	 * @param elements the elements to write
	 * @param writer   the writer to use
	 * @param level    the initial indent level
	 * @throws IOException
	 */
	public static void asArray(Collection<Integer> elements, Writer writer, int level) throws IOException {
		writer.write('[');
		var iterator = elements.iterator();
		if (iterator.hasNext()) {
			writeInteger(iterator.next(), writer, level + 1);
		}
		while (iterator.hasNext()) {
			writer.write(',');
			writeInteger(iterator.next(), writer, level + 1);
		}
		writer.write('\n');
		indent("]", writer, level);
	}

	/**
	 * Writes the elements as a pretty JSON array to file.
	 *
	 * @param elements the elements to write
	 * @param path     the file path to use
	 * @throws IOException
	 *
	 * @see #asArray(Collection, Writer, int)
	 */
	public static void asArray(Collection<Integer> elements, Path path) throws IOException {
		try (BufferedWriter writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8)) {
			asArray(elements, writer, 0);
		}
	}

	/**
	 * Returns the elements as a pretty JSON array.
	 *
	 * @param elements the elements to use
	 * @return a {@link String} containing the elements in pretty JSON format
	 *
	 * @see #asArray(Collection, Writer, int)
	 */
	public static String asArray(Collection<Integer> elements) {
		try {
			StringWriter writer = new StringWriter();
			asArray(elements, writer, 0);
			return writer.toString();
		} catch (IOException e) {
			return null;
		}
	}

	/**
	 * Help method for asObject().
	 *
	 * @param entry  the elements to write
	 * @param writer the writer to use
	 * @param level  the initial indent level
	 * @throws IOException
	 */
	public static void writeEntry(Entry<String, Integer> entry, Writer writer, int level) throws IOException {
		writer.write('\n');
		quote(entry.getKey(), writer, level);
		writer.write(": ");
		writer.write(entry.getValue().toString());
	}

	/**
	 * Writes the elements as a pretty JSON object.
	 *
	 * @param elements the elements to write
	 * @param writer   the writer to use
	 * @param level    the initial indent level
	 * @throws IOException
	 */
	public static void asObject(Map<String, Integer> elements, Writer writer, int level) throws IOException {
		writer.write('{');
		var iterator = elements.entrySet().iterator();
		if (iterator.hasNext()) {
			writeEntry(iterator.next(), writer, level + 1);
		}
		while (iterator.hasNext()) {
			writer.write(',');
			writeEntry(iterator.next(), writer, level + 1);
		}
		writer.write('\n');
		indent("}", writer, level - 1);
	}

	/**
	 * Writes the elements as a pretty JSON object to file.
	 *
	 * @param elements the elements to write
	 * @param path     the file path to use
	 * @throws IOException
	 *
	 * @see #asObject(Map, Writer, int)
	 */
	public static void asObject(Map<String, Integer> elements, Path path) throws IOException {
		try (BufferedWriter writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8)) {
			asObject(elements, writer, 0);
		}
	}

	/**
	 * Returns the elements as a pretty JSON object.
	 *
	 * @param elements the elements to use
	 * @return a {@link String} containing the elements in pretty JSON format
	 *
	 * @see #asObject(Map, Writer, int)
	 */
	public static String asObject(Map<String, Integer> elements) {
		try {
			StringWriter writer = new StringWriter();
			asObject(elements, writer, 0);
			return writer.toString();
		} catch (IOException e) {
			return null;
		}
	}

	/**
	 * Help method for asNestedObject()
	 *
	 * @param entry  the elements to write
	 * @param writer the writer to use
	 * @param level  the initial indent level
	 * @throws IOException
	 */
	public static void writeNestedEntry(Entry<String, ? extends Collection<Integer>> entry, Writer writer, int level)
			throws IOException {
		writer.write('\n');
		quote(entry.getKey(), writer, level);
		writer.write(": ");
		asArray(entry.getValue(), writer, level);
	}

	/**
	 * Writes the elements as a nested pretty JSON object. The generic notation used
	 * allows this method to be used for any type of map with any type of nested
	 * collection of integer objects.
	 *
	 * @param elements the elements to write
	 * @param writer   the writer to use
	 * @param level    the initial indent level
	 * @throws IOException
	 */
	public static void asNestedObject(Map<String, ? extends Collection<Integer>> elements, Writer writer, int level)
			throws IOException {
		writer.write('{');
		var iterator = elements.entrySet().iterator();
		if (iterator.hasNext()) {
			writeNestedEntry(iterator.next(), writer, level + 1);
		}
		while (iterator.hasNext()) {
			writer.write(',');
			writeNestedEntry(iterator.next(), writer, level + 1);
		}
		writer.write('\n');
		indent("}", writer, level - 1);
	}

	/**
	 * Writes the elements as a nested pretty JSON object to file.
	 *
	 * @param elements the elements to write
	 * @param path     the file path to use
	 * @throws IOException
	 *
	 * @see #asNestedObject(Map, Writer, int)
	 */
	public static void asNestedObject(Map<String, ? extends Collection<Integer>> elements, Path path)
			throws IOException {
		try (BufferedWriter writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8)) {
			asNestedObject(elements, writer, 0);
		}
	}

	/**
	 * Returns the elements as a nested pretty JSON object.
	 *
	 * @param elements the elements to use
	 * @return a {@link String} containing the elements in pretty JSON format
	 *
	 * @see #asNestedObject(Map, Writer, int)
	 */
	public static String asNestedObject(Map<String, ? extends Collection<Integer>> elements) {
		try {
			StringWriter writer = new StringWriter();
			asNestedObject(elements, writer, 0);
			return writer.toString();
		} catch (IOException e) {
			return null;
		}
	}

	/**
	 * Help method for outputFiles().
	 *
	 * @param entry  the elements to write
	 * @param writer the writer to use
	 * @param level  the initial indent level
	 * @throws IOException
	 */
	public static void writeFiles(Entry<String, ? extends Map<String, TreeSet<Integer>>> entry, Writer writer,
			int level) throws IOException {
		writer.write('\n');
		quote(entry.getKey(), writer, level);
		writer.write(": ");
		asNestedObject(entry.getValue(), writer, level);
	}

	/**
	 * Writes the elements as a nested pretty JSON object. The generic notation used
	 * allows this method to be used for any type of map with any type of nested map
	 * of TreeSet objects.
	 *
	 * @param elements the elements to write
	 * @param writer   the writer to use
	 * @param level    the initial indent level
	 * @throws IOException
	 */
	public static void outputFiles(Map<String, ? extends Map<String, TreeSet<Integer>>> elements, Writer writer,
			int level) throws IOException {
		writer.write('{');
		var iterator = elements.entrySet().iterator();
		if (iterator.hasNext()) {
			writeFiles(iterator.next(), writer, level + 1);
		}
		while (iterator.hasNext()) {
			writer.write(',');
			writeFiles(iterator.next(), writer, level + 1);
		}
		writer.write('\n');
		indent("}", writer, level - 1);
	}

	/**
	 * Writes the elements as a nested pretty JSON object to file.
	 *
	 * @param elements the elements to write
	 * @param path     the file path to use
	 * @throws IOException
	 *
	 * @see #outputFiles(Map, Writer, int)
	 */
	public static void outputFiles(Map<String, ? extends Map<String, TreeSet<Integer>>> elements, Path path)
			throws IOException {
		try (BufferedWriter writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8)) {
			outputFiles(elements, writer, 0);
		}
	}

	/**
	 * Returns the elements as a nested pretty JSON object.
	 *
	 * @param elements the elements to use
	 * @return a {@link String} containing the elements in pretty JSON format
	 *
	 * @see #outputFiles(Map, Writer, int)
	 */
	public static String outputFiles(Map<String, ? extends Map<String, TreeSet<Integer>>> elements) {
		try {
			StringWriter writer = new StringWriter();
			outputFiles(elements, writer, 0);
			return writer.toString();
		} catch (IOException e) {
			return null;
		}
	}

	/**
	 * Writes the {@code \t} tab symbol by the number of times specified.
	 *
	 * @param writer the writer to use
	 * @param times  the number of times to write a tab symbol
	 * @throws IOException
	 */
	public static void indent(Writer writer, int times) throws IOException {
		for (int i = 0; i < times; i++) {
			writer.write('\t');
		}
	}

	/**
	 * Indents and then writes the element.
	 *
	 * @param element the element to write
	 * @param writer  the writer to use
	 * @param times   the number of times to indent
	 * @throws IOException
	 *
	 * @see #indent(String, Writer, int)
	 * @see #indent(Writer, int)
	 */
	public static void indent(Integer element, Writer writer, int times) throws IOException {
		indent(element.toString(), writer, times);
	}

	/**
	 * Indents and then writes the element.
	 *
	 * @param element the element to write
	 * @param writer  the writer to use
	 * @param times   the number of times to indent
	 * @throws IOException
	 *
	 * @see #indent(Writer, int)
	 */
	public static void indent(String element, Writer writer, int times) throws IOException {
		indent(writer, times);
		writer.write(element);
	}

	/**
	 * Writes the element surrounded by {@code " "} quotation marks.
	 *
	 * @param element the element to write
	 * @param writer  the writer to use
	 * @throws IOException
	 */
	public static void quote(String element, Writer writer) throws IOException {
		writer.write('"');
		writer.write(element);
		writer.write('"');
	}

	/**
	 * Indents and then writes the element surrounded by {@code " "} quotation
	 * marks.
	 *
	 * @param element the element to write
	 * @param writer  the writer to use
	 * @param times   the number of times to indent
	 * @throws IOException
	 *
	 * @see #indent(Writer, int)
	 * @see #quote(String, Writer)
	 */
	public static void quote(String element, Writer writer, int times) throws IOException {
		indent(writer, times);
		quote(element, writer);
	}
}