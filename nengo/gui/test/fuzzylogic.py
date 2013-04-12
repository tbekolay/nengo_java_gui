#import ca.nengo.math.Function;
#import ca.nengo.math.FunctionInterpreter;
#import ca.nengo.math.impl.AbstractFunction;
#import ca.nengo.math.impl.ConstantFunction;
#import ca.nengo.math.impl.DefaultFunctionInterpreter;
#import ca.nengo.model.Network;
#import ca.nengo.model.SimulationException;
#import ca.nengo.model.StructuralException;
#import ca.nengo.model.Units;
#import ca.nengo.model.impl.FunctionInput;
#import ca.nengo.model.impl.NetworkImpl;
#import ca.nengo.model.nef.NEFEnsemble;
#import ca.nengo.model.nef.NEFEnsembleFactory;
#import ca.nengo.model.nef.impl.NEFEnsembleFactoryImpl;
#import ca.nengo.model.neuron.Neuron;
#import ca.nengo.sim.Simulator;

#import ca.nengo.model.StructuralException;
#import ca.nengo.ui.models.nodes.UINetwork;

"""
Fuzzification is implemented as a function transformation. Inference is done
with multidimensional ensembles from which norms and conorms are decoded.
Composition is done by projecting high-dimensional fuzzy consequents
additively onto the same ensemble, from which the mode is selected by lateral
inhibition.

"""

def createNetwork():
    net = NetworkImpl()
    net.name = "FuzzyLogic"
    simulator = net.simulator

    # Rules:
    # 1) if A and (B or C) then 1
    # 2) if D then 2
    fi = DefaultFunctionInterpreter()

    functions = [fi.parse("x0 < .2", 1), ConstantFunction(1, 0.5),
                ConstantFunction(1, 0.2), ConstantFunction(1, 0.3)]
    fin = FunctionInput("input", functions, Units.UNK)

    ef = NEFEnsembleFactoryImpl()

    A = ef.make("A", 100, 1, "A", False)
    B = ef.make("B", 100, 1, "B", False)
    C = ef.make("C", 100, 1, "C", False)
    D = ef.make("D", 100, 1, "D", False)

    rule1a = ef.make("rule1a", 500, 2, "rule1a", False)
    rule1b = ef.make("rule1b", 500, 2, "rule1b", False)
    rule2 = ef.make("rule2", 200, 1, "rule2", False)
    rule2.collectSpikes(True)

    rule1a.addDecodedOrigin("OR", [MAX(2)], Neuron.AXON)
    rule1b.addDecodedOrigin("AND", [MIN(2)], Neuron.AXON)
    rule1a.doneOrigins()
    rule1b.doneOrigins()
    rule2.doneOrigins()

    output = ef.make("output", 500, 5, "fuzzyoutput", False)

    net.addNode(fin)
    net.addNode(A)
    net.addNode(B)
    net.addNode(C)
    net.addNode(D)
    net.addNode(rule1a)
    net.addNode(rule1b)
    net.addNode(rule2)
    net.addNode(output)

    A.addDecodedTermination("in", [[1.0, 0.0, 0.0, 0.0]], 0.005, False)
    B.addDecodedTermination("in", [[0.0, 1.0, 0.0, 0.0]], 0.005, False)
    C.addDecodedTermination("in", [[0.0, 0.0, 1.0, 0.0]], 0.005, False)
    D.addDecodedTermination("in", [[0.0, 0.0, 0.0, 1.0]], 0.005, False)

    net.addProjection(fin.getOrigin(FunctionInput.ORIGIN_NAME), A.getTermination("in"))
    net.addProjection(fin.getOrigin(FunctionInput.ORIGIN_NAME), B.getTermination("in"))
    net.addProjection(fin.getOrigin(FunctionInput.ORIGIN_NAME), C.getTermination("in"))
    net.addProjection(fin.getOrigin(FunctionInput.ORIGIN_NAME), D.getTermination("in"))

    rule1a.addDecodedTermination("B", [[1.0], [0.0]], 0.005, False)
    rule1a.addDecodedTermination("C", [[0.0], [1.0]], 0.005, False)
    rule1b.addDecodedTermination("A", [[1.0], [0.0]], 0.005, False)
    rule1b.addDecodedTermination("B or C", [[0.0], [1.0]], 0.005, False)
    rule2.addDecodedTermination("D", [[1.0]], 0.005, False)

    net.addProjection(B.getOrigin(NEFEnsemble.X), rule1a.getTermination("B"))
    net.addProjection(C.getOrigin(NEFEnsemble.X), rule1a.getTermination("C"))
    net.addProjection(A.getOrigin(NEFEnsemble.X), rule1b.getTermination("A"))
    net.addProjection(rule1a.getOrigin("OR"), rule1b.getTermination("B or C"))
    net.addProjection(D.getOrigin(NEFEnsemble.X), rule2.getTermination("D"))

    output.addDecodedTermination("rule1", [[0.4], [0.3], [0.2], [0.1], [0.0]], 0.005, False)
    output.addDecodedTermination("rule2", [[0.0], [0.1], [0.2], [0.3], [0.4]], 0.005, False)

    net.addProjection(rule1b.getOrigin("AND"), output.getTermination("rule1"))
    net.addProjection(rule2.getOrigin(NEFEnsemble.X), output.getTermination("rule2"))

    neg = -0.3
    pos = 0.9
    m = [[pos, neg, neg, neg, neg],
         [neg, pos, neg, neg, neg],
         [neg, neg, pos, neg, neg],
         [neg, neg, neg, pos, neg],
         [neg, neg, neg, neg, pos]]
    output.addDecodedTermination("recurrent", m, 0.005, False)

    clipped = [Clip(5, 0, 0.0, 1.0), Clip(5, 1, 0.0, 1.0), Clip(5, 2, 0.0, 1.0),
               Clip(5, 3, 0.0, 1.0), Clip(5, 4, 0.0, 1.0)]
    output.addDecodedOrigin("recurrent", clipped, Neuron.AXON)

    net.addProjection(output.getOrigin("recurrent"), output.getTermination("recurrent"))

    # Add probes
    try:
        simulator.addProbe(C.name, "in", True)
        simulator.addProbe(A.name, "in", True)
        simulator.addProbe(B.name, "in", True)
        simulator.addProbe(D.name, "in", True)
    except Exception, e:
        e.printStackTrace();

    return net

class MIN(AbstractFunction):
    def map(self, x):
        return min(x)

class MAX(AbstractFunction):
    def map(self, x):
        return max(x)

class Clip(AbstractFunction):
    def __init__(self, outdim, indim, min_, max_):
        AbstractFunction.__init__(self, outdim)
        self.d = indim
        self.min = min_
        self.max = max_

    def map(self, x):
        return min(max(x[self.d], self.min), self.max)

from . import run_example

if __name__ == '__main__':
    run_example(createNetwork(), RunSimulatorAction("Run", network)).doAction)
