import java.io.IOException;
import java.io.PrintWriter;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Map;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.text.StringEscapeUtils;

/**
 * The servlets class responsible for simple search
 * 
 * @author zhengyuan
 */
@SuppressWarnings("serial")
public class IndexServlets extends HttpServlet {

	/** The title to use for this webpage. */
	private static final String TITLE = "Search Engine";

	/** thread-safe index */
	private final ThreadSafeInvertedIndex threadIndex;

	/**
	 * Constructor to initialize thread safe index;
	 * 
	 * @param threadIndex
	 */
	public IndexServlets(ThreadSafeInvertedIndex threadIndex) {
		super();
		this.threadIndex = threadIndex;
	}

	@Override
	protected void doGet(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {
		response.setContentType("text/html");
		PrintWriter out = response.getWriter();
		out.printf("<HTML>");
		out.printf("<head><title>%s</title></head>%n", TITLE);
		out.printf("  <BODY>");
		out.printf("<h1>Search Engine</h1>%n%n");
		out.print("<form method = \"post\" action = \"/\">"
				+ "          <input type=\"text\" placeholder=\"query\" name = \"query\"><br>\n"
				+ "			<input type=\"radio\" name=\"searchMode\" value=\"partial\" checked> partial search<br>\n"
				+ "			<input type=\"radio\" name=\"searchMode\" value=\"exact\"> exact search<br>\n"
				+ "          <input type=\"submit\" value=\"Search\"  class=\"button\">\n" + "</form>");
		out.printf("  </BODY>");
		out.printf("</HTML>");

		out.flush();
		out.close();
	}

	@Override
	protected void doPost(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {
		String query = request.getParameter("query").trim();
		query = StringEscapeUtils.escapeHtml4(query);
		if (!query.equals("")) {
			searchPage(request, response, query);
		} else {
			response.sendRedirect("/");
		}
	}

	/**
	 * Present a search page and the search result below
	 * 
	 * @param request
	 * @param response
	 * @param query    query word
	 * @throws IOException
	 */
	private void searchPage(HttpServletRequest request, HttpServletResponse response, String query) throws IOException {

		response.setContentType("text/html");
		DecimalFormat FORMATTER = new DecimalFormat("0.00000");

		PrintWriter out = response.getWriter();
		out.printf("<HTML>");
		out.printf("<head><title>%s</title></head>%n", TITLE);
		out.printf("  <BODY>");
		out.printf("<h1>Search Engine</h1>%n%n");
		out.printf("<form method = \"post\" action = \"/\">"
				+ "          <input type=\"text\" placeholder=\"query\" name = \"query\"><br>\n"
				+ "			<input type=\"radio\" name=\"searchMode\" value=\"partial\" checked> partial search<br>\n"
				+ "			<input type=\"radio\" name=\"searchMode\" value=\"exact\"> exact search<br>\n"
				+ "          <input type=\"submit\" value=\"Search\"  class=\"button\">\n" + "</form>");
		boolean exact = request.getParameter("searchMode").equals("exact") ? true : false;
		QueryParser parser = new QueryParser(threadIndex);
		parser.search(query, exact);
		Map<String, ArrayList<InvertedIndex.Result>> resultMap = parser.getResult();
		for (String word : resultMap.keySet()) {
			if (resultMap.get(word).size() != 0) {
				out.printf("<p>Search word: %s<br/>", word);
				for (InvertedIndex.Result result : resultMap.get(word)) {
					out.printf("Location: <a href= %s>%s</a><br/>", result.getLocation(), result.getLocation());
					out.printf("Count: %s<br>", result.getCount());
					out.printf("Score: %s</div></p>\n", FORMATTER.format(result.getScore()));
				}
			} else {
				out.printf("<p>No results of \"%s\"</p>\n", word);
			}
		}
		out.printf("  </BODY>");
		out.printf("</HTML>");

		out.flush();
		out.close();

		response.setStatus(HttpServletResponse.SC_OK);
	}
}
