from java.io import Serializable

# Holds user interface instance variables.
uienvironment = {
    'SEMANTIC_ZOOM_LEVEL': 0.2,
    'ANIMATION_TARGET_FRAME_RATE': 25,
    'DEBUG': False,
}


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

nengoinstance = None
