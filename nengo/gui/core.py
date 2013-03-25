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

class UserPreferences(Serializable):
    """Serializable object which contains UI preferences of the application"""

    def __init__(self):
        self._enableTooltips = True
        self._gridVisible = True
        self.isWelcomeScreen = True

    def apply(self, applyTo):
        applyTo.enableTooltips = self.enableTooltips
        applyTo.gridVisible = self.gridVisible

    @property
    def enableTooltips(self):
        return self._enableTooltips

    @enableTooltips.setter
    def enableTooltips(self, enable):
        self._enableTooltips = enable
        WorldImpl.tooltipsVisible = self._enableTooltips

    @property
    def gridVisible(self):
        return self._gridVisible
    
    @gridVisible.setter
    def gridVisible(self, visible):
        self._gridVisible = visible
        PXGrid.gridVisible = self._gridVisible