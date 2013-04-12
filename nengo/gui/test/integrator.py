import java.lang.reflect.InvocationTargetException;

import javax.swing.SwingUtilities;

import ca.nengo.math.Function;
import ca.nengo.math.impl.ConstantFunction;
import ca.nengo.model.SimulationException;
import ca.nengo.model.StructuralException;
import ca.nengo.model.Termination;
import ca.nengo.model.Units;
import ca.nengo.model.impl.FunctionInput;
import ca.nengo.model.impl.NetworkImpl;
import ca.nengo.model.nef.NEFEnsemble;
import ca.nengo.model.nef.NEFEnsembleFactory;
import ca.nengo.model.nef.impl.NEFEnsembleFactoryImpl;
import ca.nengo.ui.NengoGraphics;
import ca.nengo.ui.lib.util.Util;
import ca.nengo.ui.models.nodes.UINetwork;
import ca.nengo.util.Probe;

import time

from . import buildNetwork, tau

class IntegratorExample(object):
    """In this example, an Integrator network is constructed."""

    def createUINetwork(self, nengoGraphics):
        network = UINetwork(NetworkImpl())
        nengoGraphics.world.ground.addChild(network)
        network.openViewer()
        network.viewer.ground.elasticEnabled = True

        threading.Thread(make_runnable(
            lambda: self.buildNetwork(network.model))).start()

    def buildNetwork(self, network):
        network.name = "Integrator"

        # Util.debugMsg("Network building started")

        f = ConstantFunction(1, 1.0)
        input = FunctionInput("input", [f], Units.UNK)

        # uiViewer.addNeoNode(uiInput);

        ef = NEFEnsembleFactoryImpl()
        integrator = ef.make("integrator", 500, 1, "integrator1", False)
        interm = integrator.addDecodedTermination("input", [[tau]], tau, False)
        fbterm = integrator.addDecodedTermination("feedback", [[1.0]], tau, False)

        network.addNode(integrator)
        time.sleep(1)
        network.addNode(input)
        time.sleep(1)
        # UINEFEnsemble uiIntegrator = new UINEFEnsemble(integrator);
        # uiViewer.addNeoNode(uiIntegrator);
        # uiIntegrator.collectSpikes(true);

        # UITermination uiInterm =
        # uiIntegrator.showTermination(interm.getName());
        # UITermination uiFbterm =
        # uiIntegrator.showTermination(fbterm.getName());

        network.addProjection(input.getOrigin(FunctionInput.ORIGIN_NAME), interm)
        time.sleep(0.5)
        network.addProjection(integrator.getOrigin(NEFEnsemble.X), fbterm)
        time.sleep(0.5)

        # Test removing projections
        network.removeProjection(interm)
        time.sleep(0.5)
        # add the projection back
        network.addProjection(input.getOrigin(FunctionInput.ORIGIN_NAME), interm)
        time.sleep(0.5)
        # Add probes
        integratorXProbe = network.simulator.addProbe("integrator", NEFEnsemble.X, True)
        time.sleep(0.5)
        # Test adding removing probes
        network.simulator.removeProbe(integratorXProbe)
        time.sleep(0.5)
        # add the probe back
        network.simulator.addProbe("integrator", NEFEnsemble.X, True)
        time.sleep(0.5)

        SwingUtilities.invokeLater(make_runnable(self.doPostUIStuff))

        # Util.debugMsg("Network building finished");

    def doPostUIStuff(self):
        # RunSimulatorAction simulatorRunner = new RunSimulatorAction("Run",
        # network, 0f, 1f, 0.0002f);
        # simulatorRunner.doAction();

        # SwingUtilities.invokeAndWait(new Runnable() {
        # public void run() {
        #    PlotTimeSeries plotAction = new PlotTimeSeries(
        #    integratorProbe.getModel().getData(),
        #    integratorProbe.getName());
        #    plotAction.doAction();
        # }
        # });
        self.network = None

    # private UIStateProbe integratorProbe;

    def __init__(self):
        self.run()

    def run(self):
        SwingUtilities.invokeAndWait(make_runnable(self.createUINetwork(NengoGraphics())))

if __name__ == "__main__":
    IntegratorExample()
