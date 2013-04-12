#import ca.nengo.math.Function;
#import ca.nengo.math.impl.ConstantFunction;
#import ca.nengo.model.Network;
#import ca.nengo.model.StructuralException;
#import ca.nengo.model.Units;
#import ca.nengo.model.impl.FunctionInput;
#import ca.nengo.model.impl.NetworkImpl;
#import ca.nengo.ui.actions.RunSimulatorAction;
#import ca.nengo.ui.dev.ExampleRunner;
#import ca.nengo.ui.models.nodes.UINetwork;

#import java.lang.reflect.InvocationTargetException;

#import javax.swing.SwingUtilities;

#import ca.nengo.math.Function;
#import ca.nengo.math.impl.ConstantFunction;
#import ca.nengo.model.Network;
#import ca.nengo.model.StructuralException;
#import ca.nengo.model.Termination;
#import ca.nengo.model.Units;
#import ca.nengo.model.impl.FunctionInput;
#import ca.nengo.model.impl.NetworkImpl;
#import ca.nengo.model.nef.NEFEnsemble;
#import ca.nengo.model.nef.NEFEnsembleFactory;
#import ca.nengo.model.nef.impl.NEFEnsembleFactoryImpl;
#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.models.nodes.UINetwork;

class NetworkViewerTest(ExampleRunner):
    """Starts Nengo with a network viewer open"""

    @staticmethod
    def CreateNetwork():
        network = NetworkImpl()

        f = ConstantFunction(1, 1.0)
        input = FunctionInput("input", [[f]], Units.UNK)

        network.addNode(input)

        return network

    def doStuff(self, network):
        RunSimulatorAction("Run", network, 0.0, 1.0, 0.002).doAction()


class NetworkViewerMemoryTest(object):
    """Just a quick check for one type of memory leaks in Network Viewer."""
    i = 0
    nengo
    NUM_LOOPS = 500
    network

    @staticmethod
    def createNetwork():
        network = NetworkImpl()

        f = ConstantFunction(1, 1.0)
        # Function f = new SineFunction();
        input = FunctionInput("input", [f], Units.UNK)
        network.addNode(input)

        ef = NEFEnsembleFactoryImpl()

        integrator = ef.make("integrator", 500, 1, "integrator1", False)
        network.addNode(integrator)
        integrator.collectSpikes(True)

        # Plotter.plot(integrator);
        # Plotter.plot(integrator, NEFEnsemble.X);

        tau = .05

        interm = integrator.addDecodedTermination("input", [[tau]], tau, False)
        # Termination interm = integrator.addDecodedTermination("input", new
        #     float[][]{new float[]{1f}}, tau);
        network.addProjection(input.getOrigin(FunctionInput.ORIGIN_NAME), interm)

        fbterm = integrator.addDecodedTermination("feedback", [[1.0]], tau, False)
        network.addProjection(integrator.getOrigin(NEFEnsemble.X), fbterm)

        # System.out.println("Network creation: " + (System.currentTimeMillis() - start));
        return network

    @staticmethod
    def getApproximateUsedMemory():
        System.gc()
        System.runFinalization()
        totalMemory = Runtime.getRuntime().totalMemory()
        free = Runtime.getRuntime().freeMemory()
        return totalMemory - free

    def makeAndOpenNetwork(self):
        self.network = UINetwork(createNetwork())
        self.nengoGraphics.world.ground.addChild(network)
        self.network.openViewer()
        # network.openViewer();
        # netView = new NetworkViewer(network);
        # window = new Window(.getGround(), network);

    def run(self):
        printMemoryUsed("Start")
        self.nengoGraphics = NengoGraphics()

        # Window windows = new Window[NUM_OF_LOOPS];
        for i in range(NUM_LOOPS):
            try:
                SwingUtilities.invokeAndWait(make_runnable(self.makeAndOpenNetwork))
                time.sleep(2)
                SwingUtilities.invokeAndWait(make_runnable(self.network.destroy))
            except InterruptedException, e:
                e.printStackTrace()
            except InvocationTargetException, e:
                e.targetException.printStackTrace()
            printMemoryUsed("Loop # " + i)

    @staticmethod
    def printMemoryUsed(String msg):
        System.out.println("*** " + msg + " ***")
        System.out.println("Approximate used memory: " + getApproximateUsedMemory() / 1024 + " k")

if __name__ == "__main__":
    NetworkViewerTest()