"""
import java.awt.BasicStroke;
import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;
import java.util.ArrayList;

import ca.nengo.ui.lib.Style.NengoStyle;
import ca.nengo.ui.lib.world.Destroyable;
import ca.nengo.ui.lib.world.WorldLayer;
import ca.nengo.ui.lib.world.WorldObject.Listener;
import ca.nengo.ui.lib.world.WorldObject.Property;
import ca.nengo.ui.lib.world.piccolo.WorldObjectImpl;
import ca.nengo.ui.lib.world.piccolo.primitives.Path;
import ca.nengo.ui.lib.world.piccolo.primitives.PiccoloNodeInWorld;
"""

from .world_object import WorldObject 

import math

class ElasticObject(WorldObject):
    DEFAULT_REPULSION_DISTANCE = 150

    def __init__(self, *args, **kwargs):
        WorldObject.__init__(self, *args, **kwargs)

        # Cache the Elastic world for fast access because it is used often
        self.elastic_ground = self.elastic_world = None
        self._anchored = False
        self.repulsion_range = None

        # Counts the number of times the position has been locked
        self.position_lock = 0

        self.addPropertyChangeListener(Property.PARENTS_CHANGED, Listener() {})
#            public void propertyChanged(Property event) {
#                if (getParent() instanceof ElasticGround) {
#                    elasticGround = (ElasticGround) getParent();
#                }
#            }

        self.addPropertyChangeListener(Property.BOUNDS_CHANGED, Listener() {})
#            public void propertyChanged(Property event) {
#                recalculateRepulsionRange();
#            }

        self.recalculateRepulsionRange()

    def recalculateRepulsionRange(self):
        bounds = self.localToGlobal(self.bounds)
        radius = math.sqrt(bounds.width * bounds.width
                           + bounds.height * bounds.height)
        self.repulsion_range = self.DEFAULT_REPULSION_DISTANCE + radius

    @property
    def offset(self):
        if self.elastic_world is not None:
            return self.elastic_world.elastic_position(self)
        else:
            WorldObject.offset(self)

    @property
    def offsetReal(self):
        """This is the real getOffset function.
        
        ??? TWB: What?
        
        """
        return WorldObject.offset(self)

    @property
    def positionLocked(self):
        if self.elastic_ground is not None:
            return self.elastic_ground.positionLocked
        return False

    @positionLocked.setter
    def positionLocked(self, locked):
        if locked:
            self.position_lock += 1
        else:
            self.position_lock = max(0, self.position_lock - 1)

        if self.elastic_ground is not None:
            self.elastic_ground.positionLocked = self.position_lock > 0 

    @property
    def anchored(self):
        return self._anchored

    @anchored.setter
    def anchored(self, anchored):
        if self._anchored == anchored:
            return
        self._anchored = anchored
        if self._anchored:
            if self.anchor is None:
                self.anchor = Anchor(self)
            self.positionLocked = True
        else:
            if self.anchor is not None:
                self.anchor.destroy()
                self.anchor = None
            self.positionLocked = False

    def setOffset(self, x, y):
        """If NetworkViewer exists as a parent, this becomes a redirect
        to NetworkViewer's set location function.

        """
        if self.elastic_world is not None:
            self.elastic_world.setElasticPosition(self, x, y)
        else
            WorldObject.setOffset(self, x, y)

    def setOffsetReal(self, x, y):
        """This is the real setOffset function, apparently.
        
        TWB: What?
        
        """
        WorldObject.setOffset(self, x, y)

    @selected.setter
    def selected(self, selected):
        WorldObject.selected(self, selected)
        self.positionLocked = selected


    def prepareForDestroy(self):
        if self.anchor is not None:
            self.anchor.destroy()
            self.anchor = None
        WorldObject.prepareForDestroy(self)


class Anchor(Listener):
    SIZE_ANCHOR = 15

    def __init__(self, obj):
        Listener.__init__(self)
        self.obj = obj
        ground = obj.worldLayer

        self.border = Path.createRectangle(0, 0, 1, 1)
        self.line = Path()
        # line.setStrokePaint(Style.COLOR)
        self.border.setPpaint(None)
        self.border.stroke = BasicStroke(2.)
        self.border.strokePaint = NengoStyle.COLOR_ANCHOR
        self.line.setPaint(None)
        self.line.stroke = BasicStroke(2.)
        self.line.strokePaint = NengoStyle.COLOR_ANCHOR

        ground.addChild(self.line)
        ground.addChild(self.border)
        self.updateBounds()
        self.obj.addPropertyChangeListener(Property.REMOVED_FROM_WORLD, self)
        self.obj.addPropertyChangeListener(Property.GLOBAL_BOUNDS, self)
        
        self.destroyed = False

    def destroy(self):
        if not self.destroyed:
            self.line.destroy()
            self.border.destroy()
            self.destroyed = True
            self.obj.removePropertyChangeListener(Property.REMOVED_FROM_WORLD, self)
            self.obj.removePropertyChangeListener(Property.GLOBAL_BOUNDS, self)

    def updateBounds(self):
        self.border.moveToFront()
        self.line.moveToFront()

        bounds = obj.localToGlobal(obj.bounds)
        self.border.bounds = bounds

        if bounds.width > 0:
            points = []
            x = bounds.centerX
            y = bounds.maxY
            points.append(Point2D.Double(x, y))
            y += self.SIZE_ANCHOR * (2. / 3.)
            points.append(Point2D.Double(x, y))
            x -= self.SIZE_ANCHOR
            points.append(Point2D.Double(x, y))
            x += self.SIZE_ANCHOR * 2
            points.append(Point2D.Double(x, y))

            self.line.setPathToPolyline(points)

    def propertyChanged(self, event):
        if event == Property.REMOVED_FROM_WORLD:
            self.destroy()
        elif event == Property.GLOBAL_BOUNDS:
            self.updateBounds()
