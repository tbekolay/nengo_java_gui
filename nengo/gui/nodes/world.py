from java.awt.geom import Point2D, Rectangle2D
# import java.util.Collection;
import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;
import java.security.InvalidParameterException;
import java.util.ArrayList;
import java.util.Collection;

import javax.swing.JPopupMenu;

import ca.nengo.ui.NengoGraphics;
import ca.nengo.ui.actions.PasteAction;
import ca.nengo.ui.lib.Style.NengoStyle;
import ca.nengo.ui.lib.actions.ActionException;
import ca.nengo.ui.lib.actions.RemoveObjectsAction;
import ca.nengo.ui.lib.actions.StandardAction;
import ca.nengo.ui.lib.actions.ZoomToFitAction;
import ca.nengo.ui.lib.util.UIEnvironment;
import ca.nengo.ui.lib.util.menus.PopupMenuBuilder;
import ca.nengo.ui.lib.world.Interactable;
import ca.nengo.ui.lib.world.World;
import ca.nengo.ui.lib.world.WorldObject;
import ca.nengo.ui.lib.world.handlers.AbstractStatusHandler;
import ca.nengo.ui.lib.world.handlers.EventConsumer;
import ca.nengo.ui.lib.world.handlers.KeyboardHandler;
import ca.nengo.ui.lib.world.handlers.MouseHandler;
import ca.nengo.ui.lib.world.handlers.PanEventHandler;
import ca.nengo.ui.lib.world.handlers.SelectionHandler;
import ca.nengo.ui.lib.world.handlers.TooltipPickHandler;
import ca.nengo.ui.lib.world.handlers.TopWorldStatusHandler;
import ca.nengo.ui.lib.world.piccolo.objects.TooltipWrapper;
import ca.nengo.ui.lib.world.piccolo.objects.Window;
import ca.nengo.ui.lib.world.piccolo.primitives.PXGrid;
import ca.nengo.ui.lib.world.piccolo.primitives.PXLayer;
import ca.nengo.ui.models.NodeContainer;
import ca.nengo.ui.util.NengoClipboard;
import edu.umd.cs.piccolo.PRoot;
import edu.umd.cs.piccolo.event.PBasicInputEventHandler;
import edu.umd.cs.piccolo.util.PBounds;

# import ca.nengo.ui.lib.world.handlers.SelectionHandler;

from .world_object import WorldObject


class World(WorldObject):
    """Implementation of World.

    World holds World Objects and has navigation and interaction handlers.

    """

    # Padding to use around objects when zooming in on them
    OBJECT_ZOOM_PADDING = 100

    TOOLTIPS_ENABLED = True


    def __init__(self, name, sky, ground):
        WorldObject.__init__(self, name)

        # If true, then selection mode. If false, then navigation mode.
        self.isSelectionMode = False

        # PLayer which holds the ground layer
        self.layer = PXLayer()
        self.pRoot.addChild(self.layer)

        # Ground which can be zoomed and navigated
        self.ground = ground
        self.ground.world = self
        self.layer.addChild(self.ground.piccolo)

        # Sky, which looks at the ground and whose position and scale
        # remain static
        self.sky = sky
        self.sky.addLayer(self.layer)
        self.addChild(self.sky)

        # Create handlers
        self.panHandler = PanEventHandler()
        self.keyboardHandler = KeyboardHandler(self)
        self.sky.camera.addInputEventListener(self.keyboardHandler)
        self.sky.camera.addInputEventListener(TooltipPickHandler(self, 1000, 0))
        self.sky.camera.addInputEventListener(MouseHandler(self))

        self.selectionEventHandler = SelectionHandler(self, self.panHandler)
        self.selectionEventHandler.marqueePaint = NengoStyle.COLOR_BORDER_SELECTED
        self.selectionEventHandler.marqueeStrokePaint = NengoStyle.COLOR_BORDER_SELECTED
        self.selectionEventHandler.marqueePaintTransparency = 0.1

        self.piccolo.addInputEventListener(EventConsumer())
        self.statusBarHandler = TopWorldStatusHandler(self)

        # self.animateToSkyPosition(0, 0)
        self.sky.viewScale = 0.7

        # Layer attached to the camera which shows the zoomable grid
        self.gridLayer = PXGrid.createGrid(self.sky.camera,
            nengoinstance.universe.root, NengoStyle.COLOR_DARKBORDER, 1500)

        # Let the top canvas have a handle on this world
        nengoinstance.universe.addWorld(self)

        self.setBounds(0, 0, 800, 600)
        self.initSelectionMode()


    def getGround(self):
        pass

    def getSky(self):
        pass

    def skyToGround(self, position):
        pass

    def getSelection(self):
        pass

    def getSelectionHandler(self):
        pass

    def zoomToFit(self):
        pass

    def zoomToObject(self, object):
        pass


    @staticmethod
    def getObjectBounds(objects):
        startX = float('inf')
        startY = float('inf')
        endX = float('-inf')
        endY = float('-inf')

        for wo in objects:
            position = wo.localToGlobal(Point2D.Double(0, 0))
            bounds = wo.localToGlobal(wo.bounds)

            x = position.x
            y = position.y

            if x < startX:
                startX = x
            if x + bounds.width > endX:
                endX = x + bounds.width

            if y < startY:
                startY = y
            if y + bounds.height > endY:
                endY = y + bounds.height

        if len(objects) > 0:
            return Rectangle2D.Double(startX, startY,
                                      endX - startX, endY - startY)
        else:
            raise ValueError("No objects")

    # Just access class variable
    # public static boolean isTooltipsVisible() {
    #    return tooltipsEnabled;
    # }

    # Just access class variable
    # public static void setTooltipsVisible(boolean tooltipsVisible) {
    #    WorldImpl.tooltipsEnabled = tooltipsVisible;
    # }

    @property
    def pRoot(self):
        """This world's root is always to top-level root associated with the
        canvas.

        """
        return nengoinstance.universe.root

    def initSelectionMode(self):
        self.isSelectionMode = False
        self.sky.camera.addInputEventListener(self.panHandler)
        self.sky.camera.addInputEventListener(self.selectionEventHandler)

    def constructMenu(self, menu, posX, posY):
        """Create context menu."""
        clipboard = nengoinstance.clipboard
        if clipboard.hasContents():
            clipboardNames = clipboard.contentsNames
            selectionName = "selection"
            if clipboardNames.size() == 1:
                selectionName = clipboardNames.get(0)

            pasteAction = PasteAction("Paste '" + selectionName + "' here",
                                      self, False)
            pasteAction.setPosition(posX, posY)
            menu.addAction(pasteAction)

        menu.addAction(ZoomToFitAction("Zoom to fit", self))
        # windowsMenu = menu.addSubMenu("Windows")
        # windowsMenu.addAction(CloseAllWindows("Close all"))
        # windowsMenu.addAction(MinimizeAllWindows("Minimize all"))

    def constructSelectionMenu(self, selection, menu):
        menu.addAction(ZoomToFitAction("Zoom to fit", self))
        menu.addAction(RemoveObjectsAction(selection, "Remove selected"))

    def prepareForDestroy(self):
        nengoinstance.universe.removeWorld(self)

        self.keyboardHandler.destroy()
        self.gridLayer.removeFromParent()
        self.layer.removeFromParent()

        self.ground.destroy()
        self.sky.destroy()

        WorldObject.prepareForDestroy(self)

    def animateToSkyPosition(self, x, y):
        """Sets the view position of the sky, and animates to it.

        Positions are relative to the ground.

        """
        newBounds = Rectangle2D.Double(x, y, 0, 0)

        self.sky.animateViewToCenterBounds(newBounds, False, 600)

    def closeAllWindows(self):
        """Closes all windows which exist in this world."""
        for window in self.windows:
            window.close()

    @property
    def windows(self):
        """Returns a collection of all the windows in this world.

        """
        skyWindows = self.sky.windows
        groundWindows = self.ground.windows

        return skyWindows + groundWindows

    def getContextMenu(self, posX=None, posY=None):
        menu = PopupMenuBuilder(self.name)
        self.constructMenu(menu, posX, posY)
        return menu.toJPopupMenu()

    @property
    def selection(self):
        return self.selectionEventHandler.selection

    def getSelectionMenu(self, selection):
        """Context menu for currently selected items.

        None if no context menu is to be shown.

        """

        if len(selection) > 1:
            menu = PopupMenuBuilder(len(selection) + " objects selected")
            self.constructSelectionMenu(selection, menu)
            return menu.toJPopupMenu()
        return None

    def isAncestorOf(self, wo):
        if wo is self:
            return True

        if self.ground.isAncestorOf(wo):
            return True
        else:
            return WorldObject.isAncestorOf(self, wo)

    def minimizeAllWindows(self):
        """ Minimizes all windows that exist in this world."""
        for window in self.windows:
            window.windowState = Window.WindowState.MINIMIZED

    def setBounds(self, x, y, w, h):
        self.sky.setBounds(x, y, w, h)
        return WorldObject.setBounds(self, x, y, w, h)

    @selectionmode.setter
    def selectionMode(self, enabled):
        if self.selectionMode == enabled:
            return

        self.selectionMode = enabled
        self.sky.camera.removeInputEventListener(self.selectionEventHandler)
        self.selectionEventHandler.endSelection(False)

        if self.selectionMode:
            self.sky.camera.removeInputEventListener(self.panHandler)
            self.sky.camera.addInputEventListener(self.selectionEventHandler)
        else:
            self.initSelectionMode()

    @statusBarHandler.setter
    def statusBarHandler(self, handler):
        """Set the status bar handler, there can be only one."""
        if self.statusBarHandler is not None:
            self.sky.camera.removeInputEventListener(self.statusBarHandler)

        self.statusBarHandler = handler

        if self.statusBarHandler is not None:
            self.sky.camera.addInputEventListener(self.statusBarHandler)

    def showTooltip(self, objectSelected):
        tooltip = TooltipWrapper(self.sky, objectSelected.tooltip,
                                 objectSelected)
        tooltip.fadeIn()
        return tooltip

    def skyToGround(self, position):
        self.sky.localToView(position)
        return position

    def zoomToBounds(self, bounds, time=1000):
        """ Animate the sky to look at a portion of the ground at bounds."""
        biggerBounds = PBounds(bounds.x - self.OBJECT_ZOOM_PADDING,
                               bounds.y - self.OBJECT_ZOOM_PADDING,
                               bounds.width + self.OBJECT_ZOOM_PADDING * 2,
                               bounds.height + self.OBJECT_ZOOM_PADDING * 2)

        self.sky.animateViewToCenterBounds(biggerBounds, True, time)

    def zoomToFit(self):
        if len(self.selection) > 0:
            bounds = World.getObjectBounds(self.selection)
            self.zoomToBounds(bounds)
        else:
            self.zoomToBounds(self.ground.piccolo
                              .getUnionOfChildrenBounds(None))

    def zoomToObject(self, object):
        bounds = object.parent.localToGlobal(object.fullBounds)
        self.zoomToBounds(bounds)


    closeAllWindows = make_action("Close all windows", self.closeAllWindows)

    minimizeAllWindows = make_action("Minimize all windows",
                                     self.minimizeAllWindows)

# import ca.nengo.ui.lib.world.piccolo.WorldImpl;
# import ca.nengo.ui.lib.world.piccolo.objects.Window;
# import ca.nengo.ui.lib.world.piccolo.primitives.PXEdge;
# import ca.nengo.ui.lib.world.WorldLayer;
# import ca.nengo.ui.lib.world.WorldObject;
# import ca.nengo.ui.lib.world.piccolo.objects.Window;
# import ca.nengo.ui.lib.world.piccolo.primitives.PiccoloNodeInWorld;

# import ca.nengo.ui.lib.Style.NengoStyle;
# import ca.nengo.ui.lib.world.WorldSky;
# import ca.nengo.ui.lib.world.handlers.KeyboardFocusHandler;
# import ca.nengo.ui.lib.world.handlers.ScrollZoomHandler;
# import ca.nengo.ui.lib.world.piccolo.primitives.PXCamera;
# import ca.nengo.ui.lib.world.piccolo.primitives.PXEdge;
# import edu.umd.cs.piccolo.PCamera;
# import edu.umd.cs.piccolo.PLayer;
# import edu.umd.cs.piccolo.event.PZoomEventHandler;

class WorldLayer(WorldObject):

    def __init__(self, name, node):
        WorldObject.__init__(self, name, node)
        self.world = None

    def addChild(self, child):
        pass

    def addEdge(self, edge):
        pass

    @property
    def windows(self):
        return [wo for wo in self.chidren if isinstance(wo, Window)]

    def clearLayer(self):
        """Removes and destroys children."""
        for wo in self.children:
            wo.destroy()


class WorldSky(WorldLayer):
    """A layer within a world which looks at the ground layer.

    This layer can also contain world objects, but their positions
    are static during panning and zooming.

    """
    MAX_ZOOM_SCALE = 5.0
    MIN_ZOOM_SCALE = 0.05

    def __init__(self):
        WorldLayer.__init__(self, "Sky", PXCamera())
        self.camera = self.piccolo
        self.camera.setPaint(NengoStyle.COLOR_BACKGROUND)

        # Attach handlers
        zoomHandler = PZoomEventHandler()
        zoomHandler.minDragStartDistance = 20
        zoomHandler.minScale = self.MIN_ZOOM_SCALE
        zoomHandler.maxScale = self.MAX_ZOOM_SCALE

        self.camera.addInputEventListener(zoomHandler)
        self.camera.addInputEventListener(KeyboardFocusHandler())
        self.camera.addInputEventListener(ScrollZoomHandler())

        self.world = None

    def animateViewToCenterBounds(self, centerBounds, shouldScaleToFit, duration):
        """Animate the camera's view from its current transform when the activity
        starts to a new transform that centers the given bounds in the camera
        layers coordinate system into the cameras view bounds. If the duration is
        0 then the view will be transformed immediately, and null will be
        returned. Else a new PTransformActivity will get returned that is set to
        animate the camera's view transform to the new bounds. If shouldScale is
        true, then the camera will also scale its view so that the given bounds
        fit fully within the cameras view bounds, else the camera will maintain
        its original scale.

        """
        self.camera.animateViewToCenterBounds(centerBounds, shouldScaleToFit, duration)

    @property
    def viewBounds(self):
        """Return the bounds of this camera in the view coordinate system."""
        return self.camera.viewBounds

    @viewBounds.setter
    def viewBounds(self, centerBounds):
        """Translates and scales the camera's view transform so that the given
        bounds (in camera layer's coordinate system)are centered withing the
        cameras view bounds. Use this method to point the camera at a given
        location.

        """
        self.camera.viewBounds = centerBounds

    @property
    def viewScale(self):
        """Return the scale applied by the view transform to the layers viewed by
        this camera.

        """
        return self.camera.viewScale

    @viewScale.setter
    def viewScale(self, scale):
        """Set the scale of the view transform that is applied to the layers viewed
        by this camera.

        """
        self.camera.viewScale = scale

    def localToView(self, local):
        """Convert the object from the camera's local coordinate system to the
        camera's view coordinate system. The given point is modified by this
        method.

        """
        return self.camera.localToView(local)

    def viewToLocal(self, view):
        """Convert the object from the camera's view coordinate system to the
        camera's local coordinate system. The given point is modified by this.

        """
        return self.camera.viewToLocal(view)

    def addLayer(self, layer):
        self.camera.addLayer(layer)

    def addEdge(self, edge):
        raise NotImplementedError("Not sure how this would work")

#import javax.swing.SwingUtilities;

#import ca.nengo.ui.lib.util.Util;
#import ca.nengo.ui.lib.world.ObjectSet;
#import ca.nengo.ui.lib.world.World;
#import ca.nengo.ui.lib.world.WorldLayer;
#import ca.nengo.ui.lib.world.WorldObject;
#import ca.nengo.ui.lib.world.piccolo.primitives.PXEdge;
#import ca.nengo.ui.lib.world.piccolo.primitives.PXNode;
#import edu.umd.cs.piccolo.PLayer;
#import edu.umd.cs.piccolo.PNode;

class WorldGround(WorldLayer):
    """Layer within a world which is zoomable and pannable.

    It contains world objects.

    """

    def __init__(self):
        WorldLayer.__init__(self, "Ground", GroundNode())
        self.children = None
        self.layerNode = self.piccolo
        self.layerNode.pickable = False

    @staticmethod
    def dropObject(world, parent, wo, centerCameraPosition=True):
        """Adds a little pizzaz when adding new objects."""
        parent.addChild(wo)

        Point2D finalPosition;
        if centerCameraPosition:
            fullBounds = wo.fullBounds

            finalPosition = world.skyToGround(Point2D.Double(world.width / 2,
                                                             world.height / 2))

            # The final position is at the center of the full bounds of the
            # object to be added.
            finalPosition = Point2D.Double(
                finalPosition.x - (fullBounds.x - wo.offset.x)
                 - (fullBounds.width / 2.0),
                finalPosition.y - (fullBounds.y - wo.offset.y)
                 - (fullBounds.height / 2.0))
        else:
            finalPosition = wo.offset

        wo.scale = 1.0 / world.sky.viewScale
        wo.setOffset(finalPosition.x,
                     finalPosition.y - (100.0 / world.sky.viewScale))
        wo.animateToPositionScaleRotation(finalPosition.x, finalPosition.y,
                                          1, 0, 500)

    def prepareForDestroy(self):
        self.layerNode.removeFromParent()
        WorldLayer.prepareForDestroy(self)

    def addEdge(self, edge):
        self.layerNode.addEdge(edge)

    def addChildFancy(self, wo, centerCameraPosition=True):
        """Adds a child object. Like addChild, but with more pizzaz."""
        self.dropObject(self.world, self, wo, centerCameraPosition)

    def childAdded(self, wo):
        WorldLayer.childAdded(wo)
        self.children.append(wo)

    def childRemoved(self, wo):
        WorldLayer.childRemoved(wo)
        self.children.remove(wo)

    def containsEdge(self, edge):
        return self.layerNode.containsEdge(edge)

    @property
    def edges(self):
        return self.layerNode.edges

    @property
    def groundScale(self):
        return self.world.sky.viewScale

    def localToParent(self, local):
        return self.piccolo.localToParent(local)

    #public static interface ChildFilter {
    #    public boolean acceptChild(WorldObject obj);
    #}


class GroundNode(PXNode):
    def __init__(self):
        PXNode.__init__(self)
        self.edgeHolder = PNode()

    def addEdge(self, edge):
        self.edgeHolder.addChild(edge)

    def containsEdge(self, edge):
        return edge.parent == self.edgeHolder:

    @property
    def edges(self):
        return edgeHolder.children

    @parent.setter
    def parent(self, newParent):
        if newParent is not None and not isinstance(newParent, PLayer):
            raise TypeError
        PXNode.setParent(self, newParent)

        # Invoke later, otherwise the edge holder may be added below the
        # ground. We can't add directly here because this function is called
        # from also addChild
        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                if (getParent() != null) {
                    getParent().addChild(0, edgeHolder);
                }
            }
        })

#import java.awt.Dimension;
#import java.lang.reflect.Constructor;
#import java.lang.reflect.InvocationTargetException;

#import javax.swing.SwingUtilities;

#import ca.nengo.ui.configurable.ConfigException;
#import ca.nengo.ui.configurable.ConfigResult;
#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.descriptors.PInt;
#import ca.nengo.ui.configurable.managers.ConfigManager;
#import ca.nengo.ui.configurable.managers.ConfigManager.ConfigMode;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.LayoutAction;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.objects.activities.TrackedAction;
#import ca.nengo.ui.lib.util.UIEnvironment;
#import ca.nengo.ui.lib.util.menus.PopupMenuBuilder;
#import ca.nengo.ui.lib.world.piccolo.WorldImpl;
#import ca.nengo.ui.lib.world.piccolo.WorldSkyImpl;
#import edu.uci.ics.jung.graph.Graph;
#import edu.uci.ics.jung.visualization.Layout;

class ElasticWorld(World):
    """A World which supports Spring layout.

    Objects within this world attract and repel each other.

    """

    DEFAULT_LAYOUT_BOUNDS = Dimension(1000, 1000)

    def __init__(self, name, sky=None, ground=None):
        self.layoutBounds = self.DEFAULT_LAYOUT_BOUNDS
        self.name = name
        self.sky = sky
        if sky is None:
            self.sky = WorldSky()
        self.ground = ground
        if ground is None:
            self.ground = ElasticGround()
        World.__init__(self, self.name, self.sky, self.ground)

    def applyJungLayout(self, layoutType):
        DoJungLayout(self, layoutType).doAction()

#    def constructLayoutMenu(self, menu):
#        menu.addSection("Elastic layout");
#        if (!getGround().isElasticMode()) {
#            menu.addAction(new SetElasticLayoutAction("Enable", true));
#        } else {
#            menu.addAction(new SetElasticLayoutAction("Disable", false));
#        }

#        menu.addSection("Apply layout");

#        MenuBuilder algorithmLayoutMenu = menu.addSubMenu("Algorithm");

#        algorithmLayoutMenu.addAction(new JungLayoutAction(FeedForwardLayout.class, "Feed-Forward"));
#        algorithmLayoutMenu.addAction(new JungLayoutAction(StretchedFeedForwardLayout.class, "Streched Feed-Forward"));
#        algorithmLayoutMenu.addAction(new JungLayoutAction(CircleLayout.class, "Circle"));
#        algorithmLayoutMenu.addAction(new JungLayoutAction(ISOMLayout.class, "ISOM"));

#        MenuBuilder layoutSettings = algorithmLayoutMenu.addSubMenu("Settings");
#        layoutSettings.addAction(new SetLayoutBoundsAction("Set preferred bounds", this));

#    }

    def doFeedForwardLayout(self):
        JungLayoutAction(self, FeedForwardLayout.class, "Feed-Forward").doAction()

#    def constructMenu(self, menu, posX, posY):
#        super.constructMenu(menu, posX, posY);
#        //constructLayoutMenu(menu.addSubMenu("Layout"));
#    }

#    protected void constructMenu(PopupMenuBuilder menu) {
#        super.constructMenu(menu, 0.0, 0.0);
#    }

#    protected Dimension getLayoutBounds() {
#        return layoutBounds;
#    }

#    @Override
#    public ElasticGround getGround() {
#        return (ElasticGround) super.getGround();
#    }

#    public void setLayoutBounds(Dimension bounds) {
#        this.layoutBounds = bounds;
#    }


#import java.awt.geom.Point2D;

#import ca.nengo.model.Network;
#import ca.nengo.model.Node;
#import ca.nengo.ui.lib.world.WorldObject;
#import ca.nengo.ui.lib.world.elastic.ElasticWorld;
#import ca.nengo.ui.models.NodeContainer;
#import ca.nengo.ui.models.UINeoNode;

class NengoWorld(ElasticWorld, NodeContainer):
#    protected void constructMenu(PopupMenuBuilder menu) {

#        super.constructMenu(menu);

#        // Add models section
#        menu.addSection("Add model");

#        // Create network action
#        menu.addAction(new CreateModelAction("New Network", this, new CNetwork()));

    def addNodeModel(self, node, posX=None, posY=None):
        if not isinstance(node, Network):
            raise ContainerException("Only Networks are allowed to be added to the top-level Window")

        nodeUI = UINeoNode.createNodeUI(node)

        if posX is not None and posY is not None:
            nodeUI.setOffset(posX, posY)
            self.ground.addChild(nodeUI)
        else:
            self.ground.addChildFancy(nodeUI)

        return nodeUI

    def getNodeModel(self, name):
        for nodeUI in self.ground.children:
            if isinstance(nodeUI, UINeoNode):
                if nodeUI.name == name:
                    return nodeUI.model
        return None

    def localToView(self, local):
        local = self.sky.parentToLocal(local)
        local = self.sky.localToView(local)
        return local

