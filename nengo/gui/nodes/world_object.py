from edu.umd.cs.piccolo.activities import PInterpolatingActivity

"""
import java.awt.Paint;
import java.awt.geom.Dimension2D;
import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.security.InvalidParameterException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Enumeration;
import java.util.HashSet;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;

import ca.nengo.ui.lib.objects.activities.TransientMessage;
import ca.nengo.ui.lib.util.Util;
import ca.nengo.ui.lib.world.Destroyable;
import ca.nengo.ui.lib.world.PaintContext;
import ca.nengo.ui.lib.world.WorldLayer;
import ca.nengo.ui.lib.world.WorldObject;
import ca.nengo.ui.lib.world.WorldObject.Listener;
import ca.nengo.ui.lib.world.piccolo.primitives.PXNode;
import ca.nengo.ui.lib.world.piccolo.primitives.PiccoloNodeInWorld;
import edu.umd.cs.piccolo.PCamera;
import edu.umd.cs.piccolo.PNode;
import edu.umd.cs.piccolo.activities.PInterpolatingActivity;
import edu.umd.cs.piccolo.event.PInputEventListener;
import edu.umd.cs.piccolo.util.PBounds;
"""


class WorldObject(object):
    """World objects are visible UI objects which exist in a World layer
    (Ground or Sky).

    """
    WORLD_EVT_TO_PICCOLO_EVT = {
        Property.PARENTS_CHANGED: PNode.PROPERTY_PARENT,
        Property.BOUNDS_CHANGED: PNode.PROPERTY_BOUNDS,
        Property.PARENTS_BOUNDS: PXNode.PROPERTY_PARENT_BOUNDS,
        Property.FULL_BOUNDS: PXNode.PROPERTY_FULL_BOUNDS,
        Property.GLOBAL_BOUNDS: PXNode.PROPERTY_GLOBAL_BOUNDS,
        Property.VIEW_TRANSFORM: PCamera.PROPERTY_VIEW_TRANSFORM,
        Property.REMOVED_FROM_WORLD: PXNode.PROPERTY_REMOVED_FROM_WORLD,
        Property.CHILDREN_CHANGED: PNode.PROPERTY_CHILDREN,
    }
    # {v:k for k, v in map.items()} Python 2.7 +
    PICCOLO_EVT_TO_WORLD_EVT = dict((v, k) for k, v in
                                    WORLD_EVT_TO_PICCOLO_EVT.iteritems())

    TIME_BETWEEN_POPUPS = 1500

    @staticmethod
    def piccoloEventToWorldEvent(property_name):
        return WorldObject.PICCOLO_EVT_TO_WORLD_EVT[property_name]

    @staticmethod
    def worldEventToPiccoloEvent(property_type):
        return WorldObject.WORLD_EVT_TO_PICCOLO_EVT[property_type]

    def __init__(self, name="", pnode=None):
        self.draggable = True
        self.childListeners = set()
        self.eventListenerMap = {}
        self.destroyed = False
        self.selected = False
        self.lastPopupTime = 0

        if pnode is None:
            self.pnode = PXNode()
        else:
            self.pnode = pnode

        if not isinstance(self.pnode, PNode):
            raise TypeError("Must be PNode")

        self.pnode.worldObject = self
        # self.init(self.name)
        ## Was init
        self.selectable = False
        self.name = name
        ## Was init

    def addActivity(self, activity):
        self.pnode.addActivity(activity)

    public void addChildrenListener(ChildListener listener) {
        if (childListeners.contains(listener)) {
            throw new InvalidParameterException();
        }
        childListeners.add(listener);
    }
    def addChild(self, wo, index=-1):
        if not isinstance(wo, WorldObject):
            raise TypeError, "Invalid child object."
        if index == -1:
            self.pnode.addChild(wo.pnode)
        else:
            self.pnode.addChild(index, wo.pnode)

    def addChildListener(self, listener):
        if self.childListeners.contains(listener):
            raise ValueError, "Already exists"
        self.childListeners.add(listener)

    def addInputEventListener(self, listener):
        self.pnode.addInputEventListener(listener)

    def addPropertyChangeListener(self, event, listener):
        eventlisteners = self.eventListenerMap.get(event, None)
        if eventlisteners is None:
            eventlisteners = {}
            self.eventListenerMap[event] = eventlisteners

        eventlisteners[self.listener, ListenerAdapter(event, listener)]

        # If there is an associated piccolo event, add the listener to the
        # piccolo object as well

        """
        if piccoloPropertyName is not None:
            piccoloListenerSet = piccoloListeners.get(piccoloPropertyName)
            if piccoloListenerSet is None:
                piccoloListenerSet = set()
            piccoloListener = piccoloListenerSet.get(listener)
            if piccoloListener is None:
                piccoloListener = PiccoloChangeListener(listener)
                piccoloListeners[listener] = piccoloListener
            self.pnode.addPropertyChangeListener(self.worldEventToPiccoloEvent(eventType), piccoloListener)
        """

    def animateToBounds(self, x, y, width, height, duration):
        """Animate this node's bounds from their current location when the
        activity starts to the specified bounds.

        If this node descends from the root then the activity will be
        scheduled, else the returned activity should be scheduled manually.
        If two different transform activities are scheduled for the same node
        at the same time, they will both be applied to the node, but
        the last one scheduled will be applied last on each frame,
        so it will appear to have replaced the original.
        Generally you will not want to do that. Note this method
        animates the node's bounds, but does not change the node's transform.
        Use animateTransformToBounds() to animate the node's transform instead.

        """
        self.pnode.animateToBounds(x, y, width, height, duration)

    def animateToPosition(self, x, y, duration):
        self.pnode.animateToPositionScaleRotation(x, y, self.pnode.scale,
                                                  self.pnode.rotation, duration)

    def animateToPositionScaleRotation(self, x, y, scale, theta, duration):
        """Animate this node's transform from its current location when
        the activity starts to the specified location, scale, and rotation.

        If this node descends from the root then the activity will be
        scheduled, else the returned activity should be scheduled manually.
        If two different transform activities are scheduled for
        the same node at the same time, they will both be applied to the node,
        but the last one scheduled will be applied last on each frame,
        so it will appear to have replaced the original.
        Generally you will not want to do that.

        """
        self.pnode.animateToPositionScaleRotation(x, y, scale, theta, duration)

    def animateToScale(self, scale, duration):
        self.pnode.animateToPositionScaleRotation(self.pnode.offset.x,
            self.pnode.offset.y, scale, self.pnode.rotation, duration)

    def animateToTransparency(self, transparency, duration):
        self.pnode.animateToTransparency(transparency, duration);

    def childAdded(self, wo):
        for listener in self.childListeners:
            listener.childAdded(wo)

    def childRemoved(self, wo):
        for listener in self.childListeners:
            listener.childRemoved(wo)

    def destroy(self):
        if self.destroyed:
            return
        self.prepareForDestroy()
        self.destroyChildren()
        if isinstance(self.pnode, PXNode):
            self.pnode.removeFromWorld()
        self.destroyed = True

    def destroyChildren(self):
        # Copy to list to avoid concurrency error
        objects = [wo for wo in self.children]
        for wo in objects:
            wo.destroy()

    def doubleClicked(self):
        """Called if this object is double clicked on."""
        pass

    def altClicked(self):
        """Called if this object is clicked on with the 'alt' key held."""
        pass

    def dragOffset(self, dx, dy):
        """Offset this node relative to the parents coordinate system,
        and is NOT affected by this node's current scale or rotation.

        This is implemented by directly adding dx to the m02 position
        and dy to the m12 position in the affine transform.

        """
        if not self.draggable:
            return
        self.offset.setLocation(self.offset.x + dx, self.offset.y + dy)

    def firePropertyChange(self, event):
        eventListeners = self.eventListenerMap.get(event, None)
        if eventListeners is not None:
            for listener in eventListeners.keys():
                listener.propertyChanged(event)

    def findIntersectingNodes(self, full_bounds):
        intersectingNodes = []
        self.pnode.findIntersectingNodes(full_bounds, intersectingNodes)
        intersectingObjects = []

        for node in intersectingNodes:
            if isinstance(node, PiccoloNodeInWorld and node.visible):
                intersectingObjects.append(node.worldObject)

        return interesectingObjects

    @property
    def bounds(self):
        """Return a copy of this node's bounds.

        These bounds are stored in the local coordinate system of this node
        and do not include the bounds of any of this node's children.

        """
        return self.pnode.bounds

    @property
    def children(self):
        """Return the list used to manage this node's children.
        This list should not be modified.

        """
        return self._getChildren()

    def _getChildren(self):
        objects = []
        for child in self.pnode.children:
            if isinstance(child, PiccoloNodeInWorld):
                wo = child.worldObject
                if wo is not None:
                    objects.append(wo)
        return objects

    @property
    def childrenCount(self):
        """Schedule the given activity with the root.

        Note that only scheduled activities will be stepped.
        If the activity is successfully added true is returned, else false.

        """
        return self._getChildren.size();

    @property
    def fullBounds(self):
        """Return a copy of this node's full bounds.

        These bounds are stored in the parent coordinate system of this node
        and they include the union of this node's bounds
        and all the bounds of its descendents.

        """
        return self.pnode.fullBounds

    @property
    def height(self):
        return self.pnode.height

    @property
    def offset(self):
        """Return the offset that is being applied
        to this node by its transform.

        This offset effects this node and all of its descendents
        and is specified in the parent coordinate system.
        This returns the values that are in the m02 and m12 positions
        in the affine transform.

        """
        return self.pnode.offset

    @property
    def parent(self):
        parent = self.pnode.parent
        if parent is None:
            return
        return parent.worldObject

    @property
    def rotation(self):
        """Returns the rotation applied by this node's transform, in radians.

        This rotation affects this node and all its descendents.
        The value returned will be between 0 and 2pi radians.

        """
        return self.pnode.rotation

    @property
    def scale(self):
        """Return the scale applied by this node's transform.

        The scale is effecting this node and all its descendents.

        """
        return self.pnode.scale

    @property
    def tooltip(self):
        return None

    @property
    def transparency(self):
        """Return the transparency used when painting this node.

        Note that this transparency is also applied
        to all of the node's descendents.

        """
        return self.pnode.transparency

    @property
    def visible(self):
        """Return true if this node is visible;
        i.e., will it paint itself and descendents.

        """
        return self.pnode.visible

    @property
    def width(self):
        return self.pnode.width

    @property
    def world(self):
        if self.worldLayer is None:
            return None
        return self.worldLayer.world

    @property
    def worldLayer(self):
        node = self.pnode

        while node is not None:
            wo = node.worldObject
            if isinstance(wo, WorldLayer):
                return wo
            node = node.parent
        return None

    @property
    def x(self):
        """Return the x position (in local coords) of this node's bounds."""
        return self.pnode.x

    @property
    def y(self):
        """Return the y position (in local coords) of this node's bounds."""
        return self.pnode.y

    def globalToLocal(self, global_obj):
        """Transform the given object from global coordinates
        to this node's local coordinate system.

        Note that this will modify the dimension parameter.

        """
        return self.pnode.globalToLocal(global_obj)
#        if isinstance(globalThing, Dimension2D):
#            pass
#        elif isinstance(globalThing, Point2D):
#            pass
#        elif isinstance(globalThing, Rectangle2D):
#            pass

    def isAncestorOf(self, wo):
        return self.pnode.isAncestorOf(wo.pnode)

    def isAnimating(self):
        if isinstance(self.pnode, PiccoloNodeInWorld):
            return self.pnode.isAnimating()
        return False

    def layoutChildren(self):
        """Nodes that apply layout constraints to their children
        should override this method and do the layout there.

        """
        pass

    def localToGlobal(self, local_obj):
        """Transform the given object from this node's local coordinate system
        to the global coordinate system.

        Note that this will modify the point parameter.

        """
        self.pnode.localToGlobal(local_obj)
#        if isinstance(localThing, Point2D):
#            pass
#        elif isinstance(localThing, Rectangle2D):
#            pass

    def localToParent(self, local_obj):
        """Transform the given object from this node's local coordinate system
        to its parent's local coordinate system.

        Note that this will modify the point parameter.

        """
        self.pnode.localToParent(local_obj)
#        if isinstance(localThing, Point2D):
#            pass
#        elif isinstance(localThing, Rectangle2D):
#            pass
#        elif isinstance(localThing, Dimension2D):
#            pass

    def moveToBack(self):
        """Change the order of this node in its parent's children list
        so that it will draw in back of all of its other sibling nodes.

        """
        self.pnode.moveToBack()

    def moveToFront(self):
        """Change the order of this node in its parent's children list
        so that it will draw after the given sibling node.

        """
        self.pnode.moveToFront()

    def objectToGround(self, obj):
        layer = self.worldLayer
        self.pnode.localToGlobal(obj)

        if isinstance(layer, WorldSky):
            layer.world.sky.localToView(obj)
            return obj
        elif isinstance(layer, WorldGround):
            return obj
        
        return None
#        if isinstance(obj, Point2D):
#            pass
#        elif isinstance(obj, Rectangle2D):
#            pass

    def objectToSky(self, obj):
        layer = self.worldLayer

        if layer is None:
            return obj

        self.pnode.localToGlobal(obj)

        if isinstance(layer, WorldGround):
            layer.world.sky.viewToLocal(obj)
            return obj
        elif isinstance(layer, WorldSky):
            return obj

        raise TypeError
#        if isinstance(obj, Point2D):
#            pass
#        elif isinstance(obj, Rectangle2D):
#            pass

    def paint(self, context):
        """Paint this node behind any of its children nodes.

        Subclasses that define a different appearance should override
        this method and paint themselves there.

        """
        pass

    def parentToLocal(self, parent_obj):
        """Transform the given point from this node's parent's
        local coordinate system to the local coordinate system of this node.

        Note that this will modify the point parameter.

        """
        return self.pnode.parentToLocal(parent_obj)
#        if isinstance(parent_obj, Point2D):
#            pass
#        elif isinstance(parent_obj, Rectangle2D):
#            pass

    def prepareForDestroy(self):
        """Perform any operations before being destroyed."""
        pass

    def removeChild(self, wo):
        if not isinstance(wo, WorldObject):
            raise TypeError("Invalid child object")
        self.pnode.removeChild(wo.pnode)

    def removeChildrenListener(self, listener):
        if not listener in self.childListeners:
            raise ValueError
        self.childListeners.remove(listener)

    def removeFromParent(self):
        """Delete this node by removing it from its parent's list of children."""
        self.pnode.removeFromParent()

    def removeFromWorld(self):
        """This function must be called before the object is removed
        from the world, or placed in a new one.

        """
        if isinstance(self.pnode, PXNode):
            self.pnode.removeFromWorld()

    def removeInputEventListener(self, listener):
        self.pnode.removeInputEventListener(listener)

    def removePropertyChangeListener(self, event, listener):
        successfull = False
        eventlisteners = self.eventListenerMap.get(event, None)
        if eventlisteners is not None:
            if listener in eventlisteners:
                adapter = eventlisteners[listener]
                adapter.destroy()
                del eventlisteners[listener]
                successful = True
        
        if not successful:
            raise ValueError("Listener is not attached")

    def repaint(self):
        """Mark the area on the screen represented by this nodes full bounds as
        needing a repaint.

        """
        self.pnode.repaint()

    def setBounds(self, *args):
        """Set the bounds of this node to the given value.

        These bounds are stored in the local coordinate system of this node.
        If the width or height is less then or equal to zero then the bound's
        empty bit will be set to

        Subclasses must call the super.setBounds() method.

        """
        if len(args) != 1 and len(args) != 4:
            raise ValueError("1 or 4 args")
        self.pnode.setBounds(*args)

    @childrenPickable.setter
    def childrenPickable(self, pickable):
        """Set the children pickable flag.

        If this flag is false then this node will not try to pick its children.
        Children are pickable by default.

        """
        self.pnode.childrenPickable = pickable

    @height.setter
    def height(self, height):
        return self.pnode.height = height

    def setOffset(self, *args):
        """Set the offset that is being applied to this node by its transform.

        This offset effects this node and all of its descendents
        and is specified in the nodes parent coordinate system.
        This directly sets the values of the m02 and m12 positions
        in the affine transform. Unlike "PNode.translate()",
        it is not effected by the transforms scale.

        """
        if len(args) != 1 and len(args) != 2:
            raise ValueError("1 or 2 args")
        self.pnode.setOffset(*args)

    @paint.setter
    def paint(self, paint):
        """Set the paint used to paint this node. This value may be set to null."""
        self.pnode.setPaint(paint)


    @pickable.setter
    def pickable(self, pickable):
        """Set the pickable flag for this node.

        Only pickable nodes can receive input events.
        Nodes are pickable by default.

        """
        self.pnode.pickable = pickable

    @rotation.setter
    def rotation(self, theta):
        """Sets the rotation of this node's transform in radians.

        This will affect this node and all its descendents.

        """
        self.pnode.rotation = theta

    @scale.setter
    def scale(self, scale):
        """Set the scale of this node's transform.

        The scale will affect this node and all its descendents.

        """
        self.pnode.scale = scale

    @transparency.setter
    def transparency(self, transparency):
        """Set the transparency used to paint this node.

        Note that this transparency applies to this node
        and all of its descendents.

        """
        self.pnode.transparency = transparency

    @visible.setter
    def visible(self, visible):
        self.pnode.visible = visible

    @width.setter
    def width(self, width):
        self.pnode.width = width

    def showPopupMessage(self, msg):
        """Show a transient message which appears over the object.

        The message is added to the world's sky layer.

        """
        if self.world is None:
            return

        messages.debugMsg("UI Popup Msg: " + msg)
        msgObject = TransientMessage(msg)

        offsetX = -(msgObject.width - self.pnode.width) / 2.

        position = self.objectToSky(offsetX, -5)
        msgObject.offset = position
        self.world.sky.addChild(msgObject)
        
        currentTime = System.currentTimeMillis()
        delay = max(0, self.TIME_BETWEEN_POPUPS - currentTime - self.lastPopupTime)
        msgObject.popup(delay)
        self.lastPopupTime = currentTime + delay

    def toString(self):
        return self.name

    def translate(self, dx, dy):
        """Translate this node's transform by the given amount,
        using the standard affine transform translate method.

        This translation effects this node and all of its descendents.

        """
        self.pnode.translate(dx, dy)


""" ???
public interface ChildListener {
    public void childAdded(WorldObject wo);
    public void childRemoved(WorldObject wo);
}

public interface Listener {
    public void propertyChanged(Property event);
}

public enum Property {
    BOUNDS_CHANGED, CHILDREN_CHANGED, FULL_BOUNDS, GLOBAL_BOUNDS, MODEL_CHANGED,
    PARENTS_BOUNDS, PARENTS_CHANGED, REMOVED_FROM_WORLD, VIEW_TRANSFORM, WIDGET
}
"""

class ListenerAdapter(object):
    def __init__(self, event_type, listener, pnode):
        self.event_type = event_type
        self.listener = listener
        self.pnode = pnode
        self.piccolo_listener = None

        piccolo_pname = WorldObject.worldEventToPiccoloEvent(self.event_type)
        if piccolo_pname is not None:
            self.piccolo_listener = PiccoloChangeListener(listener)
            self.pnode.addPropertyChangeListener(
                WorldObject.worldEventToPiccoloEvent(self.event_type),
                self.piccolo_listener)

    def destroy(self):
        if self.piccolo_listener is not None:
            self.pnode.removePropertyChangeListener(
                WorldObject.worldEventToPiccoloEvent(self.event_type),
                self.piccolo_listener)


class PiccoloChangeListener(PropertyChangeListener):
    """Adapater for WorldObjectChange listener to PropertyChangeListener"""
    def __init__(self, listener):
        self.listener = listener

    def propertyChanged(self, event):
        self.listener.propertyChanged(WorldObject.piccoloEventToWorldEvent(event.propertyName))
