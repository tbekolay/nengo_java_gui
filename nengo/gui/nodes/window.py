#import java.awt.event.MouseEvent;
#import java.awt.geom.Point2D;
#import java.awt.geom.Rectangle2D;
#import java.lang.ref.WeakReference;
#
#import javax.swing.JPopupMenu;
#
#import ca.nengo.ui.lib.Style.NengoStyle;
#import ca.nengo.ui.lib.util.UIEnvironment;
#import ca.nengo.ui.lib.util.Util;
#import ca.nengo.ui.lib.world.Interactable;
#import ca.nengo.ui.lib.world.WorldObject;
#import ca.nengo.ui.lib.world.handlers.EventConsumer;
#import ca.nengo.ui.lib.world.piccolo.WorldObjectImpl;
#import ca.nengo.ui.lib.world.piccolo.objects.icons.CloseIcon;
#import ca.nengo.ui.lib.world.piccolo.objects.icons.MaximizeIcon;
#import ca.nengo.ui.lib.world.piccolo.objects.icons.MinimizeIcon;
#import ca.nengo.ui.lib.world.piccolo.objects.icons.RestoreIcon;
#import ca.nengo.ui.lib.world.piccolo.primitives.Path;
#import ca.nengo.ui.lib.world.piccolo.primitives.Text;
#import edu.umd.cs.piccolo.event.PBasicInputEventHandler;
#import edu.umd.cs.piccolo.event.PInputEvent;
#import edu.umd.cs.piccolo.event.PInputEventListener;
#import edu.umd.cs.piccolox.nodes.PClip;

import weakref


class WindowPropertyChangeListener(Listener):
    def __init__(self, window):
        Listener.__init__(self)
        self.window = window

    def propertyChanged(self, event):
        if self.window.state == WindowState.MAXIMIZED:
            self.window.maximizeBounds()


class Window(WorldObject):
    """A Window which can be minimized, normal, maximized and closed.

    A Window wraps another world object which contains content displayed
    in the window.

    """

    DEFAULT_HEIGHT = 400
    DEFAULT_WIDTH = 600
    MENU_BAR_HEIGHT = 27
    WINDOW_STATES = ['maximized', 'minimized', 'normal']
    WINDOW_STATE_DEFAULT = 'normal'

    def __init__(self, source, content):
        WorldObject.__init__(self)
        self.sourceRef = weakref.ref(source)
        self.selectable = True
        self.content = content
        self.menubar = MenuBar(self)

        self.clippingRectangle = PClip()
        self.clippingRectangle.addChild(content.piccolo)
        self.clippingRectangle.setPaint(NengoStyle.COLOR_BACKGROUND)
        self.border = Border(self, NengoStyle.COLOR_FOREGROUND)

        self.piccolo.addChild(self.clippingRectangle)
        self.addChild(self.menubar)
        self.addChild(self.border)

        self.windowStateChanged()
        self.content.addInputEventListener(MenuBarHandler())
        self.addInputEventListener(MenuBarHandler())

        self.eventConsumer = None
        self.sourceShadow = None
        self.state = self.WINDOW_STATE_DEFAULT
        self.savedWindowBounds = None
        self.savedWindowOffset = None
        self.savedWindowState = self.WINDOW_STATE_DEFAULT

        self.addPropertyChangeListener(Property.PARENTS_BOUNDS,
                                       WindowPropertyChangeListener(self))

    def maximizeBounds(self):
        self.setOffset(0, 0)
        self.bounds = self.parentToLocal(self.parent.bounds)

    def prepareForDestroy(self):
        self.windowState = WindowState.MINIMIZED
        if self.sourceShadow is not None:
            self.sourceShadow.destroy()
            self.sourceShadow = None

        self.content.destroy()
        WorldObject.prepareForDestroy(self)

    def windowStateChanged(self):
        self.menubar.updateButtons()
        if self.state == MAXIMIZED:
            if self.sourceShadow is not None:
                self.sourceShadow.destroy()
                self.sourceShadow = None

            self.border.visible = False
            nengoinstance.addWorldWindow(self)

            if self.eventConsumer is None:
                self.eventConsumer = EventConsumer()
                self.addInputEventListener(self.eventConsumer)

            self.maximizeBounds()
            self.menubar.highlighted = True

            BoundsHandle.removeBoundsHandlesFrom(self)
        elif self.state == NORMAL:
            source = self.source()
            if source is None:
                raise Exception("Window still active after source destroyed")

            if self.savedWindowBounds is not None:
                self.bounds = self.savedWindowBounds
                self.setOffset(self.savedWindowOffset)
            else:
                self.width = self.DEFAULT_WIDTH
                self.height = self.DEFAULT_HEIGHT
                if source is not None:
                    self.setOffset((self.width - source.width) / -2.0,
                                   source.height + 20)

            if self.eventConsumer is not None:
                self.removeInputEventListener(self.eventConsumer)
                self.eventConsumer = None

            source.addChild(self)
            self.border.visible = True

            BoundsHandle.addBoundsHandlesTo(self)

            if self.sourceShadow is None:
                self.sourceShadow = RectangularEdge(source, self)
                source.addChild(self.sourceShadow, 0)

        elif self.state == MINIMIZED:
            if self.sourceShadow is not None:
                self.sourceShadow.destroy()
                self.sourceShadow = None
            self.removeFromParent()

        if self.state == WindowState.MINIMIZED:
            self.visible = False
            self.childrenPickable = False
            self.pickable = False
        else:
            self.visible = True
            self.childrenPickable = True
            self.pickable = True

            self.layoutChildren()

    def close(self):
        self.destroy()

    def cycleVisibleWindowState(self):
        """Increases the size of the window through state transitions."""
        if self.state == MAXIMIZED:
            self.windowState = WindowState.NORMAL
        elif self.state == NORMAL:
            self.windowState = WindowState.MAXIMIZED
        elif self.state == MINIMIZED:
            self.windowState = WindowState.NORMAL

    @property
    def contextMenu(self):
        if hasattr(self.contents, 'contextMenu'):
            return self.contents.contextMenu
        return None

    @property
    def name(self):
        return self.contents.name

    def layoutChildren(self):
        WorldObject.layoutChildren(self)

        self.menubar.setBounds(0, 0, self.width, self.MENU_BAR_HEIGHT)

        self.contents.setBounds(0, 0, self.width() - 4,
                                self.height - 4 - self.MENU_BAR_HEIGHT)
        self.contents.setOffset(2, 2 + self.MENU_BAR_HEIGHT)

        self.clippingRectangle.setPathToRectangle(self.x, self.y,
                                                  self.width, self.height)

    def moveToFront(self):
        WorldObject.moveToFront(self)
        source = self.source()
        if source is not None:
            source.moveToFront()

    def restoreSavedWindow(self):
        self.windowState = self.savedWindowState

    @windowState.setter
    def windowState(self, state):
        if self.state != state:
            # Saves the window bounds and offset
            if self.state == WindowState.NORMAL:
                self.savedWindowBounds = self.bounds
                self.savedWindowOffset = self.offset

            # Saves the previous window state
            if state == WindowState.MINIMIZED:
                self.savedWindowState = self.state

            self.state = state
            self.windowStateChanged()

    @property
    def maximized(self):
        return self.state == 'maximized'

    @property
    def minimzed(self):
        return self.state == 'minimized'


class MenuBarHandler(PBasicInputEventHandler)
    def __init__(self, menubar):
        PBasicInputEventHandler.__init__(self)
        self.menubar = menubar

    def mouseEntered(self, event):
        self.menubar.highlighted = True

    def mouseExited(self, event):
        self.menubar.highlighted = False


class MenuBar(WorldObject, PInputEventListener):
    BUTTON_SIZE = 26

    def __init__(self, window):
        WorldObject.__init__(self)
        PInputEventListener.__init__(self)
        self.window = window
        self.init()

    def init(self):
        self.addInputEventListener(self)

        self.rectangle = Path.createRectangle(0, 0, 1, 1)
        self.rectangle.setPaint(NengoStyle.COLOR_BACKGROUND2)
        self.addChild(self.rectangle)

        self.title = Text(self.window.name)
        self.title.font = NengoStyle.FONT_LARGE
        self.addChild(self.title)

        self.normalButton = Button(RestoreIcon(self.BUTTON_SIZE),
            make_runnable(lambda: self.window.setWindowState('normal')))
        self.maximizeButton = Button(MaximizeIcon(self.BUTTON_SIZE),
            make_runnable(lambda: self.window.setWindowState('maximized')))
        self.minimizeButton = Button(MinimizeIcon(self.BUTTON_SIZE),
            make_runnable(lambda: self.window.setWindowState('minimized')))
        self.closeButton = Button(CloseIcon(self.BUTTON_SIZE),
            make_runnable(lambda: self.window.close()))

        self.buttonHolder = WorldObject()
        self.addChild(self.buttonHolder)
        self.buttonHolder.addChild(self.maximizeButton)
        self.buttonHolder.addChild(self.normalButton)
        self.buttonHolder.addChild(self.minimizeButton)
        self.buttonHolder.addChild(self.closeButton)

        self.highlighted = False

    def layoutChildren(self):
        WorldObject.layoutChildren(self)
        self.title.setBounds(3, 3, self.width, self.height)

        buttonX = self.width - self.closeButton.width
        self.closeButton.setOffset(buttonX, 0)
        buttonX -= self.closeButton.width()
        self.maximizeButton.setOffset(buttonX, 0)
        self.normalButton.setOffset(buttonX, 0)
        buttonX -= self.minimizeButton.width
        self.minimizeButton.setOffset(buttonX, 0)
        self.rectangle.setBounds(self.bounds)

    def processEvent(self, event, type):
        if type == MouseEvent.MOUSE_CLICKED and event.clickCount == 2:
            self.window.cycleVisibleWindowState()

    @highlighted.setter
    def highlighted(self, highlighted):
        if highlighted or self.window.windowState == 'maximized':
            self.rectangle.transparency = 1
            self.buttonHolder.transparency = 1
            self.title.transparency = 1
        else:
            self.rectangle.transparency = 0.2
            self.buttonHolder.transparency = 0.4
            self.title.transparency = 0.6

    def updateButtons(self):
        if self.window.state == 'maximized':
            self.maximizeButton.removeFromParent()
            self.buttonHolder.addChild(self.normalButton)
        else:
            self.normalButton.removeFromParent()
            self.buttonHolder.addChild(self.maximizeButton)
