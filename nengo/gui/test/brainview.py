# import ca.nengo.model.StructuralException;
# import ca.nengo.model.impl.NetworkImpl;
# import ca.nengo.ui.models.nodes.UINetwork;

from . import run_example


def processNetwork(network):
    network.closeViewer()
    network.createBrainViewer()

run_example(NetworkImpl(), processNetwork)
