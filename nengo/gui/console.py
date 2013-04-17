#import java.awt.BorderLayout;
#import java.awt.Color;
#import java.awt.Insets;
#import java.awt.event.ActionEvent;
#import java.awt.event.FocusAdapter;
#import java.awt.event.FocusEvent;
#import java.awt.event.KeyEvent;
#import java.awt.event.KeyListener;
#import java.awt.event.WindowAdapter;
#import java.awt.event.WindowEvent;
#import java.io.File;
#import java.util.ArrayList;
#import java.util.regex.Pattern;

#import javax.swing.Action;
#import javax.swing.JEditorPane;
#import javax.swing.JFrame;
#import javax.swing.JPanel;
#import javax.swing.JScrollPane;
#import javax.swing.JSeparator;
#import javax.swing.JTextArea;
#import javax.swing.SwingUtilities;
#import javax.swing.ToolTipManager;
#import javax.swing.text.BadLocationException;
#import javax.swing.text.Style;
#import javax.swing.text.StyleConstants;
#import javax.swing.text.StyleContext;

#import org.apache.log4j.Logger;
#import org.python.core.PyStringMap;
#import org.python.util.PythonInterpreter;

#import ca.nengo.config.JavaSourceParser;
#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.lib.Style.NengoStyle;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.objects.activities.TrackedAction;

class ScriptFocusAdapter(FocusAdapter):
    def __init__(self, console):
        self.console = console
        FocusAdapter.__init__(self)

    def focusGained(self, event):
        self.console.commandField.requestFocusInWindow()


class ConsoleAction(TrackedAction):
    def __init__(self, console, initText):
        TrackedAction.__init__(self, "Running...")
        self.console = console
        self.initText = initText

    def action(self):
        nengoinstance.progressIndicator.start(self.initText.trim())
        self.console.commandField.enabled = False
        try:
            if self.initText.startsWith("run "):
                self.console.addVariable("scriptname", self.initText[4:].trim())
                self.console.interpreter.execfile(self.initText[4:].trim())
            elif self.initText.startsWith("help "):
                self.console.appendText(JavaSourceParser.removeTags(
                    getHelp(self.initText[5:].trim()), self.console.HELP_STYLE))
                self.console.appendText("\n", "root")
            elif self.initText == "clear":
                self.console.displayArea.text = ""
            elif self.initText == "reset":
                self.console.reset(True)
            else:
                self.console.interpreter.exec(self.initText)
        except Exception, e:
            self.console.LOGGER.error("Runtime error in interpreter", e)
            self.console.appendText(e.toString() + "\n", self.console.ERROR_STYLE)

    def postAction(self):
        TrackedAction.postAction(self)
        self.console.commandField.enabled = True
        self.console.commandField.requestFocus()


class ScriptConsole(JPanel):
    """A user interface panel for entering script commands.

    """

    LOGGER = Logger.getLogger(ScriptConsole.class)
    CURRENT_VARIABLE_NAME = "that"
    CURRENT_DATA_NAME = "data"

    COMMAND_STYLE = "command"
    OUTPUT_STYLE = "output"
    ERROR_STYLE = "error"
    HELP_STYLE = "help"

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.interpreter.execfile("python/startup_ui.py")

        self.displayArea = JEditorPane("text/html", "")
        self.displayArea.editable = False
        self.displayArea.margin = Insets(5, 5, 5, 5)
        # add a listener, so that keys typed when displayArea has focus can pass to commandField
        self.displayArea.addKeyListener(CommandKeyListener(self))

        self.commandField = JTextArea()
        ToolTipManager.sharedInstance().registerComponent(self.commandField)
        self.layout = BorderLayout()

        self.displayScroll = JScrollPane(self.displayArea)

        self.separator = JSeparator(JSeparator.HORIZONTAL)

        panel = JPanel()
        panel.layout = BorderLayout()
        panel.add(self.displayScroll, BorderLayout.CENTER)
        panel.add(self.separator, BorderLayout.SOUTH)

        self.add(panel, BorderLayout.CENTER)
        self.add(self.commandField, BorderLayout.SOUTH)
        self.displayScroll.border = None

        self.commandField.addKeyListener(CommandKeyListener(self))
        self.commandField.focusTraversalKeysEnabled = False

        if not NengoStyle.GTK:
            self.commandField.border = None

        self.historyCompletor = HistoryCompletor()
        self.callChainCompletor = CallChainCompletor(self.interpreter)
        self.inCallChainCompletionMode = False
        self.typedText = ""
        self.typedCaretPosition = 0
        self.addedVariables = []

        self.interpreter.out = ConsoleOutputWriter(self)

        self.addFocusListener(ScriptFocusAdapter(self))

        # Tooltip stuff
        self.toolTipVisible = True
        self.defaultDismissDelay = ???
        self.lastHelpTime = 0
        self.hideTip = ???

        self.style()

    def style(self):
        # Some are commented out because of inconsistencies with what
        # different platforms do with background and foreground colour.

        self.styleContext = StyleContext()
        self.rootStyle = self.styleContext.addStyle("root", None)
        StyleConstants.setForeground(self.rootStyle, NengoStyle.COLOR_FOREGROUND)

        self.childrenBackground = NengoStyle.COLOR_BACKGROUND
        self.childrenForeground = NengoStyle.COLOR_FOREGROUND
        if not NengoStyle.GTK:
            self.commandField.caretColor = NengoStyle.COLOR_LIGHT_GREEN

        self.commandStyle = self.styleContext.addStyle(self.COMMAND_STYLE, rootStyle)
        StyleConstants.setForeground(self.commandStyle, NengoStyle.COLOR_FOREGROUND)
        StyleConstants.setItalic(self.commandStyle, True)
        outputStyle = self.styleContext.addStyle(self.OUTPUT_STYLE, rootStyle)
        StyleConstants.setForeground(outputStyle, Color.GRAY)
        errorStyle = self.styleContext.addStyle(self.ERROR_STYLE, rootStyle)
        StyleConstants.setForeground(errorStyle, Color.RED)

        helpStyle = self.styleContext.addStyle(self.HELP_STYLE, rootStyle)
        StyleConstants.setForeground(helpStyle, NengoStyle.COLOR_FOREGROUND)

    @childrenBackground.setter
    def childrenBackground(self, bg):
        self.displayArea.background = bg
        if not NengoStyle.GTK:
            self.commandField.background = bg

    #childrenForeground.setter
    def childrenForeground(self, fg):
        self.displayArea.foreground = fg
        if not NengoStyle.GTK:
            self.commandField.foreground = fg
        self.separator.foreground = fg

    def addVariable(self, name, variable):
        self.interpreter.set(self.makePythonName(name), variable)
        self.addedVariables.append(self.makePythonName(name))

    def removeVariable(self, name):
        name = self.makePythonName(name)
        if self.interpreter.get(name) is not None:
            self.interpreter.exec("del " + name)

    @property
    def variables(self):
        return self.interpreter.locals.keys()

    def reset(self, clearModules):
        """Reset the script console back to initial conditions
        (remove all modules and variables added within the interpreter).

        """
        if clearModules:
            # remove modules
            self.interpreter.exec("sys.modules.clear()")

        # remove variables
        for var in self.variables:
            # keep any variables that were added manually or special vars
            if not var in self.addedVariables and not v.startsWith("__"): 
                self.removeVariable(var)

        # re-add init variables
        self.interpreter.execfile("python/startup_ui.py")

    @staticmethod
    def makePythonName(name):
        # replace special characters with "_"
        nonPythonChar = Pattern.compile("\\W")
        name = nonPythonChar.matcher(name).replaceAll("_")

        # prepend "_" if name starts with a number
        if name.matches("\\A\\d.*"):
            name = "_" + name

        # prepend "_" if name is reserved word
        reserved = ["and", "assert", "break", "class", "continue", "def",
                    "del", "elif", "else", "except", "exec", "finally", "for",
                    "from", "global", "if", "import", "in", "is", "lambda",
                    "not", "or", "pass", "print", "raise", "return", "try",
                    "while", "yield"]

        for keyword in reserved:
            if name == keyword:
                name = "_" + name

        return name

    @currentObject.setter
    def currentObject(self, o):
        self.interpreter.set(self.CURRENT_VARIABLE_NAME, o)

    @currentData.setter
    def currentData(self, o):
        self.interpreter.set(self.CURRENT_DATA_NAME, o)
        # convert the TimeSeriesData into a numeric array
        self.interpreter.exec(self.CURRENT_DATA_NAME + "=array("
                              + self.CURRENT_DATA_NAME + ".values).T")

    def setFocus(self):
        """Sets initial focus (should be called from UI thread)"""
        self.commandField.requestFocus()

    def appendText(self, text, style):
        self.displayArea.document.insertString(self.displayArea.document.length,
            text, self.styleContext.getStyle(style))
        self.displayArea.caretPosition = self.displayArea.document.length
        self.scrollToBottom()

    def scrollToBottom(self):
        self.displayScroll.verticalScrollBar.value = self.displayScroll.verticalScrollBar.maximum
        #myDisplayArea.setCaretPosition(myDisplayArea.getDocument().getLength());        
        #myDisplayArea.scrollRectToVisible(new Rectangle(0,myDisplayArea.getHeight(),0,myDisplayArea.getHeight()));

    def clearCommand(self):
        self.commandField.text = ""

    def withinString(self):
        typedTextToCaret = self.typedText[:self.typedCaretPosition]
        singles = 0
        doubles = 0

        for ch in typedTextToCaret:
            if ch == "'":
                singles += 1
            if ch == '"':
                doubles += 1

        return singles % 2 == 1 or doubles % 2 == 1

    @inCallChainCompletionMode.setter
    def inCallChainCompletionMode(self, inMode):
        """Sets whether the console is in the mode of completing a call
        chain (otherwise it uses history completion).
        """
        self._inCallChainCompletionMode = inMode
        if inMode:
            typedTextToCaret = self.typedText[:self.typedCaretPosition]
            self.callChainCompletor.base = self.getCallChain(typedTextToCaret)
        else:
            self.commandField.toolTipText = None

    @property
    def inCallChainCompletionMode(self):
        return self._inCallChainCompletionMode

    def enterCommand(self, text):
        self.appendText(">>", "root")
        self.appendText(text + "\r\n", self.COMMAND_STYLE)
        self.historyCompletor.add(text)
        self.clearCommand()
        self.setTypedText()

        initText = text
        ConsoleAction(self, initText).doAction()

    @staticmethod
    def getHelp(entity):
        result = "No documentation found for " + entity

        try:
            c = Class.forName(entity)
            docs = JavaSourceParser.getDocs(c)
            if docs is not None:
                result = docs
        except ClassNotFoundException, e:
            self.LOGGER.error("Class not found in help request", e)

        return result

    def completorUp(self):
        """Moves up the command completor list."""
        if self.inCallChainCompletionMode:
            callChain = self.getCallChain(self.typedText[:self.typedCaretPosition])
            replacement = self.callChainCompletor.previous(callChain)
            self.commandField.select(self.typedCaretPosition - len(callChain),
                                     self.commandField.caretPosition)
            # String selection = myCommandField.getSelectedText();
            self.commandField.replaceSelection(replacement)
            self.commandField.toolTipText = self.callChainCompletor.documentation
            
            # System.out.println("caret pos: " + myTypedCaretPosition);
            # System.out.println("call chain: " + callChain);
            # System.out.println("selection: " + selection);
            # System.out.println("replacement: " + replacement);
        else:
            self.commandField.text = self.historyCompletor.previous(self.typedText)

    def completorDown(self):
        """Moves down the command completor list."""
        if self.inCallChainCompletionMode:
            callChain = self.getCallChain(self.typedText[:self.typedCaretPosition])
            replacement = self.callChainCompletor.next(callChain)
            self.commandField.select(self.typedCaretPosition - len(callChain),
                                     self.commandField.caretPosition)
            # String selection = myCommandField.getSelectedText();
            self.commandField.replaceSelection(replacement)
            self.commandField.toolTipText = self.callChainCompletor.documentation

            #System.out.println("call chain: " + callChain);
            #System.out.println("selection: " + selection);
            #System.out.println("replacement: " + replacement);
        else:
            self.commandField.text = self.historyCompletor.next(self.typedText)

    def showToolTip(self):
        if (not self.toolTipVisible and self.lastHelpTime > 0
                and System.currentTimeMillis() - self.lastHelpTime < 500):
            self.appendText(JavaSourceParser.removeTags(
                self.commandField.toolTipText + "\r\n", self.HELP_STYLE)
        else:
            showTip = self.commandField.actionMap.get("postTip")
            self.hideTip = self.commandField.actionMap.get("hideTip")
            if showTip is not None and not self.toolTipVisible:
                e = ActionEvent(self.commandField, ActionEvent.ACTION_PERFORMED, "")
                SwingUtilities.invokeLater(make_runnable(
                    lambda: showTip.actionPerformed(e)))
            self.toolTipVisible = True
            self.defaultDismissDelay = ToolTipManager.sharedInstance().dismissDelay
            # show until hideToolTip(), up to one minute max
            ToolTipManager.sharedInstance().dismissDelay = 1000 * 60
        self.lastHelpTime = System.currentTimeMillis()

    def hideToolTip(self):
        if self.hideTip is not None and self.toolTipVisible:
            e = ActionEvent(self.commandField, ActionEvent.ACTION_PERFORMED, "")
            # final Action hideTip = myHideTip;
            SwingUtilities.invokeLater(make_runnable(
                lambda: self.hideTip.actionPerformed(e)))
        self.toolTipVisible = False
        ToolTipManager.sharedInstance().dismissDelay = self.defaultDismissDelay

    def setTypedText(self):
        """Takes note of the text in the command field,
        as text that the user has typed (as opposed to recalled history).

        The two types must be distinguished, because we don't want an
        unselected history item to be used as the basis for
        subsequent history lookups.
        
        """
        self.typedText = self.commandField.text
        self.typedCaretPosition = self.commandField.caretPosition
        self.historyCompletor.resetIndex()
        self.callChainCompletor.resetIndex()


    def revertToTypedText(self):
        """Resets command field text to the last text typed by the user
        (as opposed to autocompleted text).
        
        """
        self.commandField.text = self.typedText
        self.commandField.caretPosition = self.typedCaretPosition

    @staticmethod
    def getCallChain(command):
        # note: I tried to do this with a single regex but I can't see how to
        # handle nested brackets properly
        pattern = Pattern.compile("\\w||\\.")  # word character or dot

        brackets = 0
        start = 0
        for i in range(len(command) - 1, -1, -1):
            if command[i] == ')':
                brackets += 1
            elif brackets > 0 and command[i] == '(':
                brackets -= 1
            elif (brackets == 0 and (not i == len(command) - 1 and command[i] == '(')
                  and not pattern.matcher(command[i]).matches()):
                start = i + 1
                break
        return command[start:]

    def passKeyEvent(self, event):
        kl = self.commandField.keyListeners
        for listner in kl:
            if isinstance(listener, CommandKeyListener):
                listener.keyPressed(event)


class CommandKeyListener(KeyListener):
    def __init__(self, console):
        self.console = console

    def keyPressed(self, event):
        code = event.keyCode

        # Escape
        if code == KeyEvent.VK_ESCAPE and self.console.inCallChainCompletionMode():
            self.console.revertToTypedText()
            self.console.inCallChainCompletionMode = False
        elif code == KeyEvent.VK_ESCAPE:
            self.console.clearCommand()
        # Shift-tab
        elif code == KeyEvent.VK_TAB and event.isShiftDown():
            self.console.commandField.append("\t")
        # Tab
        elif code == KeyEvent.VK_TAB:
            self.console.inCallChainCompletionMode = True
            event.consume()
        # Up arrow
        elif code == KeyEvent.VK_UP:
            self.console.completorUp()
            event.consume()
        # Down arrow
        elif code == KeyEvent.VK_DOWN:
            self.console.completorDown()
            event.consume()
        # Control
        elif code == KeyEvent.VK_CONTROL:
            self.console.showToolTip()
        # Shift-enter
        elif code == KeyEvent.VK_ENTER and event.isShiftDown():
            # allow a new line to be entered
            self.console.commandField.append("\n")
        # Enter
        elif code == KeyEvent.VK_ENTER:
            event.consume()
            self.console.enterCommand(self.console.commandField.text)
        else:
            if not self.console.commandField.hasFocus() and event.keyChar != KeyEvent.CHAR_UNDEFINED:
                # a typing event is coming from far away (the command field doesn't have focus)
                # so manually append the typed character
                curtext = self.console.commandField.text
                if event.keyCode == KeyEvent.VK_BACK_SPACE:
                    self.console.commandField.text = curtext[:-1]
                elif event.keyCode != KeyEvent.VK_DELETE:
                    self.console.commandField.text = self.console.commandField.text() + e.keyChar
                    self.console.commandField.requestFocus()
                self.console.inCallChainCompletionMode = False

        def keyReleased(self, event):
            code = event.keyCode
            # Control
            if code == 17:
                self.console.hideToolTip()
            elif code != 38 and code != 40:
                self.console.setTypedText()
                if code == 9:
                    self.console.completorUp()
                if code == 46 and not self.console.withinString():
                    self.console.inCallChainCompletionMode = True

        def keyTyped(self, event):
            pass

class ConsoleOutputWriter(java.io.Writer):
    """Replacement for original console writer
    that should eliminate the "Read end dead" bug.
    
    """

    def __init__(self, console):
        java.io.Writer.__init__(self)
        self.console = console

    def write(self, cbuf, off, len):
        self.console.appendText(cbuf, self.console.OUTPUT_STYLE)

    def flush(self):
        pass

    def close(self):
        pass

    @staticmethod
    def test():
        class _WindowAdapter(WindowAdapter):
            def windowClosing(self, e):
                System.exit(0)

        # System.out.println(makePythonName("10balloon"));
        # System.out.println(makePythonName("assert"));
        # System.out.println(makePythonName("1 + 1 = 2"));

        JavaSourceParser.addSource(File("../simulator/src/java/main"))
        interpreter = PythonInterpreter()
        console = ScriptConsole(interpreter)

        frame = JFrame("Script Console")
        frame.contentPane.add(console)

        frame.addWindowListener(_WindowAdapter())

        frame.setSize(500, 400);
        frame.visible = True

        SwingUtilities.invokeLater(make_runnable(console.setFocus))


class CommandCompletor(object):
    """Base class for command completors, which provide suggestions for
    filling in the remainder of partially-specified scripting commands.

    """

    def __init__(self):
        self.options = []
        self.index = len(self.options)


    def resetIndex(self):
        self.index = len(self.options)

    def previous(self, partial):
        for i in range(self.index - 1, -1, -1):
            if self.options[i].startsWith(partial):
                self.index = i
                return self.options[i]

        self.index = -1
        return partial

    def next(self, partial):
        for i in range(self.index + 1, len(self.option)):
            if self.options[i].startsWith(partial):
                self.index = i
                return self.options[i]

        self.index = len(self.options)
        return partial

#import java.io.BufferedInputStream;
#import java.io.BufferedOutputStream;
#import java.io.File;
#import java.io.FileInputStream;
#import java.io.FileNotFoundException;
#import java.io.FileOutputStream;
#import java.io.IOException;
#import java.io.ObjectInput;
#import java.io.ObjectInputStream;
#import java.io.ObjectOutput;
#import java.io.ObjectOutputStream;
#import java.util.ArrayList;
#import java.util.Collections;
#import java.util.List;

#import ca.nengo.ui.lib.util.Util;

class HistoryCompletor(CommandCompletor):
    """A list of commands that have been entered previously."""

    HISTORY_LOCATION_PROPERTY = "HistoryCompletor.File"
    NUM_COMMANDS_SAVED = 1000

    def __init__(self):
        CommandCompletor.__init__(self)
        self.fileobj = File(System.getProperty(HISTORY_LOCATION_PROPERTY,
                                               "commandhistory.dat"))
        if self.readFile() is None:
            return
        # read in past commands from file and add them to the options
        self.options.extend(self.readFile())
        self.resetIndex()

    def add(self, command):
        """Add command string to CommandCompletor and update commandhistory file"""
        self.options.append(command)
        self.resetIndex()
        overwriteFile(self.options)

    def readFile(self):
        """Read commandhistory file."""
        if not self.fileobj.exists() or not self.fileobj.canRead():
            return None
        with open(self.fileobj, 'r') as input:
            commands = input.readlines()
        return commands

    def overwriteFile(self, commands):
        """Overwrite commandhistory file with specified list of command strings."""
        with open(self.fileobj, 'w') as output:
            if len(commands) > self.NUM_COMMANDS_SAVED:
                commands = commands[-self.NUM_COMMANDS_SAVED:]
            output.writelines('\n'.join(commands) + '\n')

#import java.lang.reflect.Constructor;
#import java.lang.reflect.Field;
#import java.lang.reflect.Method;
#import java.lang.reflect.Modifier;
#import java.util.ArrayList;
#import java.util.List;
#import java.util.StringTokenizer;

#import org.python.core.PyClass;
#//import org.python.core.PyJavaClass;
#//import org.python.core.PyJavaInstance;
#import org.python.core.PyJavaType;
#import org.python.core.PyList;
#import org.python.core.PyObject;
#import org.python.core.PyObjectDerived;
#import org.python.core.PyString;
#import org.python.core.PyStringMap;
#import org.python.util.PythonInterpreter;

#import ca.nengo.config.JavaSourceParser;

class CallChainCompletor(CommandCompletor):
    """A CommandCompletor that suggests completions based on
    Python variable names and methods/fields of Python objects.
    
    """

    def __init__(self, interpreter):
        CommandCompletor.__init__(self)
        self.interpreter = interpreter
        self._documentation = []

    @base.setter
    def base(self, callChain):
        """Rebuilds the completion options list from a "base" call chain.
        
        :param string callChain: A partial call chain; e.g. "x.getY().get",
        from which we would extract the base call chain "x.getY()".
        (In this case the new options list might include "x.getY().toString()",
        "x.getY().wait()", etc.)
        
        """
        options = []
        endsWithBracket = callChain.endsWith("(")
        if endsWithBracket:
            callChain = callChain[:-1]

        pc = self.getKnownClass(callChain)

        # the root variable is specified
        if callChain.lastIndexOf('.') > 0:
            base = callChain[:callChain.lastIndexOf('.')]
            options = self.getMembers(base)
        elif endsWithBracket and pc is not None:
            options = self.getConstructors(pc)
        elif endsWithBracket: 
            # looks like an unrecognized full class name
            options = []
        else:
            options = self.variables

        self.options = options
        self.resetIndex()

    @property
    def documentation(self):
        result = None
        if self.index >= 0 and self.index < len(self._documentation):
            result = self._documentation[self.index]
            if result is not None and len(result) == 0:
                result = None
            if result is not None and not "<html>" in result:
                result = "<html>" + result + "</html>"
            if result is not None:
                result = result.replace("\n", "<br>")
                # TODO: allow for whitespace before BR
                result = result.replace("<\\\\p><br>", "<\\p>")
        return result

    def getConstructors(self, pc):
        result = []
        documentation = []

        if isinstance(pc, PyJavaType):
            className = pc.toString().split("'")[1]
            c = Class.forName(className)
            constructors = c.constructors
            for i in range(len(constructors)):
                mods = constructors[i].modifiers
                if Modifier.isPublic(mods):
                    buf = StringBuffer(c.simpleName)
                    buf.append("(")
                    names = JavaSourceParser.getArgNames(constructors[i])
                    types = constructors[i].parameterTypes
                    for j in range(len(types)):
                        buf.append(types[j].simpleName)
                        buf.append(" ")
                        buf.append(names[j])
                        if j < len(types) - 1:
                            buf.append(", ")
                        buf.append(")")
                        result.add(buf.toString())
                        self._documentation.append(JavaSourceParser.getDocs(constructors[i]))                        
        # do nothing for Python classes
        return result

    def getKnownClass(self, callChain):
        map = self.interpreter.locals
        keys = map.keys()

        for key in keys:
            if (key == callChain and isinstance(map[key], PyJavaType)
                    or isinstance(map[key], PyClass):
                return map[key]
        return None

    @property
    def variables(self):
        map = self.interpreter.locals
        keys = map.keys()

        result = []
        self._documentation = []
        for key in keys:
            result.append(key)
        return result
            
#            PyObject po = map.get(item);
#            if (po instanceof PyClass) {
#                myDocumentation.add(getClassDocs(((PyClass) po).__name__));
#            } else if (po instanceof PyInstance) {
#                PyClass pc = ((PyInstance) po).instclass;
#                if (pc instanceof PyClass) {
#                    myDocumentation.add(getClassDocs(((PyClass) pc).__name__));                    
#                } else {
#                    myDocumentation.add("");                    
#                }
#            } else {
#                myDocumentation.add("");
#            }

    
#    private static String getClassDocs(String className) {
#        String result = null;
#        try {
#            Class<?> c = Class.forName(className);
#            result = JavaSourceParser.getDocs(c);
#        } catch (ClassNotFoundException e) {
#            e.printStackTrace();
#        }
#        return (result == null) ? "" : result;
#    }

    def getMembers(self, base):
        map = self.interpreter.locals

        varTok = base.split('.')
        rootVariable = varTok[0]
        
        po = self.getObject(map, rootVariable)

        result = []
        self._documentation = []
        if isinstance(po, PyJavaType):
            className = po.toString().split("'")[1]
            
            c = Class.forName(className)
                
            fields = c.fields
            for field in fields:
                mods = field.modifiers
                if Modifier.isStatic(mods) and Modifier.isPublic(mods):
                    result.append(base + "." + field.name)
                    self._documentation.append("")

            methods = c.methods
            for method in methods:
                mods = method.modifiers
                if Modifier.isStatic(mods) and Modifier.isPublic(mods):
                    result.append(self.getMethodSignature(base, method)
                    # self._documentation.append(JavaSourceParser.getDocs(methods[i]))
        elif isinstance(po, PyObjectDerived):
            rootClassName = po.toString().split("@")[0]

            c = self.getReturnClass(rootClassName, base)
            fields = c.fields
            for field in fields:
                mods = field.modifiers
                if Modifier.isPublic(mods):
                    result.append(base + "." + field.name)
                    self._documentation.append("")

                methods = c.methods

                for method in methods:
                    mods = method.modifiers
                    if Modifier.isPublic(mods):
                        result.append(self.getMethodSignature(base, method))
                        #myDocumentation.add(JavaSourceParser.getDocs(methods[i]));
        # then it's a python object (?)
        elif po is not None and len(varTok) == 1:
            for item in po.__dir__():
                attr = po.__findattr__(item)
                buf = StringBuffer(base + ".")
                buf.append(item.toString())

                if attr.isCallable():
                    buf.append("(")
#                        try {
#                            String[] varnames = ((PyTableCode) ((PyFunction) ((PyMethod) attr).im_func).func_code).co_varnames;
#                            for (int i = 1; i < varnames.length; i++) { //skip 'self' arg
#                                buf.append(varnames[i]);
#                                if (i < varnames.length - 1) buf.append(", ");
#                            }
#                        } catch (ClassCastException e) {
#                            e.printStackTrace();
#                        }
                    buf.append(")")
            result.append(buf.toString())
        return result

    @staticmethod
    def getMethodSignature(base, m):
        buf = StringBuffer(base + ".")
        buf.append(m.name)
        buf.append('(')
        paramTypes = m.parameterTypes
        paramNames = JavaSourceParser.getArgNames(m)
        for j in range(len(paramTypes)):
            buf.append(paramTypes[j].simpleName
            buf.append(" ")
            buf.append(paramNames[j])
            if j < len(paramTypes) - 1:
                buf.append(", ")
        buf.append(')')
        return buf.toString()

    def getObject(self, map, key):
        return map.get(key, None)

    def getReturnClass(self, rootClassName, callChain):
        """We only match methods by name and number of parameters,
        not by parameter type.

        """
        result = Class.forName(rootClassName)                

        for member in callChain.split(".")[1:]:
            # Method
            if "(" in member:
                memberTok = StringTokenizer(member, "(, )", False)                        
                numParams = memberTok.countTokens() - 1
                member = memberTok.nextToken()
                
                methods = result.methods
                firstMatchingMethod = None
                for method in methods:
                    if (method.name == member and method.genericParameterTypes.length == numParams:
                        firstMatchingMethod = method
                        break

                if firstMatchingMethod is None:
                    raise NoSuchMethodException("No method named " + member + " with " + numParams + " parameters")
                return firstMatchingMethod.returnType
            # Field
            else:
                return result.getField(member).class
        return result
