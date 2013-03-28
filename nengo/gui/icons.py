from java.awt import BasicStroke
from java.awt.geom import GeneralPath
from .style import NengoStyle
# import ca.nengo.ui.lib.world.piccolo.WorldObjectImpl;

import math

class BaseIcon(WorldObject):
    def __init__(self, size, style=NengoStyle()):
        self.size = size
        self.style = style
        self.setBounds(0, 0, self.size, self.size)

    def paint(self, context):
        WorldObject.paint(context)
        g2 = context.graphics
        g2.color = self.style.COLOR_FOREGROUND
        g2.stroke = BasicStroke(BaseLayoutIcon.STROKE_WIDTH,
                                BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND)
        self.paintIcon(g2)

    def paintIcon(self, g2):
        raise NotImplementedError


class BaseLayoutIcon(BaseIcon):
    STROKE_WIDTH = 2
    PADDING = 5


class BaseWindowIcon(BaseIcon):
    STROKE_WIDTH = 3
    PADDING = 6


class ArrowIcon(BaseLayoutIcon):
    def paintIcon(self, g2):
        rectangleSize = self.size - self.PADDING * 2.0
        path = GeneralPath()
        path.moveTo(self.PADDING, rectangleSize / 2.0 + self.PADDING)
        path.lineTo(rectangleSize + self.PADDING, rectangleSize / 2.0 + self.PADDING)

        # up tick
        path.lineTo(rectangleSize / 1.5 + self.PADDING, self.PADDING * 2)

        # down tick
        path.moveTo(rectangleSize + self.PADDING, rectangleSize / 2.0 + self.PADDING)
        path.lineTo(rectangleSize / 1.5 + self.PADDING, rectangleSize)
        g2.draw(path)


class CloseIcon(BaseWindowIcon):
    def paintIcon(self, g2):
        rectangleSize = self.size - self.PADDING
        path = GeneralPath()
        path.moveTo(self.PADDING, self.PADDING)
        path.lineTo(rectangleSize, rectangleSize)
        path.moveTo(self.PADDING, rectangleSize)
        path.lineTo(rectangleSize, self.PADDING)
        g2.draw(path)


class LoadIcon(BaseLayoutIcon):
    def paintIcon(self, g2):
        rectangleSize = self.size - self.PADDING * 2

        # Line
        g2.drawLine(self.PADDING, rectangleSize + self.PADDING,
            rectangleSize + self.PADDING, rectangleSize + self.PADDING)

        # Arrow
        path = GeneralPath()
        path.moveTo(rectangleSize / 2.0 + self.PADDING, rectangleSize)
        path.lineTo(rectangleSize / 2.0 + self.PADDING, self.PADDING)

        # left tick
        path.lineTo(self.PADDING * 2, (self.size / 2.0) - 1)

        # right tick
        path.moveTo(rectangleSize / 2.0 + self.PADDING, self.PADDING)
        path.lineTo(rectangleSize, (self.size / 2.0) - 1)
        g2.draw(path)


class MaximizeIcon(BaseWindowIcon):
    def paintIcon(self, g2):
        rectangleSize = self.size - self.PADDING * 2
        g2.drawRect(self.PADDING, self.PADDING, rectangleSize, rectangleSize)


class MinimizeIcon(BaseWindowIcon):
    def paintIcon(self, g2):
        yPosition = self.size - self.PADDING - 1
        g2.drawLine(self.PADDING, yPosition, self.size - self.PADDING, yPosition)


class RestoreIcon(BaseWindowIcon):
    def paintIcon(self, g2):
        rectangleSize = self.size - self.PADDING * 2
        g2.drawRect(self.PADDING, self.PADDING + rectangleSize / 2 - 1,
                    rectangleSize, rectangleSize / 2 + 1)


class SaveIcon(BaseLayoutIcon):
    def paintIcon(self, g2):
        rectangleSize = self.size - self.PADDING * 2

        # Line
        g2.drawLine(self.PADDING, rectangleSize + self.PADDING,
            rectangleSize + self.PADDING, rectangleSize + self.PADDING)

        # Arrow
        path = GeneralPath()
        path.moveTo(rectangleSize / 2.0 + self.PADDING, self.PADDING)
        path.lineTo(rectangleSize / 2.0 + self.PADDING, rectangleSize)

        # left tick
        path.lineTo(self.PADDING * 2, (self.size / 2.0) - 1)

        # right tick
        path.moveTo(rectangleSize / 2.0 + self.PADDING, rectangleSize)
        path.lineTo(rectangleSize, (self.size / 2.0) - 1)
        g2.draw(path)


class ZoomIcon(BaseLayoutIcon):
    def paintIcon(self, g2):
        rectangleSize = self.size - self.PADDING * 2
        ticklen = rectangleSize * 0.3

        g2.drawRect(self.PADDING, self.PADDING, rectangleSize, rectangleSize)

        # Double sided diagonal arrow
        arrowpad = self.PADDING + self.STROKE_WIDTH + 1
        rectangleSize = self.size - arrowpad * 2
        path = GeneralPath()

        # ticks
        path.moveTo(arrowpad, rectangleSize + arrowpad)
        path.lineTo(arrowpad, rectangleSize + arrowpad - ticklen)
        path.moveTo(arrowpad, rectangleSize + arrowpad)
        path.lineTo(arrowpad + ticklen, rectangleSize + arrowpad)

        # line
        path.moveTo(arrowpad, rectangleSize + arrowpad)
        path.lineTo(rectangleSize + arrowpad, arrowpad)

        # ticks
        path.lineTo(rectangleSize + arrowpad, arrowpad + ticklen)
        path.moveTo(rectangleSize + arrowpad, arrowpad)
        path.lineTo(rectangleSize + arrowpad - ticklen, arrowpad)
        g2.draw(path)


class ModelIcon(WorldObject, Listener):
    """An Icon which has a representation and a label.

    It is used to represent Nengo models.

    """

    def __init__(self, model, icon):
        # The inner icon node which contains the actual icon representation
        self._icon = icon


        # Parent of this icon (ModelObject)
        self.model = model

        # Whether to show the type of model in the label
        self.show_type = False

        self.addChild(self._icon)
        # Label of the icon
        self.label = Text()
        self.label.constrainWidthToTextWidth = True
        self.updateLable()
        self.addChild(self.label)
        self.model.addPropertyChangeListener(Property.MODEL_CHANGED, self)

        # The bounds of this object matches those of the real icon
        self._icon.addPropertyChangeListener(Property.FULL_BOUNDS, self)
        self.updateBounds()

    def updateBounds(self):
        # Updates the bounds of this node based on the inner icon
        self.setBounds(self._icon.localToParent(self._icon.bounds))

    def layoutChildren(self):
        self.super__layoutChildren()

        # Layout the icon and label
        iconWidth = self.width * self.scale
        labelWidth = self.label.width
        offsetX = -1 * (labelWidth - iconWidth) / 2.0

        self.label.setOffset(offsetX, self.height * self.scale)

    # Called when the NEO model has been updatedn
    def modelUpdated(self):
        self.updateLabel()

    def configureLabel(self, show_type):
        self.show_type = show_type
        self.updateLabel()

    def doubleClicked(self):
        self.model.doubleClicked()

    def altClicked(self):
        self.model.altClicked()

    @property
    def name(self):
        return self.label.text

    def setLabelVisible(self, visible):
        if self.visible:
            self.addChild(self.label)
        elif not self.visible and self.label.parent is not None:
            self.label.removeFromParent()

    def updateLabel(self):
        if self.show_type and self.model.name == "":
            self.label.text = "unnamed " + self.model.typeName
        elif self.show_type and self.model.name != "":
            self.label.text = self.model.name + " (" + self.model.typeName + ")"
        elif self.model.name == "":
            self.label.text = "unnamed"
        else:
            self.label.text = self.model.name

    def propertyChanged(self, event):
        if event == Property.FULL_BOUNDS:
            self.updateBounds()
        elif event == Property.MODEL_CHANGED:
            self.modelUpdated()


class NodeContainerIcon(ModelIcon):
    """Icon for a Node Container. The size of this icon scales depending on the
    number of nodes contained by the model.

    """

    MAX_SCALE = 1.5
    MIN_SCALE = 0.5

    def __init__(self, model, icon):
        ModelIcon.__init__(self, model, icon)
        self.num_nodes = -1
        self.size_label = Text("")
        self.size_label.font = NengoStyle.FONT_SMALL
        self.size_label.constrainWidthToTextWidth = True
        self.addChild(self.size_label)
        self.layoutChildren()
        self.modelUpdated()

    def udpateIconScale(self):
        """Scales the icon display size depending on how many nodes are
        contained within it.

        """
        self.num_nodes = self.modelParent.nodesCount
        dimensionality = self.modelParent.dimensionality

        neuronsText = str(self.num_nodes) + " Neuron" + ("" if self.num_nodes == 1 else "s")
        if self.modelParent.model.mode == SimulationMode.DIRECT:
            neuronsText = "Direct Mode"

        dimensionalityText = ""
        if dimensionality > 0:
            dimensionalityText = "   " + str(dimensionality) + "D"
        self.size_label.text = neuronsText + dimensionalityText

        if self.num_nodes >= self.nodeCountNormalization:
            num_nodes_normalized = 1
        else:
            num_nodes_normalized = math.sqrt(float(self.num_nodes)
                                             / self.nodeCountNormalization)

        self._icon.scale = self.MIN_SCALE + (num_nodes_normalized *
                                             (self.MAX_SCALE - self.MIN_SCALE))

    @property
    def nodeCountNormalization(self):
        raise NotImplementedError

    def layoutChildren(self):
        ModelIcon.layoutChildren(self)

        # center the label
        iconWidth = self._icon.width * self._icon.scale
        labelWidth = self.size_label.width * self.size_label.scale
        xOffset = (iconWidth - labelWidth) / 2.
        self.size_label.setOffset(xOffset, -(self.size_label.height + 1))

        self.size_label.moveToFront()

    def modelUpdated(self):
        ModelIcon.modelUpdated(self)
        self.updateIconScale()

    @property
    def modelParent(self):
        return ModelIcon.getModelParent(self)


class EnsembleIcon(WorldObject):
    CIRCLE_DIAMETER = 16
    PADDING = 4

    def __init__(self):
        self.icon_size = 44 + self.CIRCLE_DIAMETER + self.PADDING * 2
        self.setBounds(0, 0, self.icon_size, self.icon_size)

    def paint(self, context):
        WorldObject.paint(self, context)
        g2 = context.graphics

        g2.color = NengoStyle.COLOR_FOREGROUND
        g2.translate(self.PADDING, self.PADDING)

        g2.fillOval(2, 9, self.CIRCLE_DIAMETER, self.CIRCLE_DIAMETER)
        g2.fillOval(1, 34, self.CIRCLE_DIAMETER, self.CIRCLE_DIAMETER)
        g2.fillOval(26, 0, self.CIRCLE_DIAMETER, self.CIRCLE_DIAMETER)
        g2.fillOval(22, 22, self.CIRCLE_DIAMETER, self.CIRCLE_DIAMETER)
        g2.fillOval(44, 21, self.CIRCLE_DIAMETER, self.CIRCLE_DIAMETER)
        g2.fillOval(28, 44, self.CIRCLE_DIAMETER, self.CIRCLE_DIAMETER)


class EnsembleIcon(NodeContainerIcon):
    def __init__(self, ensemble):
        NodeContainerIcon.__init__(self, ensemble, VectorIcon())

    @property
    def nodeCountNormalization(self):
        return 1000


class FunctionInputIcon(ModelIcon):
    # Using "Serif" because Font.SERIF is not in Java 1.5 - TWB
    FONT = Font("Serif", Font.ITALIC, 45)
    TEXT = "f(t)"
    PADDING = 10

    def __init__(self, function_input):
        ModelIcon.__init__(self, function_input, self.create_text_icon())

    @staticmethod
    def createTextIcon():
        title_holder = WorldObject()

        title = Text(FunctionInputIcon.TEXT)
        title.font = FunctionInputIcon.FONT

        title.setOffset(FunctionInputIcon.PADDING * 1.5,
                        - 0.5 * FunctionInputIcon.PADDING)
        title_holder.addChild(title)

        title_holder.setBounds(0, 0, title.width
                               + FunctionInputIcon.PADDING * 2, title.height)
        return title_holder


class IconImage(WorldObject):
    def __init__(self, path):
        WorldObject.__init__(self, IconImageNode(path))
        self.pickable = False


class IconImageNode(PXImage):
    """Just like PImage, except it semantically zooms
    (i.e., at low scales, it does not paint its bitmap).

    """
    TEMP_ELLIPSE = Ellipse2D.Float()

    ENABLE_SEMANTIC_ZOOM = False

    def __init__(self, image_or_string=None):
        PXImage.__init__(self, image_or_string)
        self.path = GeneralPath()  # transient???
        self.original_bounds = self.bounds
        self.prev_scale = 0

    def updatePath(self, scale):
        origWidth = self.original_bounds.width
        origHeight = self.original_bounds.height
        width = origWidth * scale
        height = origWidth * scale
        offsetX = (origWidth - width) / 2.
        offsetY = (origHeight - height) / 2.

        self.path.reset()
        self.TEMP_ELLIPSE.setFrame(offsetX, offsetY, width, height)
        self.path.append(self.TEMP_ELLIPSE, False)

    def paint(self, context):
        s = context.scale
        g2 = context.graphics

        if self.ENABLE_SEMANTIC_ZOOM and s < uienvironment['SEMANTIC_ZOOM_LEVEL']:
            if s != self.prev_scale:
                delta = 1 - ((uienvironment['SEMANTIC_ZOOM_LEVEL'] - s)
                             / uienvironment['SEMANTIC_ZOOM_LEVEL'])
                self.updatePath(1. / delta)

            g2.setPaint(NengoStyle.COLOR_FOREGROUND)
            g2.fill(self.path)

            # g2.fill(self.boundsReference)

        else:
            self.super__setPaint(context)


class NetworkIcon(WorldObject):
    NODE_COLUMNS = 2
    NODE_ROWS = 3
    LINE_WIDTH = 4
    CIRCLE_DIAMETER = 18
    CIRCLE_RADIUS = CIRCLE_DIAMETER / 2
    ROW_HEIGHT = 30
    COLUMN_WIDTH = 75
    PADDING = 4

    def __init__(self):
        self.setBounds(0, 0, self.PADDING * 2 + self.CIRCLE_DIAMETER
                       + (self.NODE_COLUMNS - 1) * self.COLUMN_WIDTH,
                       self.PADDING * 2 + self.CIRCLE_DIAMETER
                       + (self.NODE_ROWS - 1) * self.ROW_HEIGHT)

    def paint(self, context):
        WorldObject.paint(context)
        g2 = context.graphics

        g2.stroke = BasicStroke(self.LINE_WIDTH)
        g2.color = NengoStyle.COLOR_FOREGROUND
        g2.translate(self.PADDING, self.PADDING)

        # Draw grid
        for row in xrange(self.NODE_ROWS):
            y_pos = row * self.ROW_HEIGHT
            g2.drawLine(self.CIRCLE_RADIUS, y_pos + self.CIRCLE_RADIUS,
                        self.COLUMN_WIDTH + self.CIRCLE_RADIUS,
                        y_pos + self.CIRCLE_RADIUS)

            for col in xrange(self.NODE_COLUMNS):
                g2.fillOval(col * self.COLUMN_WIDTH, y_pos,
                            self.CIRCLE_DIAMETER, self.CIRCLE_DIAMETER)

            # Draw diagonal line: top-left to bottom-right
            g2.drawLine(self.CIRCLE_RADIUS, self.CIRCLE_RADIUS,
                        self.CIRCLE_RADIUS + self.COLUMN_WIDTH
                        * (self.NODE_COLUMNS - 1), self.CIRCLE_RADIUS
                        + self.ROW_HEIGHT * (self.NODE_ROWS - 1))

            # Draw diagonal line: bottom-left to top-right
            g2.drawLine(self.CIRCLE_RADIUS, self.CIRCLE_RADIUS + self.ROW_HEIGHT
                        * (self.NODE_ROWS - 1), self.CIRCLE_RADIUS
                        + self.COLUMN_WIDTH * (self.NODE_COLUMNS - 1),
                        self.CIRCLE_RADIUS)


class NetworkIcon(NodeContainerIcon):
    def __init__(self, network):
        NodeContainerIcon.__init__(self, network, VectorIcon())

    @property
    def nodeCountNormalization(self):
        return 1000


class NodeIcon(ModelIcon):
    def __init__(self, node):
        ModelIcon.__init__(self, node, Path.createEllipse(0, 0, 50, 50))
        self._icon.paint = NengoStyle.COLOR_FOREGROUND
        self.configureLabel(False)


class ProbeIcon(ModelIcon):
    DEFAULT_COLOR = NengoStyle.COLOR_LIGHT_PURPLE

    def __init__(self, probe):
        ModelIcon.__init__(self, probe, WorldObject(Triangle()))

    @property
    def color(self):
        return self._icon.paint

    @color.setter
    def color(self, color):
        self._icon.paint = color


class Triangle(PXPath):
    """Icon which is basically a right-facing equilateral triangle"""
    SIZE = 20

    def __init__(self):
        PXPath.__init__(self)

        x, y = 0, 0
        self.moveTo(x, y)

        x -= self.SIZE * math.cos(math.pi / 6)
        y -= self.SIZE * math.sin(math.PI / 6)

        self.lineTo(x, y)

        y += self.SIZE

        self.lineTo(x, y)
        self.closePath()

        self.paint = NengoStyle.COLOR_LIGHT_PURPLE
