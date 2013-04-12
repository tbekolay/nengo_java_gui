# Destroyable: self.destroy()
# Droppable: self.justDropped(), self.acceptTarget(WorldObject)
# DroppableX: self.droppedOnTargets(WorldObject[])
# Interactable: self.getContextMenu()
# NamedObject: self.getName()
# Searchable: self.getSeearchableValues()
#  class SearchValuePair { String name, String value }


class PaintContext(object):
    def __init__(self, graphics, scale):
        self.graphics = graphics
        self.scale = scale
