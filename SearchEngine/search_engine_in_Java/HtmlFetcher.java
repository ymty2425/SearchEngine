import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.MalformedURLException;
import java.net.Socket;
import java.net.URL;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * A specialized version of {@link HttpsFetcher} that follows redirects and
 * returns HTML content if possible.
 *
 * @see HttpsFetcher
 */
public class HtmlFetcher {

	/**
	 * Returns {@code true} if and only if there is a "Content-Type" header and the
	 * first value of that header starts with the value "text/html"
	 * (case-insensitive).
	 *
	 * @param headers the HTTP/1.1 headers to parse
	 * @return {@code true} if the headers indicate the content type is HTML
	 */
	public static boolean isHtml(Map<String, List<String>> headers) {
		String content = "Content-Type";
		String value = "text/html";
		if (headers.containsKey(content)) {
			return headers.get(content).get(0).toLowerCase().startsWith(value);
		}
		return false;

	}

	/**
	 * Parses the HTTP status code from the provided HTTP headers, assuming the
	 * status line is stored under the {@code null} key.
	 *
	 * @param headers the HTTP/1.1 headers to parse
	 * @return the HTTP status code or -1 if unable to parse for any reasons
	 */
	public static int getStatusCode(Map<String, List<String>> headers) {
		String content = null;
		if (headers.containsKey(content)) {
			String s = headers.get(content).get(0);
			Pattern pattern = Pattern.compile("\\d{3}");
			Matcher matcher = pattern.matcher(s);
			if (matcher.find()) {
				return Integer.parseInt(matcher.group());
			}

		}
		return -1;
	}

	/**
	 * Returns {@code true} if and only if the HTTP status code is between 300 and
	 * 399 (inclusive) and there is a "Location" header with at least one value.
	 *
	 * @param headers the HTTP/1.1 headers to parse
	 * @return {@code true} if the headers indicate the content type is HTML
	 */
	public static boolean isRedirect(Map<String, List<String>> headers) {
		String content = "Location";
		if (getStatusCode(headers) >= 300 && getStatusCode(headers) <= 399 && headers.containsKey(content)) {
			return headers.get(content) != null;
		}
		return false;
	}

	/**
	 * Fetches the resource at the URL using HTTP/1.1 and sockets. If the status
	 * code is 200 and the content type is HTML, returns the HTML as a single
	 * string. If the status code is a valid redirect, will follow that redirect if
	 * the number of redirects is greater than 0. Otherwise, returns {@code null}.
	 *
	 * @param url       the url to fetch
	 * @param redirects the number of times to follow redirects
	 * @return the html or {@code null} if unable to fetch the resource or the
	 *         resource is not html
	 * @throws IOException
	 * @throws UnknownHostException
	 *
	 * @see HttpsFetcher#openConnection(URL)
	 * @see HttpsFetcher#printGetRequest(PrintWriter, URL)
	 * @see HttpsFetcher#getHeaderFields(BufferedReader)
	 * @see HttpsFetcher#getContent(BufferedReader)
	 *
	 * @see String#join(CharSequence, CharSequence...)
	 *
	 * @see #isHtml(Map)
	 * @see #isRedirect(Map)
	 */
	public static String fetch(URL url, int redirects) throws IOException, UnknownHostException {
		try (Socket socket = HttpsFetcher.openConnection(url);
				PrintWriter request = new PrintWriter(socket.getOutputStream());
				InputStreamReader input = new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8);
				BufferedReader response = new BufferedReader(input);) {
			HttpsFetcher.printGetRequest(request, url);
			var headers = HttpsFetcher.getHeaderFields(response);
			List<String> content = HttpsFetcher.getContent(response);
			headers.put("Content", content);
			if (getStatusCode(headers) >= 200 && getStatusCode(headers) < 300 && isHtml(headers)) {
				return String.join("\n", headers.get("Content"));
			}
			if (isRedirect(headers) && redirects > 0) {
				return fetch(headers.get("Location").get(0), redirects - 1);
			}
			return null;
		}
	}

	/**
	 * Converts the {@link String} url into a {@link URL} object and then calls
	 * {@link #fetch(URL, int)}.
	 *
	 * @param url       the url to fetch
	 * @param redirects the number of times to follow redirects
	 * @return the html or {@code null} if unable to fetch the resource or the
	 *         resource is not html
	 * @throws IOException
	 * @throws UnknownHostException
	 *
	 * @see #fetch(URL, int)
	 */
	public static String fetch(String url, int redirects) throws UnknownHostException, IOException {
		try {
			return fetch(new URL(url), redirects);
		} catch (MalformedURLException e) {
			return null;
		}
	}

	/**
	 * Converts the {@link String} url into a {@link URL} object and then calls
	 * {@link #fetch(URL, int)} with 0 redirects.
	 *
	 * @param url the url to fetch
	 * @return the html or {@code null} if unable to fetch the resource or the
	 *         resource is not html
	 * @throws IOException
	 * @throws UnknownHostException
	 *
	 * @see #fetch(URL, int)
	 */
	public static String fetch(String url) throws UnknownHostException, IOException {
		return fetch(url, 0);
	}

	/**
	 * Calls {@link #fetch(URL, int)} with 0 redirects.
	 *
	 * @param url the url to fetch
	 * @return the html or {@code null} if unable to fetch the resource or the
	 *         resource is not html
	 * @throws IOException
	 * @throws UnknownHostException
	 */
	public static String fetch(URL url) throws UnknownHostException, IOException {
		return fetch(url, 0);
	}
}
