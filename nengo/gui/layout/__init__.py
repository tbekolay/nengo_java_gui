import java.awt.geom.Point2D
import java.awt.geom.Rectangle2D
import java.io.Serializable
import java.util.Hashtable


class WorldLayout(java.io.Serializable):
    """Layout of nodes which is Serializable"""

    serialVersionUID = 30

    def __init__(self, name, world, elastic):
        self.name = name
        self.elastic = elastic  # Whether elastic layout is enabled
        self.node_positions = {}  # Node positions referenced by hash
        for wo in world.ground.children:
            self.add_position(wo, wo.offset)
        self.saved_view_bounds = world.sky.viewBounds

    def add_position(self, wo, position):
        self.node_positions[wo.hashCode(), position]

    def get_position(self, wo):
        return self.node_positions.get(wo.hashCode(), None)
