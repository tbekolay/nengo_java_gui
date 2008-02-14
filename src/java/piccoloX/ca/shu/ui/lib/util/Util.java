package ca.shu.ui.lib.util;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.lang.reflect.Array;
import java.lang.reflect.InvocationTargetException;
import java.util.ListIterator;

import javax.swing.JOptionPane;
import javax.swing.SwingUtilities;

import ca.shu.ui.lib.world.WorldObject;
import ca.shu.ui.lib.world.piccolo.WorldImpl;
import ca.shu.ui.lib.world.piccolo.primitives.PiccoloNodeInWorld;
import edu.umd.cs.piccolo.event.PInputEvent;
import edu.umd.cs.piccolo.util.PStack;

/**
 * Miscellaneous static functions used by the user interface
 * 
 * @author Shu Wu
 */
public class Util {
	private static final String BLANKS = "            ";

	private static final String ZEROES = "000000000000";

	private static void arrayToStringRecursive(StringBuffer sb, Object array) {
		sb.append("[");
		if (array == null) {
			sb.append("NULL");
		} else {
			Object obj = null;

			int length = Array.getLength(array);
			int lastItem = length - 1;

			for (int i = 0; i < length; i++) {
				obj = Array.get(array, i);

				if (obj instanceof Object[]) {
					arrayToStringRecursive(sb, obj);
				} else if (obj instanceof float[]) {
					arrayToStringRecursive(sb, obj);

				} else if (obj instanceof int[]) {
					arrayToStringRecursive(sb, obj);

				} else if (obj instanceof long[]) {
					arrayToStringRecursive(sb, obj);

				} else if (obj instanceof double[]) {
					arrayToStringRecursive(sb, obj);

				} else if (obj != null) {
					sb.append(obj);
				} else {
					sb.append("NULL");
				}
				if (i < lastItem) {
					sb.append(", ");
				}
			}

		}
		sb.append("]");
	}

	public static String arrayToString(Object array) {
		StringBuffer sb = new StringBuffer();
		arrayToStringRecursive(sb, array);
		return sb.toString();
	}

	public static void Assert(boolean bool) {
		Assert(bool, "");
	}

	public static void Assert(boolean bool, String msg) {
		if (!bool && UIEnvironment.isDebugEnabled()) {
			String assertMsg = "ASSERT == FALSE: " + msg;
			(new Exception(assertMsg)).printStackTrace();
			UserMessages.showWarning(assertMsg);
		}

	}

	public static void debugMsg(String msg) {
		if (UIEnvironment.isDebugEnabled()) {
			System.out.println("DebugMSG: " + msg);
		}

	}

	public static void runInEventDispathThread(Runnable runnable) {
		if (SwingUtilities.isEventDispatchThread()) {
			runnable.run();
		} else {
			try {
				SwingUtilities.invokeAndWait(runnable);
			} catch (InterruptedException e1) {
				e1.printStackTrace();
			} catch (InvocationTargetException e1) {
				e1.getTargetException().printStackTrace();
			}
		}
	}

	public static String truncateString(String input, int maxLength) {
		String noHTMLString = input.replaceAll("\\<.*?>", "");

		if (maxLength < 3) {
			maxLength = 3;
		}

		if (noHTMLString.length() > maxLength) {
			noHTMLString = noHTMLString.substring(0, noHTMLString.length() - 3) + "...";

		}
		return noHTMLString;

	}

	public static Object cloneSerializable(Serializable obj) {
		ObjectOutputStream out = null;
		ObjectInputStream in = null;

		try {
			ByteArrayOutputStream bout = new ByteArrayOutputStream();
			out = new ObjectOutputStream(bout);

			out.writeObject(obj);
			out.close();

			ByteArrayInputStream bin = new ByteArrayInputStream(bout.toByteArray());
			in = new ObjectInputStream(bin);
			Object copy = in.readObject();

			in.close();

			return copy;
		} catch (Exception ex) {
			ex.printStackTrace();
		} finally {
			try {
				if (out != null) {
					out.close();
				}

				if (in != null) {
					in.close();
				}
			} catch (IOException ignore) {
			}
		}

		return null;
	}

	public static String format(double val, int n, int w) {
		// rounding
		double incr = 0.5;
		for (int j = n; j > 0; j--)
			incr /= 10;
		val += incr;

		String s = Double.toString(val);
		int n1 = s.indexOf('.');
		int n2 = s.length() - n1 - 1;

		if (n > n2)
			s = s + ZEROES.substring(0, n - n2);
		else if (n2 > n)
			s = s.substring(0, n1 + n + 1);

		if (w > 0 & w > s.length())
			s = BLANKS.substring(0, w - s.length()) + s;
		else if (w < 0 & (-w) > s.length()) {
			w = -w;
			s = s + BLANKS.substring(0, w - s.length());
		}
		return s;
	}

	/*
	 * Get the extension of a file.
	 */
	public static String getExtension(File f) {
		String ext = null;
		String s = f.getName();
		int i = s.lastIndexOf('.');

		if (i > 0 && i < s.length() - 1) {
			ext = s.substring(i + 1).toLowerCase();
		}
		return ext;
	}

	/**
	 * @return The first node on the pick path that matches the parameter type
	 * @param event
	 *            Event sent from Piccolo
	 * @param type
	 *            The type of node to be picked from the pick tree
	 */
	@SuppressWarnings("unchecked")
	public static WorldObject getNodeFromPickPath(PInputEvent event,
			Class<? extends WorldObject> type) {
		PStack nodeStack = event.getPath().getNodeStackReference();
		ListIterator it = nodeStack.listIterator(nodeStack.size());

		while (it.hasPrevious()) {
			Object node = it.previous();

			if (node instanceof PiccoloNodeInWorld) {
				WorldObject wo = ((PiccoloNodeInWorld) node).getWorldObject();

				if (wo != null) {
					if (type.isInstance(wo)) {
						return (WorldObject) wo;
					}

					/*
					 * Stop picking objects at the boundary of the worlds
					 */
					if (node instanceof WorldImpl) {
						return null;
					}
				}
			}
		}
		return null;
	}

	public static boolean isArray(Object obj) {
		if ((obj instanceof Object[]) || (obj instanceof float[]) || (obj instanceof int[])
				|| (obj instanceof long[]) || (obj instanceof double[])) {
			return true;
		}
		return false;

	}

	public static void Message(String msg, String title) {
		JOptionPane.showMessageDialog(UIEnvironment.getInstance(), msg, title,
				JOptionPane.INFORMATION_MESSAGE);
	}

}
