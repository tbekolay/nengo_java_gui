# import ca.nengo.math.Function;
# import ca.nengo.math.impl.ConstantFunction;
# import ca.nengo.model.SimulationException;
# import ca.nengo.model.StructuralException;
# import ca.nengo.model.Termination;
# import ca.nengo.model.Units;
# import ca.nengo.model.impl.FunctionInput;
# import ca.nengo.model.impl.NetworkImpl;
# import ca.nengo.model.nef.NEFEnsemble;
# import ca.nengo.model.nef.NEFEnsembleFactory;
# import ca.nengo.model.nef.impl.NEFEnsembleFactoryImpl;
# import ca.nengo.ui.lib.util.Util;
# import ca.nengo.util.Probe;

import javax.swing.SwingUtilities;

import ca.nengo.model.Network;
import ca.nengo.ui.NengoGraphics;
import ca.nengo.ui.lib.objects.activities.TrackedStatusMsg;
import ca.nengo.ui.models.nodes.UINetwork;

import time

tau = 0.05

def buildNetwork(network):
    network.name = "Integrator"

    Util.debugMsg("Network building started")

    f = ConstantFunction(1, 1)
    input = FunctionInput("input", [f], Units.UNK)

    # uiViewer.addNeoNode(uiInput)

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

    # Add probes

    integratorXProbe = network.simulator.addProbe("integrator", NEFEnsemble.X, True)
    time.sleep(0.5)

    # Test adding removing probes
    network.simulator.removeProbe(integratorXProbe)
    time.sleep(0.5)
    # add the probe back
    network.simulator.addProbe("integrator", NEFEnsemble.X, True)
    time.sleep(0.5)

    Util.debugMsg("Network building finished");


def run_example(network, runner):
    """Used to conveniently create a NengoGraphics instance
    with an existing Network model.

    """
    if isinstance(network, UINetwork):
        model = network
        model_ui = network
    elif isinstance(network, NetworkImpl):
        model = network
        nengo = NengoGraphics()

        task = TrackedStatusMsg("Creating Model UI")
        model_ui = UINetwork(model)
        nengo.world.ground.addChild(model_ui)
        model_ui.openViewer()
        task.finished()

    print "Running example: " + network.name

    # All UI functions and constructors must be invoked from the Swing
    # Event Thread

    if not isinstance(runner, Runnable):
        runner = make_runnable(runner)
    SwingUtilities.invokeLater(runner)

