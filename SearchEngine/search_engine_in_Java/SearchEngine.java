import org.eclipse.jetty.server.Handler;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.handler.HandlerList;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;

/**
 * Set up the search engine
 * 
 * @author zhengyuan
 */
public class SearchEngine {

	/** thread-safe index */
	private final ThreadSafeInvertedIndex threadIndex;

	/** The hard-coded port to run this server. */
	private final int port;

	/**
	 * @param threadIndex
	 * @param port
	 */
	public SearchEngine(ThreadSafeInvertedIndex threadIndex, int port) {
		this.threadIndex = threadIndex;
		this.port = port;
	}

	/**
	 * Initialize the servlet and start the server
	 * 
	 * @throws Exception
	 */
	public void start() throws Exception {
		Server server = new Server(port);
		ServletContextHandler context = new ServletContextHandler();

		context.setContextPath("/");
		context.addServlet(new ServletHolder(new IndexServlets(threadIndex)), "/");

		HandlerList handlers = new HandlerList();
		handlers.setHandlers(new Handler[] { context });

		server.setHandler(handlers);
		server.start();
		server.join();
	}
}