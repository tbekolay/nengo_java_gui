from jip.embed import require
require('org.simplericity.macify:macify:1.6')

from java.lang import Runnable, System
from org.simplericity.macify.eawt import DefaultApplication

from .core import Nengo


class RunWrapper(Runnable):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.func(*self.args, **self.kwargs)

def start():
    System.setProperty("apple.laf.useScreenMenuBar", "true")
    System.setProperty("com.apple.mrj.application.apple.menu.about.name",
                       "Nengo")
    application = DefaultApplication()
    nengo = Nengo()
    nengo.application = application

if __name__ == '__main__':
    start()


"""Consider!!

from threading import Thread
import time

def make_imports():
    import unicodedata

background_import = Thread(target=make_imports)
background_import.start()

print "Do something else while we wait for the import"
for i in xrange(10):
    print i
    time.sleep(0.1)
print "Now join..."
background_import.join()

print "And actually use unicodedata"
import unicodedata
"""

""" Do we need any of these?

package ca.nengo.ui.lib.util;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.lang.reflect.Array;
import java.util.ListIterator;

import javax.swing.JOptionPane;

import ca.nengo.ui.NengoGraphics;
import ca.nengo.ui.lib.actions.ActionException;
import ca.nengo.ui.lib.world.WorldObject;
import ca.nengo.ui.lib.world.piccolo.WorldImpl;
import ca.nengo.ui.lib.world.piccolo.primitives.PiccoloNodeInWorld;
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
            showException(new Exception("ASSERT == FALSE, " + msg));
        }
    }

    public static void showException(Exception exception) {
        String msg = exception.getMessage();
        StringBuilder assertMsg = new StringBuilder(
                "An unexpected error has occured \n"
                        + "Please report this log at: https://github.com/ctn-waterloo/nengo/issues\nIf possible, please include a record of what you were doing preceding this screen \n\n");
        assertMsg.append("*** " + NengoGraphics.APP_NAME + " ***\n");

        if (msg != null && !"".equals(msg)) {
            assertMsg.append(msg + "\n");
        }

        assertMsg.append("*** Stack Trace *** \n");
        exceptionToString(assertMsg, exception);
        if (exception instanceof ActionException) {
            ActionException actionException = (ActionException) exception;
            if (actionException.getTargetException() != null) {
                assertMsg.append("*** Target Exception *** \n");
                exceptionToString(assertMsg, actionException.getTargetException());
            }
        }

        if (msg == null || "".equals(msg)) {
            msg = "Exception";
        }

        UserMessages.showTextDialog(msg, assertMsg.toString(), JOptionPane.ERROR_MESSAGE);

    }

    private static void exceptionToString(StringBuilder strBuilder, Exception e) {
        StackTraceElement[] stackEls = e.getStackTrace();
        int i = 0;
        strBuilder.append(e.getMessage() + "\n");
        for (StackTraceElement el : stackEls) {
            if (i > 200) {
                strBuilder.append("...");
                break;
            }
            strBuilder.append(el.toString() + "\n");
            i++;
        }
    }

    public static void debugMsg(String msg) {
        if (UIEnvironment.isDebugEnabled()) {
            System.out.println("DebugMSG: " + msg);
        }

    }

    public static String truncateString(String input, int maxLength) {
        String noHTMLString = input.replaceAll("\\<.*?>", "");

        if (maxLength < 3) {
            maxLength = 3;
        }

        if (noHTMLString.length() > maxLength) {
            noHTMLString = noHTMLString.substring(0, maxLength - 3) + "...";

        }
        return noHTMLString;

    }

    public static void sleep(long time) {
        try {
            Thread.sleep(time);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
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
        for (int j = n; j > 0; j--) {
            incr /= 10;
        }
        val += incr;

        String s = Double.toString(val);
        int n1 = s.indexOf('.');
        int n2 = s.length() - n1 - 1;

        if (n > n2) {
            s = s + ZEROES.substring(0, n - n2);
        } else if (n2 > n) {
            s = s.substring(0, n1 + n + 1);
        }

        if (w > 0 & w > s.length()) {
            s = BLANKS.substring(0, w - s.length()) + s;
        } else if (w < 0 & (-w) > s.length()) {
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
        ListIterator<Object> it = nodeStack.listIterator(nodeStack.size());

        while (it.hasPrevious()) {
            Object node = it.previous();

            if (node instanceof PiccoloNodeInWorld) {
                WorldObject wo = ((PiccoloNodeInWorld) node).getWorldObject();

                if (wo != null) {
                    if (type.isInstance(wo)) {
                        return wo;
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

    /*
     * Does a binary copy from fromFile to toFile
     */
    public static void copyFile(File fromFile, File toFile) throws IOException {
        FileInputStream fis = new FileInputStream(fromFile);
        FileOutputStream fos = new FileOutputStream(toFile);
        BufferedInputStream reader = new BufferedInputStream(fis);
        BufferedOutputStream writer = new BufferedOutputStream(fos);

        //... Loop as long as there is input
        int data = -1;
        while ((data = reader.read()) != -1) {
            writer.write(data);
        }

        //... Close reader and writers.
        reader.close();  // Close to unlock.
        writer.close();  // Close to unlock and flush to disk.
    }
}
"""

