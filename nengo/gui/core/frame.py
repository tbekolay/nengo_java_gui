from jip.embed import require
require('org.simplericity.macify:macify:1.6')

from java.awt import GraphicsEnvironment
from java.awt import Toolkit
from java.awt.event import KeyEvent
from java.lang import System
from javax.swing import FocusManager
from javax.swing import JFrame
from javax.swing import JMenuBar
from javax.swing import SwingUtilities

#import java.awt.BorderLayout;
#import java.awt.Container;
#import java.awt.Dimension;
#import java.awt.DisplayMode;
#import java.awt.GraphicsDevice;
#import java.awt.KeyEventDispatcher;
#import java.awt.Rectangle;
#import java.awt.event.KeyAdapter;
#import java.awt.event.KeyListener;
#import java.awt.event.WindowEvent;
#import java.awt.event.WindowListener;
#import java.io.ByteArrayOutputStream;
#import java.io.File;
#import java.io.FileInputStream;
#import java.io.FileOutputStream;
#import java.io.IOException;
#import java.io.ObjectInputStream;
#import java.io.ObjectOutputStream;
#import java.io.Serializable;
#import java.lang.reflect.InvocationTargetException;
#import java.util.ArrayList;
#import java.util.Collection;
#import java.util.EventListener;
#import java.util.Iterator;
#import java.util.LinkedList;

#import javax.swing.JEditorPane;
#import javax.swing.JLabel;
#import javax.swing.JMenuBar;
#import javax.swing.JOptionPane;
#import javax.swing.KeyStroke;
#import javax.swing.event.HyperlinkEvent;
#import javax.swing.event.HyperlinkListener;

#import org.simplericity.macify.eawt.ApplicationEvent;
#import org.simplericity.macify.eawt.ApplicationListener;

#import ca.nengo.plot.Plotter;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.ExitAction;
#import ca.nengo.ui.lib.actions.OpenURLAction;
#import ca.nengo.ui.lib.actions.ReversableActionManager;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.actions.ZoomToFitAction;
#import ca.nengo.ui.lib.misc.ShortcutKey;
#import ca.nengo.ui.lib.util.UIEnvironment;
#import ca.nengo.ui.lib.util.menus.MenuBuilder;
#import ca.nengo.ui.lib.world.World;
#import ca.nengo.ui.lib.world.WorldObject;
#import ca.nengo.ui.lib.world.elastic.ElasticWorld;
#import ca.nengo.ui.lib.world.piccolo.WorldImpl;
#import ca.nengo.ui.lib.world.piccolo.objects.Window;
#import ca.nengo.ui.lib.world.piccolo.primitives.PXGrid;
#import ca.nengo.ui.lib.world.piccolo.primitives.Universe;
#import edu.umd.cs.piccolo.PCamera;
#import edu.umd.cs.piccolo.activities.PActivity;
#import edu.umd.cs.piccolo.util.PDebug;
#import edu.umd.cs.piccolo.util.PPaintContext;
#import edu.umd.cs.piccolo.util.PUtil;

from org.simplericity.macify.eawt import ApplicationListener as MacAppListener

from ? import NodeContainer  # TODO

class Nengo(JFrame, MacAppListener, NodeContainer):
    serialVersionUID = 20  # TODO
    
    MENU_SHORTCUT_KEY_MASK = Toolkit.defaultToolkit.menuShortcutKeyMask

    # Name of the directory where UI Files are stored
    USER_FILE_DIR = "UIFiles"  # Get rid of this shit!

    # A String which briefly describes some commands used in this application
    WORLD_TIPS = ("<H3>Mouse</H3>"
                  "Right Click >> Context menus<BR>"
                  "Right Click + Drag >> Zoom<BR>"
                  "Scroll Wheel >> Zoom"
                  "<H3>Keyboard</H3>"
                  "CTRL/CMD F >> Search the current window<BR>"
                  "SHIFT >> Multiple select<BR>"
                  "SHIFT + Drag >> Marquee select<BR>"
                  "<H3>Additional Help</H3>" 
                  "<a href=\"http://nengo.ca/docs/html/index.html\">"
                  "Full documentation</a>"
                  "(http://nengo.ca/docs/html/index.html)<BR>"
                  "<a href=\"http://nengo.ca/faq\">"
                  "Frequently Asked Questions</a> (http://nengo.ca/faq)")
    
    VERSION = 2.0

    # String used in the UI to identify Nengo
    APP_NAME = "Nengo version " + str(VERSION)

    # Description of Nengo to be shown in the "About" Dialog box
    ABOUT = ("<H3>" + Nengo.APP_NAME + "</H3>"
             "<a href=http://www.nengo.ca>www.nengo.ca</a>"
             "<p>&copy; Centre for Theoretical Neuroscience (ctn.uwaterloo.ca) 2006-2012</p>"
             "<b>Contributors:</b> Bryan&nbsp;Tripp, Shu&nbsp;Wu, Chris&nbsp;Eliasmith, Terry&nbsp;Stewart, James&nbsp;Bergstra, "
             "Trevor&nbsp;Bekolay, Dan&nbsp;Rasmussen, Xuan&nbsp;Choo, Travis&nbsp;DeWolf, "
             "Yan&nbsp;Wu, Eric&nbsp;Crawford, Eric&nbsp;Hunsberger, Carter&nbsp;Kolbeck, "
             "Jonathan&nbsp;Lai, Oliver&nbsp;Trujillo, Peter&nbsp;Blouw, Pete&nbsp;Suma, Patrick&nbsp;Ji, Jeff&nbsp;Orchard</p>"
             "<p>This product contains several open-source libraries (copyright their respective authors). "
             "For more information, consult <tt>lib/library-licenses.txt</tt> in the installation directory.</p>"
             "<p>This product includes software developed by The Apache Software Foundation (http://www.apache.org/).</p>";

    # Use the configure panel in the right side? Otherwise it's a pop-up.
    CONFIGURE_PLANE_ENABLED = True

    # File extension for Nengo Nodes
    NEONODE_FILE_EXTENSION = "nef";

    PLUGIN_DIRECTORY = "plugins";

    # The singleton instance of the NengoGraphics object
    def getInstance(self):
        Util.Assert(instanceof(UIEnvironment.instance Nengo))
        return UIEnvironment.instance

    def __init__(self):
        self.actionManager
        self.escapeFullScreenModeListener
        self.graphicsDevice
        self.isFullScreenMode
        self.preferences
        self.shortcutKeys
        self.topWindowGraphicsEnvironment
        self.universe
        self.worldMenu
        self.editMenu
        self.runMenu
        
        self.filechooser
        self.clipboard

        self.pythonInterpreter
        self.scriptConsole
        self.dataListViewer
        self.templateViewer
        self.templatePanel
        self.toolbarPanel

        self.toolbarPane
        self.templatePane
        self.configPane
        self.dataViewerPane
        self.scriptConsolePane
        self.splitPanes

        self.progressIndicator
        
        JFrame.__init__(GraphicsEnvironment.localGraphicsEnvironment
                        .defaultScreenDevice.defaultConfiguration)
        
        if not SwingUtilities.isEventDispatchThread():
            try:
                SwingUtilities.invokeAndWait(run=self.initialize)
            except InvocationTargetException, e:
                e.targetException.printStackTrace()
            except Exception e:
                e.printStackTrace()
        else:
            self.initialize()

        # Setup icon
        try:
            image = ImageIO.read(self.class.classLoader.resource(
                "ca/nengo/ui/nengologo256.png"))
            self.iconImage = image
        except IOException, e:
            e.printStackTrace()

    def initMenu(self):
        """Initializes the menu."""
        menuBar = JMenuBar()
        menuBar.border = None

        # Style.applyMenuStyle(menuBar, True)

        fileMenu = MenuBuilder("File")
        fileMenu.jMenu.mnemonic = KeyEvent.VK_F
        self.initFileMenu(fileMenu)
        fileMenu.addAction(ExitAction(self, "Quit"), KeyEvent.VK_P)
        menuBar.add(fileMenu.jMenu)

        editMenu = MenuBuilder("Edit")
        editMenu.jMenu.mnemonic = KeyEvent.VK_E

        menuBar.add(editMenu.jMenu)

        self.initViewMenu(menuBar)

        runMenu = MenuBuilder("Run")
        runMenu.jMenu.mnemonic = KeyEvent.VK_R

        menuBar.add(runMenu.jMenu)

        worldMenu = MenuBuilder("Misc")
        worldMenu.jMenu.mnemonic = KeyEvent.VK_O
        menuBar.add(worldMenu.jMenu)

        self.updateWorldMenu()
        self.updateEditMenu()
        self.updateRunMenu()

        helpMenu = MenuBuilder("Help")
        helpMenu.jMenu.mnemonic = KeyEvent.VK_H
        menuBar.add(helpMenu.jMenu)

        helpMenu.addAction(OpenURLAction("Documentation (opens in browser)",
                "http://www.nengo.ca/documentation"), KeyEvent.VK_F1)
        helpMenu.addAction(TipsAction("Tips and Commands", False), KeyEvent.VK_T)
        isMacOS = System.getProperty("mrj.version") is not None
        if not isMacOS):
            helpMenu.addAction(AboutAction("About"), KeyEvent.VK_A)

        menuBar.visible = True
        self.jMenuBar = menuBar

    def chooseBestDisplayMode(self, device):
        best = self.getBestDisplayMode(device)
        is best is not None:
            device.displayMode = best

    def createDefaultCamera(self):
        return PUtil.createBasicScenegraph()

    def createWorld(self):
        raise NotImplementedError

    def getBestDisplayMode(self, device):
        modes = device.displayModes
        for prefMode in self.getPreferredDisplayModes(device):
            for mode in modes:
                if (mode.width == prefMode.width
                        and mode.height == prefMode.height 
                        and mode.bitDepth == prefMode.bitDepth):
                    return prefMode

        return None

    def getPreferredDisplayModes(self, device):
        """By default return the current display mode.
        
        Subclasses may override this method to return
        other modes in the collection.
        
        """
        result = [device.displayMode]
        
        # result.append(DisplayMode(640, 480, 32, 0))
        # result.append(DisplayMode(640, 480, 16, 0))
        # result.append(DisplayMode(640, 480, 8, 0))

        return result

#    protected ShortcutKey[] getShortcutKeys() {
#        return shortcutKeys;
#    }

    def initFileMenu(self, menu):
        """Use this function to add menu items to the frame menu bar."""
        pass


    def initialize(self):
        class ShortcutDispatcher(KeyEventDispatcher):
            def dispatchKeyEvent(self, e):
                if self.shortcutKeys is not None and e.getID() == KeyEvent.KEY_PRESSED:
                    for shortcutKey in self.shortcutKeys:
                        if (shortcutKey.modifiers == e.modifiers
                                and shortcutKey.keyCode == e.keyCode):
                            shortcutKey.action.doAction()
                            return True
                return False
        
        # Initialize shortcut keys
        FocusManager.currentManager.addKeyEventDispatcher(ShortcutDispatcher())

        graphicsDevice = GraphicsEnvironment.localGraphicsEnvironment.defaultScreenDevice
        self.loadPreferences()
        UIEnvironment.instance = self
        
        if preferences.isWelcomeScreen():
            preferences.welcomeScreen = False

            SwingUtilities.invokeLater(run=TipsAction("", True).doAction)

        self.restoreDefaultTitle()

        actionManager = ReversableActionManager(self)
        self.contentPane.layout = BorderLayout()

        universe = Universe()
        universe.minimumSize = Dimension(200, 200)
        universe.preferredSize = Dimension(400, 400)
        universe.initialize(self.createWorld())
        universe.focusable = True

        # self.contentPane.add(canvas)
        # canvas.preferredSize = Dimension(200, 200)

        self.initLayout(universe)

        self.bounds = Rectangle(100, 100, 800, 600)
        self.background = None
        self.addWindowListener(MyWindowListener())

        try:
            self.defaultCloseOperation = JFrame.DO_NOTHING_ON_CLOSE
        except SecurityException, e:
            e.printStackTrace()

        universe.selectionMode = False

        self.initMenu()

        # Initialize shortcut keys
        shortcuts = []
        self.constructShortcutKeys(shortcuts)

        self.validate();
        self.fullScreenMode = False

    def constructShortcutKeys(self, shortcuts):
        shortcuts.append(ShortcutKey(MENU_SHORTCUT_KEY_MASK, KeyEvent.VK_0,
                ZoomToFitAction("Zoom to fit", self.topWorld)))
    
    def getTopWorld(self):
        window = self.topWindow

        if window is not None:
            wo = window.contents
            if instanceof(wo, World):
                return wo
            else:
                return None
        else:
            return self.world
    
    def initLayout(self, canvas):
        cp = self.contentPane
        cp.add(canvas)
        canvas.requestFocus()
    
    def initViewMenu(self, menuBar):
        """Use this function to add menu items to the frame menu bar."""
        pass

    def loadPreferences(self):
        """Loads saved preferences related to the application."""
        userfile = File(USER_FILE_DIR)
        if not userfile.exists():
            userfile.mkdir()

        preferencesFile = File(USER_FILE_DIR, "userSettings")

        if preferencesFile.exists():
            try:
                fis = FileInputStream(preferencesFile)
                ois = ObjectInputStream(fis)
                try:
                    preferences = ois.readObject()
                except ClassNotFoundException:
                    System.out.println("Could not load preferences")
            except IOException:
                System.out.println("Could not read preferences file")
        
        if preferences is None:
            preferences = UserPreferences()
        preferences.apply(self)

    def savePreferences(self):
        """Save preferences to file."""
        userfile = File(USER_FILE_DIR)
        if not userfile.exists():
            userfile.mkdir()

        preferencesFile = File(USER_FILE_DIR, "userSettings")

        bos = ByteArrayOutputStream()
        try:
            oos = ObjectOutputStream(bos)
            oos.writeObject(preferences)

            fos = FileOutputStream(preferencesFile)
            fos.write(bos.toByteArray())
            fos.flush()
            fos.close()
        except IOException, e:
            e.printStackTrace()

    def updateEditMenu(self):
        """Updates the menu edit"""
        editMenu.reset()

        editMenu.addAction(UndoAction(), KeyEvent.VK_Z,
            KeyStroke.getKeyStroke(KeyEvent.VK_Z, MENU_SHORTCUT_KEY_MASK))

        editMenu.addAction(RedoAction(), KeyEvent.VK_Y,
            KeyStroke.getKeyStroke(KeyEvent.VK_Y, MENU_SHORTCUT_KEY_MASK))
        
        editMenu.jMenu.addSeparator()

    def updateRunMenu(self):
        """Updates the menu run"""
        runMenu.reset()
        # Configure parallelization

    def updateWorldMenu(self):
        """Updates the menu world"""
        worldMenu.reset()

        if not self.universe.isSelectionMode():
            worldMenu.addAction(SwitchToSelectionMode(), KeyEvent.VK_S)
        else:
            worldMenu.addAction(SwitchToNavigationMode(), KeyEvent.VK_S)

        worldMenu.jMenu.addSeparator()
        worldMenu.addAction(CloseAllPlots(), KeyEvent.VK_M)
        worldMenu.jMenu.addSeparator()

        if not self.isFullScreenMode:
            # worldMenu.addAction(TurnOnFullScreen(), KeyEvent.VK_F)
        else:
            # worldMenu.addAction(TurnOffFullScreen(), KeyEvent.VK_F)

        if not preferences.isEnableTooltips():
            worldMenu.addAction(TurnOnTooltips(), KeyEvent.VK_T)
        else:
            worldMenu.addAction(TurnOffTooltips(), KeyEvent.VK_T)

        if not PXGrid.isGridVisible():
            worldMenu.addAction(TurnOnGrid(), KeyEvent.VK_G)
        else:
            worldMenu.addAction(TurnOffGrid(), KeyEvent.VK_G)

        worldMenu.jMenu.addSeparator()
        
        qualityMenu = worldMenu.addSubMenu("Rendering Quality")

        qualityMenu.jMenu.mnemonic = KeyEvent.VK_Q

        qualityMenu.addAction(LowQualityAction(), KeyEvent.VK_L)
        qualityMenu.addAction(MediumQualityAction(), KeyEvent.VK_M)
        qualityMenu.addAction(HighQualityAction(), KeyEvent.VK_H)

        debugMenu = worldMenu.addSubMenu("Debug")
        debugMenu.jMenu.mnemonic = KeyEvent.VK_E

        if not PDebug.debugPrintUsedMemory:
            debugMenu.addAction(ShowDebugMemory(), KeyEvent.VK_S)
        else:
            debugMenu.addAction(HideDebugMemory(), KeyEvent.VK_H)

    def addActivity(self, activity):
        return self.universe.root.addActivity(activity)

    def addEscapeFullScreenModeListener(self):
        """This method adds a key listener that will take this PFrame out of
        full screen mode when the escape key is pressed. This is called for you
        automatically when the frame enters full screen mode.
        
        """
        self.removeEscapeFullScreenModeListener()
#        escapeFullScreenModeListener = new KeyAdapter() {
#            @Override
#            public void keyPressed(KeyEvent aEvent) {
#                if (aEvent.getKeyCode() == KeyEvent.VK_ESCAPE) {
#                    setFullScreenMode(false);
#                }
#            }
#        };
        self.universe.addKeyListener(escapeFullScreenModeListener)

    def addWorldWindow(self, window):
        self.universe.world.sky.addChild(window)

    def exitAppFrame(self):
        """Called when the user closes the Application window."""
        self.savePreferences()
        System.exit(0)

    def getAboutString(self):
        """Return string which describes what the application is about"""
        raise NotImplementedError

    def getActionManager(self):
        """Action manager responsible for managing actions.
        
        Enables undo and redo functionality.
        
        """
        return self.actionManager

    def getAppName(self):
        """Name of the application"""
        raise NotImplementedError

    def getAppWindowTitle(self):
        raise NotImplementedError

    def getTopWindow(self):
        return self.topWindow

    def getUniverse(self):
        """Canvas which hold the zoomable UI."""
        return self.universe

    def getWorld(self):
        return self.universe.world

    def removeEscapeFullScreenModeListener(self):
        """This method removes the escape full screen mode key listener.
        It will be called for you automatically when full screen mode exits,
        but the method has been made public for applications that wish to use
        other methods for exiting full screen mode.
        
        """
        if escapeFullScreenModeListener is not None:
            self.universe.removeKeyListener(self.escapeFullScreenModeListener)
            self.escapeFullScreenModeListener = None

    def restoreDefaultTitle(self):
        self.title = self.appWindowTitle

    def reversableActionsUpdated(self):
        """Called when reversable actions have changed. Updates the edit menu."""
        self.updateEditMenu()

    def setFullScreenMode(self, fullScreenMode):
        self.isFullScreenMode = fullScreenMode
        if fullScreenMode:
            self.addEscapeFullScreenModeListener()

            if self.isDisplayable():
                self.dispose()

            self.undecorated = True
            self.resizable = False
            self.graphicsDevice.fullScreenWindow = self

            if self.graphicsDevice.isDisplayChangeSupported():
                self.chooseBestDisplayMode(graphicsDevice)
            self.validate()
        else:
            self.removeEscapeFullScreenModeListener();

            if self.isDisplayable():
                self.dispose()

            self.undecorated = False
            self.resizable = True
            self.graphicsDevice.fullScreenWindow = None
            self.validate()
            self.visible = True

    def setTopWindow(self, window):
        self.topWindow = window
        if topWindow is not None:
            self.title = window.name + " - " + self.appWindowTitle
        else:
            UIEnvironment.instance.restoreDefaultTitle()

    class HighQualityAction(StandardAction):
        """Action to set rendering mode to high quality."""
        def __init__(self):
            StandardAction.__init__(self, "High Quality")

        def action(self):
            self.universe.defaultRenderQuality = PPaintContext.HIGH_QUALITY_RENDERING
            self.universe.animatingRenderQuality = PPaintContext.HIGH_QUALITY_RENDERING
            self.universe.interactingRenderQuality = PPaintContext.HIGH_QUALITY_RENDERING
            self.updateWorldMenu()


    # Everything starting with handle is done for MacOSX only
    def handleAbout(self, event):
        AboutAction("About").doAction()
        event.handled = True

    def handleOpenApplication(self, event):
        pass

    def handleOpenFile(self, event):
        pass

    def handlePreferences(self, event):
        pass

    def handlePrintFile(self, event):
        JOptionPane.showMessageDialog(self, "Sorry, printing not implemented")

    def handleQuit(self, event):
        ExitAction(self, "Quit").doAction()

    def handleReOpenApplication(self, event):
        pass

    class AboutAction(StandardAction):
        """Action to show the 'about' dialog"""
        def __init__(self, actionName):
            StandardAction.__init__(self, "About", actionName)
            
        def action(self):
            width = 350
            css = ("<style type = \"text/css\">"
                   "body { width: " + width + "px }"
                   "p { margin-top: 12px }"
                   "b { text-decoration: underline }"
                   "</style>")
            editor = JLabel("<html><head>" + css + "</head><body>"
                            + self.aboutString + "</body></html>")
            JOptionPane.showMessageDialog(UIEnvironment.instance, editor,
                "About " + self.appName, JOptionPane.PLAIN_MESSAGE)

    class HideDebugMemory(StandardAction):
        """Action to hide debug memory messages printed to the console."""
        def __init__(self):
            StandardAction.__init__(self, "Stop printing Memory Used to console")

        def action(self):
            PDebug.debugPrintUsedMemory = False
            self.updateWorldMenu()

    class LowQualityAction(StandardAction):
        """Action to set rendering mode to low quality."""
        def __init__(self):
            StandardAction.__init__(self, "Low Quality")

        def action(self):
            self.universe.defaultRenderQuality = PPaintContext.LOW_QUALITY_RENDERING
            self.universe.animatingRenderQuality = PPaintContext.LOW_QUALITY_RENDERING
            self.universe.interactingRenderQuality = PPaintContext.LOW_QUALITY_RENDERING
            self.updateWorldMenu()

    class MediumQualityAction(StandardAction):
        """Action to set rendering mode to medium quality."""
        def __init__(self):
            StandardAction.__init__(self, "Medium Quality")

        def action(self):
            self.universe.defaultRenderQuality = PPaintContext.HIGH_QUALITY_RENDERING
            self.universe.animatingRenderQuality = PPaintContext.LOW_QUALITY_RENDERING
            self.universe.interactingRenderQuality = PPaintContext.LOW_QUALITY_RENDERING
            self.updateWorldMenu()

    class MinimizeAllWindows(StandardAction):
        """Minimizes all windows in the top-level world."""
        def __init__(self):
            StandardAction.__init__(self, "Minimize all windows")
        
        def action(self):
            self.world.minimizeAllWindows()

    class MyWindowListener(WindowListener):
        """Listener which listens for Application window close events."""
        def windowActivated(self, event):
            pass

        def windowClosed(self, event):
            pass

        def windowClosing(self, event):
            self.exitAppFrame()

        def windowDeactivated(self, event):
            pass

        def windowDeiconified(self, event):
            pass

        def windowIconified(self, event):
            pass

        def windowOpened(self, event):
            pass


    class RedoAction(StandardAction):
        """Action to redo the last reversable action"""
        def __init__(self):
            StandardAction.__init__(self, "Redo: "
                                    + actionManager.redoActionDescription)
            if not actionManager.canRedo():
                self.enabled = False

        def action(self):
            actionManager.redoAction()

    class ShowDebugMemory(StandardAction)
        """Action to enable the printing of memory usage messages to the console"""
        def __init__(self):
            StandardAction.__init__(self, "Print Memory Used to console") 
        
        def action(self):
            PDebug.debugPrintUsedMemory = True
            self.updateWorldMenu();

    class SwitchToNavigationMode(StandardAction):
        """Action to switch to navigation mode"""
        def __init__(self):
            StandardAction.__init__(self, "Switch to Navigation Mode")

        def action(self):
            self.universe.selectionMode = False
            self.updateWorldMenu();

    class SwitchToSelectionMode(StandardAction)
        """Action to switch to selection mode"""
        def __init__(self):
            StandardAction.__init__(self,"Switch to Selection Mode   Shift")

        def action(self):
            self.universe.selectionMode = True
            self.updateWorldMenu()

    def getHelp(self):
        return WORLD_TIPS + "<BR>"

    class TipsAction(StandardAction):
        """Action which shows the tips dialog"""
        def __init__(self, actionName, isWelcomeScreen):
            StandardAction.__init__(self, "Show UI tips", actionName)
            self.welcome = isWelcomeScreen

        def action(self):
            if self.welcome:
                appendum = ("To show this message again, click "
                            "<b>Help -> Tips and Commands</b>")
                editor = JEditorPane("text/html", "<html><H2>Welcome to "
                                     + self.appName + "</H2>" + self.help
                                     + "<BR><BR>" + appendum + "</html>")
            else:
                editor = JEditorPane("text/html", "<html>" + self.help + "</html>")
            
            editor.editable = False
            editor.opaque = False
            editor.addHyperlinkListener(HyperlinkListener(
                hyperlinkUpdate=openurlaction))
#                    if (HyperlinkEvent.EventType.ACTIVATED.equals(hle.getEventType())) {
#                        new OpenURLAction(hle.getDescription(),hle.getDescription()).doAction();
#                    }                    

            JOptionPane.showMessageDialog(UIEnvironment.instance, editor,
                                          self.appName + " Tips", JOptionPane.PLAIN_MESSAGE)

    class TurnOffFullScreen(StandardAction):
        """Action to turn off full screen mode"""
        def __init__(self):
            StandardAction.__init__(self, "Full screen off")

        def action(self):
            self.fullScreenMode = False
            self.updateWorldMenu()

    class TurnOffGrid(StandardAction):
        """Action to turn off the grid"""
        def __init__(self):
            StandardAction.__init__(self, "Grid off")

        def action(self):
            preferences.gridVisible = False
            self.updateWorldMenu()

    class TurnOffTooltips(StandardAction):
        """Action to turn off tooltips"""
        def __init__(self):
            StandardAction.__init__(self, "Autoshow Tooltips off")

        def action(self):
            self.preferences.enableTooltips = False
            self.updateWorldMenu();

    class TurnOnFullScreen(StandardAction):
        """Action to turn on full screen mode"""
        def __init__(self):
            StandardAction.__init__(self, "Full screen on")

        def action(self):
            self.fullScreenMode = True
            self.updateWorldMenu()

    class TurnOnGrid(StandardAction):
        """Action to turn on the grid"""
        def __init__(self):
            StandardAction.__init__(self, "Grid on")

        def action(self):
            self.preferences.gridVisible = True
            self.updateWorldMenu()

    class TurnOnTooltips(StandardAction):
        """Action to turn on tooltips"""
        def __init__(self):
            StandardAction.__init__(self, "Autoshow Tooltips on")

        def action(self):
            self.preferences.enableTooltips = True
            self.updateWorldMenu()

    class UndoAction(StandardAction):
        """Action which undos the last reversable action"""
        def __init__(self):
            StandardAction.__init__(self, "Undo: " + actionManager.undoActionDescription)
            if not actionManager.canUndo():
                self.enabled = False

        def action(self):
            actionManager.undoAction()

    class CloseAllPlots(StandardAction):
        """Action to close all plots"""
        def __init__(self):
            StandardAction.__init__(self, "Close all plots")

        def action(self):
            Plotter.closeAll()



    def setApplication(self, application):
        application.addApplicationListener(self)
        application.enabledPreferencesMenu = False
        icon = BufferedImage(256, 256, BufferedImage.TYPE_INT_ARGB)
        try:
            icon = ImageIO.read(self.class.classLoader.getResource("ca/nengo/ui/nengologo256.png"))
        except IOException, e:
            e.printStackTrace()
        application.applicationIconImage = icon

    def setTemplatePanel(self, panel):
        """template.py calls this function to provide a template bar"""
        self.templatePanel = panel

    def setToolbar(self, bar):
        """toolbar.py calls this function to provide a toolbar"""
        self.toolbarPanel = bar;

    def NodeContainer getTopNodeContainer(self):
        window = self.topWindow

        if window is not None and isinstance(window.contents, NodeContainer):
            return window.contents
        elif window is None:
            return self

        return None

    def initialize(self, debug=False):
        self.clipboard = NengoClipboard()
        clipboard.addClipboardListener(NengoClipboard.ClipboardListener(
            clipboardChanged=self.updateEditMenu)

        SelectionHandler.addSelectionListener(SelectionHandler.SelectionListener(
#            public void selectionChanged(Collection<WorldObject> objs) {
#                updateEditMenu();
#                updateRunMenu();
#                updateScriptConsole();
#                updateConfigurationPane();
#            }
#        });

#        super.initialize();

        uienvironment['DEBUG'] = debug

        self.initializeSimulatorSourceFiles()

        if self.fileChooser is None:
            FileChooser = NeoFileChooser();

        # Set up Environment variables
        Environment.userInterface = True

        # Attach listeners for Script Console
        self.initScriptConsole()

        # Register plugin classes
        self.registerPlugins()

        self.extendedState = NengoConfigManager.getUserInteger(
            UserProperties.NengoWindowExtendedState, JFrame.MAXIMIZED_BOTH))

    def initLayout(self, canvas):
        try:
            # Tell the UIManager to use the platform look and feel
            laf = UIManager.systemLookAndFeelClassName()
            if laf == "com.sun.java.swing.plaf.gtk.GTKLookAndFeel":
                laf = "javax.swing.plaf.metal.MetalLookAndFeel"
                desktopfile = File(System.getProperty("user.home") +
                        "/.local/share/applications/nengo.desktop")
                if not desktopfile.exists():
                    defaultdesktop = File(self.class.classLoader.
                            getResource("ca/nengo/ui/nengo.desktop").path)
                    Util.copyFile(defaultdesktop, desktopfile)
                
                # df = DesktopFile.initialize("nengo", "NengoLauncher")
                # df.icon = self.class.classLoader.
                #     getResource("ca/nengo/ui/nengologo256.png").path
                # df.command = "TODO"
                # df.update()

            UIManager.lookAndFeel = laf

            # UIManager.put("Slider.paintValue", Boolean.FALSE)
        except IOException:
            System.out.println("nengo.desktop not copied.")
        except UnsupportedLookAndFeelException, e:
            e.printStackTrace()
        except ClassNotFoundException, e:
            e.printStackTrace()
        except InstantiationException, e:
            e.printStackTrace()
        except IllegalAccessException, e:
            e.printStackTrace()

        System.setProperty("swing.aatext", "true")

        #####################################################
        ### Create split pane components

        # creating the script console calls all python init stuff
        # so call it first (make toolbar, etc.)
        pythonInterpreter = PythonInterpreter()
        scriptConsole = ScriptConsole(pythonInterpreter)
        NengoStyle.applyStyle(scriptConsole)

        if self.toolbarPanel is None or self.templatePanel is None:
            # these should be made and set by template.py and toolbar.py
            # when the scriptConsole is created, so we shouldn't be here
            raise NullPointerException("toolbarPanel or templatePanel not created!")

        dataListViewer = DataListView(SimulatorDataModel(), self.scriptConsole)

        templateViewer = JScrollPane(templatePanel,
                ScrollPaneConstants.VERTICAL_SCROLLBAR_ALWAYS,
                ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER)
        templateViewer.verticalScrollBar.unitIncrement = 20
        templateViewer.revalidate()
        templateWithScrollbarSize = templateViewer.preferredSize
        templateViewer.verticalScrollBarPolicy = ScrollPaneConstants.VERTICAL_SCROLLBAR_AS_NEEDED)

        self.contentPane.add(templateViewer, BorderLayout.WEST)

        #####################################################
        ### Create nested split panes
        configPane = ConfigurationPane(canvas)

        scriptConsolePane = AuxillarySplitPane(configPane.toJComponent(), scriptConsole,
                "Script Console", AuxillarySplitPane.Orientation.Bottom)

        dataViewerPane = AuxillarySplitPane(scriptConsolePane, dataListViewer,
                "Data Viewer", AuxillarySplitPane.Orientation.Left)

        templatePane = AuxillarySplitPane(dataViewerPane, templateViewer,
                "Templates", AuxillarySplitPane.Orientation.Left,
                templateWithScrollbarSize, False)
        templatePane.resizable = False
        templatePane.auxVisible = True

        toolbarPane = AuxillarySplitPane(templatePane, toolbarPanel,
                "Toolbar", AuxillarySplitPane.Orientation.Top,
                toolbarPanel.preferredSize, False)
        toolbarPane.resizable = False
        toolbarPane.auxVisible = True

        self.contentPane.add(toolbarPane)

        # Add all panes to the list. The order added controls
        # the order in the View menu
        splitPanes = []
        splitPanes.append(scriptConsolePane)
        splitPanes.append(dataViewerPane)
        if CONFIGURE_PLANE_ENABLED:
            splitPanes.apend(configPane.toJComponent())
        splitPanes.append(templatePane)
        splitPanes.append(toolbarPane)

        canvas.requestFocus()

        progressIndicator = ProgressIndicator()
        self.contentPane.add(progressIndicator, BorderLayout.SOUTH)

    def initScriptConsole(self):
        self.scriptConsole.addVariable("world", ScriptWorldWrapper(self))

        # add listeners
        """
        self.world.ground.addChildrenListener(WorldObject.ChildListener() {

            public void childAdded(WorldObject wo) {
                if (wo instanceof ModelObject) {
                    final ModelObject modelObject = ((ModelObject) wo);
                    //                    final Object model = modelObject.getModel();
                    final String modelName = modelObject.getName();

                    try {
                        //scriptConsole.addVariable(modelName, model);

                        modelObject.addPropertyChangeListener(Property.REMOVED_FROM_WORLD,
                                new WorldObject.Listener() {
                            public void propertyChanged(Property event) {
                                scriptConsole.removeVariable(modelName);
                                modelObject.removePropertyChangeListener(Property.REMOVED_FROM_WORLD,
                                        this);
                            }
                        });

                    } catch (Exception e) {
                        UserMessages.showError("Error adding network: " + e.getMessage());
                    }
                }
            }

            public void childRemoved(WorldObject wo) {
                /*
                 * Do nothing here. We don't remove the variable here directly
                 * because the network has already been destroyed and no longer
                 * has a reference to it's model.
                 */

            }

        });
        """

    def initializeSimulatorSourceFiles(self):
        """Find and initialize the main simulator source code."""
        
        savedSourceLocation = NengoConfigManager.nengoConfig.getProperty("simulator_source")

        simulatorSource = "../simulator/src/java/main" if savedSourceLocation is None else  savedSourceLocation

        simulatorSourceFile = File(simulatorSource)
        if not simulatorSourceFile.exists():
            Util.debugMsg("Could not find simulator source files at "
                    + simulatorSourceFile.absoluteFile.toString())

        JavaSourceParser.addSource(simulatorSourceFile)

    def registerPlugins(self):
        try:
            pluginUrls = []
            pluginJars = []

            pluginDir = File(PLUGIN_DIRECTORY)
            pluginUrls.append(pluginDir.toURI().toURL())

            pluginJarFiles = pluginDir.listFiles(FilenameFilter() {}
                # public boolean accept(File dir, String name) {
                #        if (name.endsWith("jar")) {
                #              return true;
                #        } else {
                #            return false;
                #        }

            for jarFile in pluginJarFiles:
                pluginUrls.append(jarFile.toURI().toURL())

            URLClassLoader urlClassLoader = URLClassLoader(pluginUrls)

            for jarFile in pluginJarFiles:
                try:
                    jar = JarFile(jarFile)
                    pluginJars.append(jar)
                    entries = jar.entries()
                    while entries.hasMoreElements():
                        entry = entries.nextElement()
                        fileName = entry.name
                        if fileName.endsWith(".class"): 
                            try:
                                className = fileName.substring(0,
                                    fileName.lastIndexOf('.')).replace('/', '.')
                                newClass = urlClassLoader.loadClass(className)

                                Util.debugMsg("Registering class: " +
                                              newClass.name)
                                ClassRegistry.instance.register(newClass)

                            except ClassNotFoundException,  e:
                                e.printStackTrace()
                            except NoClassDefFoundError, e:
                                # this only occurs for nested classes (i.e.
                                # those with dollar signs in class name),
                                # and perhaps only on the Mac
                                # System.out.println(className)
                                # e.printStackTrace()
                                pass

                    pluginUrls.append(jarFile.toURI().toURL())
                except IOException, e:
                    e.printStackTrace()
        except MalformedURLException, e:
            e.printStackTrace()

    def getNengoWorld(self):
        self.world

    def constructShortcutKeys(self, shortcuts):
        super.constructShortcutKeys(shortcuts)

    def promptToSaveModels(self):
        """Prompt user to save models in NengoGraphics.
        This is most likely called right before the application is exiting.
        
        """
        saveSuccessful = True

        for wo in self.world.ground.children:
            if isinstance(wo, UINeoNode):
                saveAction = SaveNodeAction(wo, True)
                saveAction.doAction()
                saveSuccessful = saveSuccessful and saveAction.saveSuccessful

        return saveSuccessful

    def updateEditMenu(self):
        super.updateEditMenu()

        selectedObjects = SelectionHandler.activeSelection

        if selectedObjects is not None and selectedObjects.size() > 0:
            selectedArray = []
            selectedModelObjects = []
            for obj in selectedObjects:
                if isinstance(obj, UINeoNode):
                    selectedArray.append(obj)
                if isinstacne(obj, ModelObject):
                    selectedModelObjects.append(obj)

            cutAction = CutAction("Cut", selectedArray)
            copyAction = CopyAction("Copy", selectedArray)
            removeAction = RemoveModelAction("Remove", selectedModelObjects)
        else:
            cutAction = DisabledAction("Cut", "No object selected")
            copyAction = DisabledAction("Copy", "No object selected")
            removeAction = DisabledAction("Remove", "No objects to remove")

        if self.clipboard.hasContents():
            pasteAction = StandardAction("Paste") {
#                private static final long serialVersionUID = 1L;
#                @Override
#                protected void action() {
#                    // look for the active mouse handler. If it exists, it should contain
#                    // the current mouse position (from the mousemoved event), so use this
#                    // to create a new PasteEvent
#                    PasteAction a;
#                    MouseHandler mh = MouseHandler.getActiveMouseHandler();
#                    if (mh != null) {
#                        a = new PasteAction("Paste", (NodeContainer)mh.getWorld(), true);
#                        Point2D pos = mh.getMouseMovedRelativePosition();
#                        if (pos != null) {
#                            a.setPosition(pos.getX(), pos.getY());
#                        }
#                    } else {
#                        a = new PasteAction("Paste", NengoGraphics.getInstance(), true);
#                    }
#                    a.doAction();
#                }
#            };
        else:
            pasteAction = DisabledAction("Paste", "No object is in the clipboard")

        editMenu.addAction(copyAction, KeyEvent.VK_C,
            KeyStroke.getKeyStroke(KeyEvent.VK_C, MENU_SHORTCUT_KEY_MASK))
        editMenu.addAction(cutAction, KeyEvent.VK_X,
            KeyStroke.getKeyStroke(KeyEvent.VK_X, MENU_SHORTCUT_KEY_MASK))
        editMenu.addAction(pasteAction, KeyEvent.VK_V,
            KeyStroke.getKeyStroke(KeyEvent.VK_V, MENU_SHORTCUT_KEY_MASK))
        editMenu.addAction(removeAction, KeyEvent.VK_R,
            KeyStroke.getKeyStroke(KeyEvent.VK_DELETE, 0))

    def updateRunMenu(self):
        super.updateRunMenu();

        selectedObj = SelectionHandler.activeObject
        node = None

        if selectedObj is not None:
            if isinstance(selectedObj, UINeoNode):
                node = selectedObj
            elif isinstance(selectedObj, UIProjection):
                if selectedObj.termination is not None:
                    node = selectedObj.termination.nodeParent
                else:
                    node = selectedObj.originUI.nodeParent
            elif isinstance(selectedObj, Widget):
                node = selectedObj.nodeParent
            elif isinstance(selectedObj, UIProbe):
                node = selectedObj.probeParent

        if node is not None:
            while node.networkParent is not None:
                node = node.networkParent
            network = node

            simulateAction = RunSimulatorAction("Simulate " + network.name, network)
            interactivePlotsAction = RunInteractivePlotsAction(network)
        else:
            simulateAction = DisabledAction("Simulate", "No object selected")
            interactivePlotsAction = DisabledAction("Interactive Plots", "No object selected")

        runMenu.addAction(simulateAction, KeyEvent.VK_F4,
            KeyStroke.getKeyStroke(KeyEvent.VK_F4, 0))
        runMenu.addAction(interactivePlotsAction, KeyEvent.VK_F5,
            KeyStroke.getKeyStroke(KeyEvent.VK_F5, 0))

    def createWorld(self):
        return NengoWorld()

    def addNodeModel(self, node, posX=None, posY=None):
        if posX or posY:
            assert posX and posY

        nodeContainer = self.topNodeContainer()
        if nodeContainer is not self and nodeContainer is not None:
            # Delegate to the top Node Container in the Application
            return nodeContainer.addNodeModel(node, posX, posY)
        elif nodeContainer is self:
            nodeUI = slef.nengoWorld.addNodeModel(node, posX, posY)
            try:
                DragAction.dropNode(nodeUI)
            except UserCancelledException, e:
                # the user should not be given a chance to do this
                raise ContainerException("Unexpected cancellation of action by user")
            return nodeUI
        else:
            raise ContainerException("There are no containers to put this node")

    def captureInDataViewer(self, network):
        dataListViewer.captureSimulationData(network)

    def configureObject(self, obj):
        if CONFIGURE_PLANE_ENABLED:
            configPane.toJComponent().auxVisible = True
            configPane.configureObj(obj)
        else:
            ConfigUtil.configure(nengoinstance, obj)

    def exitAppFrame(self):
        if self.world.ground.childrenCount > 0:
            response = JOptionPane.showConfirmDialog(self,
                    "Save models?", "Exiting " + self.appName,
                    JOptionPane.YES_NO_CANCEL_OPTION)
            if response == JOptionPane.YES_OPTION:
                if not promptToSaveModels():
                    return
            elif response == JOptionPane.CANCEL_OPTION or response == JOptionPane.CLOSED_OPTION:
                # cancel exit
                return

        self.saveUserConfig()
        super.exitAppFrame()

    def saveUserConfig(self):
        NengoConfigManager.setUserProperty(
            UserProperties.NengoWindowExtendedState, self.extendedState)
        NengoConfigManager.saveUserConfig()

    def getAboutString(self):
        return ABOUT

    def getAppName(self):
        return APP_NAME

    def getAppWindowTitle(self):
        return "Nengo Workspace"


    def getClipboard(self):
        return self.clipboard

    def getNodeModel(self, name):
        nodeContainer = self.topNodeContainer()
        if nodeContainer is not slef and nodeContainer is not None:
            # Delegate to the top Node Container in the Application
            return nodeContainer.getNodeModel(name)
        elif nodeContainer is self:
            return self.nengoWorld.getNodeModel(name)
        return None

    def getPythonInterpreter(self):
        return self.pythonInterpreter

    def getProgressIndicator(self):
        return self.progressIndicator

    def getScriptConsole(self):
        return self.scriptConsole

    def isScriptConsoleVisible(self):
        return self.scriptConsolePane.isAuxVisible()

    def updateScriptConsole(self):
        scriptConsole.currentObject = SelectionHandler.activeModel

    class ToggleScriptPane(StandardAction):
        def __init__(self, description, splitPane):
            StandardAction.__init__(description)
            self.splitPane = splitPane

        def action(self):
            self.splitPane.auxVisible = not self.splitPane.isAuxVisible()

    def initFileMenu(self, fileMenu):
        fileMenu.addAction(CreateModelAction("New Network", self, CNetwork()))

        fileMenu.addAction(OpenNeoFileAction(self), KeyEvent.VK_O,
            KeyStroke.getKeyStroke(KeyEvent.VK_O, MENU_SHORTCUT_KEY_MASK))

        fileMenu.jMenu.addSeparator()

        fileMenu.addAction(SaveNetworkAction("Save Selected Network"),
            KeyEvent.VK_S, KeyStroke.getKeyStroke(KeyEvent.VK_S, MENU_SHORTCUT_KEY_MASK))

        fileMenu.addAction(GeneratePDFAction("Save View to PDF"), KeyEvent.VK_P,
            KeyStroke.getKeyStroke(KeyEvent.VK_P, MENU_SHORTCUT_KEY_MASK))

        fileMenu.addAction(GenerateScriptAction("Generate Script"),
            KeyEvent.VK_G, KeyStroke.getKeyStroke(KeyEvent.VK_G, MENU_SHORTCUT_KEY_MASK))

        fileMenu.jMenu.addSeparator()
        fileMenu.addAction(ClearAllAction("Clear all"))
        fileMenu.jMenu.addSeparator()

    def initViewMenu(self, menuBar):
        viewMenu = new MenuBuilder("View")
        viewMenu.jMenu.mnemonic = KeyEvent.VK_V
        menuBar.add(viewMenu.jMenu)

        for count, splitPane in enumerate(splitPanes):
            shortCutChar = splitPane.auxTitle.bytes[0]

            viewMenu.addAction(ToggleScriptPane("Toggle " + splitPane.auxTitle, splitPane),
                    shortCutChar, KeyStroke.getKeyStroke(0x30 + count, MENU_SHORTCUT_KEY_MASK))

        viewMenu.jMenu.addSeparator()

        viewMenu.addAction(ZoomToFitAction("Zoom to fit", self.world,
            KeyEvent.VK_0, KeyStroke.getKeyStroke(KeyEvent.VK_0, MENU_SHORTCUT_KEY_MASK))

    def localToView(self, localPoint):
        return self.nengoWorld.localToView(localPoint)

    def removeNodeModel(self, node):
        modelToDestroy = None
        for wo in self.world.ground.children:
            if isinstance(wo, ModelObject):
                modelObject = wo
                if modelObject.model == node:
                    modelToDestroy = modelObject
                    break
        if modelToDestroy is not None:
            modelToDestroy.destroyModel()
            return True
        else:
            return False

    def setDataViewerPaneVisible(self, visible):
        if dataViewerPane.isAuxVisible() != visible:
            ToggleScriptPane(None, dataViewerPane).doAction()

    def setDataViewerVisible(self, isVisible):
        dataViewerPane.auxVisible = isVisible

    def getConfigPane(self):
        return self.configPane

    def updateConfigurationPane(self):
        if configPane.toJComponent().isAuxVisible():
            configPane.configureObj(SelectionHandler.activeModel)

    def toggleConfigPane(self):
        pane = configPane.toJComponent()
        pane.auxVisible = not pane.isAuxVisible()
        self.updateConfigurationPane()

    class ConfigurationPane(object):
        def __init__(self, mainPanel):
            self.auxSplitPane = AuxillarySplitPane(mainPanel, None, "Inspector",
                AuxillarySplitPane.Orientation.Right)
            self.auxSplitPane.auxPaneWrapper.background = NengoStyle.COLOR_CONFIGURE_BACKGROUND);
            self.currentObj = None

        def configureObj(self, obj):
            if obj == self.currentObj:
                return
            self.currentObj = obj

            location = auxSplitPane.dividerLocation
            configurationPane = ConfigUtil.createConfigurationPane(obj)
            configurationPane.tree.background = NengoStyle.COLOR_CONFIGURE_BACKGROUND

            if obj is None:
                auxSplitPane.auxPane = configurationPane, "Inspector");
            else:
                # Style.applyStyle(configurationPane.tree)
                # Style.applyStyle(configurationPane.cellRenderer)

                if hasattr(obj, 'name'):
                    name = obj.name
                else:
                    name = "Inspector"
                auxSplitPane.setAuxPane(configurationPane,
                    name + " (" + obj.class.simpleName + ")")

            auxSplitPane.dividerLocation = location

        def toJComponent(self):
            return self.auxSplitPane


class RunNetworkAction(StandardAction):
    """Runs the closest network to the currently selected obj."""
    def action(self):
        selectedNode = SelectionHandler.activeObject

        selectedNetwork = UINetwork.getClosestNetwork(selectedNode)
        if selectedNetwork is not None:
            runAction = RunSimulatorAction("run", selectedNetwork)
            runAction.doAction()
        else:
            raise ActionException("No parent network to run, please select a node")

class SaveNetworkAction(StandardAction):
    """Saves the closest network to the currently selected object"""
    def action(self):
        selectedNode = SelectionHandler.activeObject

        selectedNetwork = UINetwork.getClosestNetwork(selectedNode)
        if selectedNetwork is not None:
            saveNodeAction = SaveNodeAction(selectedNetwork)
            saveNodeAction.doAction()
        else:
            raise ActionException("No parent network to save, please select a node")

class GenerateScriptAction(StandardAction):
    """Generates a script for the highest network including the selected object"""
    def action(self):
        selectedNode = SelectionHandler.activeObject

        selectedNetwork = UINetwork.getClosestNetwork(selectedNode)
        if selectedNetwork is not None:
            generatePythonScriptAction = GeneratePythonScriptAction(selectedNetwork)
            generatePythonScriptAction.doAction()
        else:
            raise ActionException("No parent network to save, please select a node")


class ShortcutKey(object):
    def __init__(self, modifiers, keycode, action):
        self.modifiers = modifiers
        self.keycode = keycode
        self.action = action
