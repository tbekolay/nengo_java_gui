# import java.lang.reflect.InvocationTargetException;
#
# import javax.swing.SwingUtilities;
#
# import ca.nengo.model.SimulationException;
# import ca.nengo.model.StructuralException;
# import ca.nengo.model.impl.NetworkImpl;
# import ca.nengo.ui.NengoGraphics;
# import ca.nengo.ui.actions.RunSimulatorAction;
# import ca.nengo.ui.models.nodes.UINetwork;
#
# import ca.nengo.model.StructuralException;
# import ca.nengo.ui.NengoGraphics;
# import ca.nengo.ui.actions.RunSimulatorAction;
# import ca.nengo.ui.dev.ExampleRunner;
# import ca.nengo.ui.dev.FuzzyLogicExample;
# import ca.nengo.ui.models.nodes.UINetwork;

import threading


class DataViewerTest(object):
    TAU = 0.05

    def __init__(self):
        try:
            self.run()
        except InterruptedException, e:
            e.printStackTrace()
        except InvocationTargetException, e:
            e.targetException.printStackTrace()

    def createUINetwork(self, nengoGraphics):
        self.network = UINetwork(NetworkImpl())
        nengoGraphics.world.ground.addChild(self.network)
        self.network.openViewer()
        self.network.viewer.ground.elasticEnabled = True

        threading.Thread(lambda: self.buildNetwork(self.network.model)).start()

    def buildNetwork(self, network):
        TestUtil.buildNetwork(network)
        SwingUtilities.invokeLater(make_runnable(self.doPostUIStuff))

    def doPostUIStuff(self):
        simulatorRunner = RunSimulatorAction("Run", self.network, 0, 1, 0.0002)
        simulatorRunner.doAction()
        nengoinstance.dataViewerPaneVisible = True

    # integratorProbe  # UIStateProbe

    def run(self):
        SwingUtilities.invokeAndWait(
            make_runnable(lambda: self.createUINetwork(NengoGraphics())))


class DataViewerTest2(ExampleRunner):
    """Creates a Fuzzy Network, and runs it for 1 second"""

    def __init__(self):
        ExampleRunner.__init__(FuzzyLogicExample.createNetwork())

    def doStuff(self, network):
        RunSimulatorAction("Run", network, 0, 1, 0.002).doAction()
        nengoinstance.dataViewerPaneVisible = True


if __name__ == '__main__':
    DataViewerTest()
    DataViewerTest2()
