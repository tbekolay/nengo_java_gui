class DoJungLayout(TrackedAction):
    def __init__(self, world, layoutType):
        TrackedAction.__init__(self, "Performing layout: " + layoutType.simpleName)
        self.world = world
        self.layout = None
        self.layoutType = layoutType

    def action(self):
        ctArgs = [Graph.class]
        ct = self.layoutType.getConstructor(ctArgs)
        SwingUtilities.invokeAndWait(make_runnable(self.world.updateGraph))
        args = [self.world.ground.updateGraph()]
        self.layout = ct.newInstance(args)

        layout.initialize(self.world.layoutBounds)

        if layout.isIncremental():
            timeNow = System.currentTimeMillis()
            while (not layout.incrementsAreDone()
                   and System.currentTimeMillis() - timeNow < 1000
                   and not layout.incrementsAreDone()):
                layout.advancePositions()

        # Layout nodes needs to be done in the Swing dispatcher thread
        SwingUtilities.invokeAndWait(make_runnable(
            lambda: self.world.ground.updateChildrenFromLayout(layout, True, True)))

class JungLayoutAction(LayoutAction):
    """Action for applying a Jung Layout.

    It implements LayoutAction, which allows it to be reversible.

    """

    def __init__(self, world, layoutClass, name):
        LayoutAction.__init__(self, world, "Apply layout " + name, name)
        self.world = world
        self.layoutClass = layoutClass

    def applyLayout(self):
        self.world.ground.elasticEnabled = False
        DoJungLayout(self.world, self.layoutClass).doAction()


class SetElasticLayoutAction(LayoutAction):
    """Action for starting and running a Iterable Jung Layout.
    
    """

    def __init__(self, world, name, enabled):
        LayoutAction.__init__(self, world, "Set Spring Layout: " + enabled, name)
        self.world = world
        self.enabled = enabled

    def applyLayout(self):
        self.world.ground.elasticEnabled = self.enabled

class SetLayoutBoundsAction(StandardAction):
    pHeight = PInt("Height")
    pWidth = PInt("Width")
    zProperties = [SetLayoutBoundsAction.pWidth, SetLayoutBoundsAction.pHeight]

    def __init__(self, actionName, parent):
        StandardAction.__init__(self, "Set layout bounds", actionName)
        self.parent = parent

    def completeConfiguration(self, properties):
        self.parent.setLayoutBounds(Dimension(properties.getValue(pWidth),
                                              properties.getValue(pHeight)))

    def action(self):
        properties = ConfigManager.configure(self.zProperties, "Layout bounds",
            nengoinstance, ConfigMode.TEMPLATE_NOT_CHOOSABLE)
        self.completeConfiguration(properties)

