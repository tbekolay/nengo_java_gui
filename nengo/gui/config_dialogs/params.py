#import java.io.Serializable;

#import ca.nengo.ui.lib.util.Util;

class Parameter(Serializable):
    """Describes a configuration parameter of a IConfigurable object."""

    def __init__(self, name, description, default):
        Serializable.__init__(self)
        self.name = name
        self.description = description
        self.default = default
        self.editable = True

    def createInputPanel(self):
        raise NotImplementedError

    @property
    def inputPanel(self):
        # Instantiate a new input panel for each call, this is ok.
        Util.Assert(not (not self.editable and self.default is None),
                "An input panel cannot be disabled and have no default value")

        inputPanel = self.createInputPanel()

        if self.default is not None:
            inputPanel.value = self.default
        inputPanel.enabled = self.editable
        return inputPanel;

    @property
    def tooltip(self):
        width = 250;
        css = "<style type = \"text/css\">"
              + "body { width: " + width + "px }"
              + "p { margin-top: 12px }" + "</style>"

        sType = "Type: " + self.typeName
        if self.description is not None:
            sBody = "<p><b>" + self.description + "</b></p>"
                    + "<p>" + sType + "</p>"
        else:
            sBody = sType

        return "<html><head>" + css + "</head><body>" + sBody + "</body></html>"

    @property
    def typeClass(self):
        raise NotImplementedError

    @property
    def typeName(self):
        raise NotImplementedError

    def toString(self):
        return self.typeName

#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.PropertyInputPanel;
#import ca.nengo.ui.configurable.panels.BooleanPanel;

class BooleanParam(Parameter):
    def createInputPanel(self):
        return BooleanPanel(self)

    @property
    def typeClass(self):
        return Boolean.class

    @property
    def typeName(self):
        return "Boolean"


#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.PropertyInputPanel;
#import ca.nengo.ui.configurable.panels.CouplingMatrixPanel;

class CouplingMatrixParam(Parameter):
    def __init__(self, name, description, default, fromSize=None, toSize=None):
        if name is None:
            name = "Editor"
        self.fromSize = fromSize
        self.toSize = toSize
        if default is not None:
            self.fromSize = len(default[0])
            self.toSize = len(default)
        CouplingMatrixParam.__init__(self, name, description, default)

    def createInputPanel(self):
        return CouplingMatrixPanel(self, self.fromSize, self.toSize)

    @property
    def typeClass(self):
        return float[][].class

    @property
    def typeName(self):
        return "Coupling Matrix"

#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.PropertyInputPanel;
#import ca.nengo.ui.configurable.panels.FloatPanel;

class FloatParam(Parameter):
    def createInputPanel(self):
        return FloatPanel(self)

    @property
    def typeClass(self):
        return float.class

    @property
    def typeName(self):
        return "Float"


#import java.util.Vector;

#import ca.nengo.config.ClassRegistry;
#import ca.nengo.math.Function;
#import ca.nengo.math.impl.FourierFunction;
#import ca.nengo.math.impl.GaussianPDF;
#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.descriptors.functions.ConfigurableFunction;
#import ca.nengo.ui.configurable.descriptors.functions.FnAdvanced;
#import ca.nengo.ui.configurable.descriptors.functions.FnConstant;
#import ca.nengo.ui.configurable.descriptors.functions.FnCustom;
#import ca.nengo.ui.configurable.descriptors.functions.FnReflective;
#import ca.nengo.ui.configurable.panels.FunctionPanel;

class FunctionParam(Parameter):
    def __init__(self, name, description, default, dimensionality, editable_dims):
        self.dimensionality = dimensionality
        self.editable_dims = editable_dims
        Parameter.__init__(self, name, description, default)

    def createConfigurableFunctions(self):
        functions = []
        functions.append(FnConstant(self.dimensionality, self.editable_dims))
        functions.append(FnCustom(self.dimensionality, False))

        # These functions can only have a input dimension of 1
        if self.dimensionality == 1:
            functions.append(FnReflective(FourierFunction.class, "Fourier Function",
                [FloatParam("Fundamental [Hz]", "The smallest frequency represented, in Hertz"),
                 FloatParam("Cutoff [Hz]", "The largest frequency represented, in Hertz"),
                 FloatParam("RMS", "Root-mean-square amplitude of the signal"),
                 LongParam("Seed", "Seed for the random number generator")],
                ["getFundamental", "getCutoff", "getRms", "getSeed"]))

            functions.append(FnReflective(GaussianPDF.class, "Gaussian PDF",
                [FloatParam("Mean", "Mean of the Gaussian distribution"),
                 FloatParam("Variance", "Variance of the Gaussian disribution"),
                 FloatParam("Peak", "Maximum value of the Gaussian distribution (at the mode)")],
                ["getMean", "getVariance", "getPeak"]))

        for type in ClassRegistry.instance.getImplementations(Function.class):
            if Function.class.isAssignableFrom(type):
                functions.append(FnAdvanced(type))

        return functions

    def createInputPanel(self):
        return FunctionPanel(self, createConfigurableFunctions())

    @property
    def typeClass(self):
        return Function.class

    @property
    def typeName(self):
        return "Function"



#import ca.nengo.math.Function;
#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.PropertyInputPanel;
#import ca.nengo.ui.configurable.panels.FunctionArrayPanel;

class FunctionArrayParam(Parameter):
    def __init__(self, name, description, default, dimensionality):
        self.dimensionality = dimensionality
        Parameter.__init__(self, name, description, default)

    def createInputPanel(self):
        return FunctionArrayPanel(self, self.dimensionality)

    @property
    def typeClass(self):
        return Function[].class

    @property
    def typeName(self):
        return "Functions"


#import ca.nengo.ui.configurable.panels.IntegerPanel;

class IntParam(RangedParam):
    def __init__(self, name, description, default, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum
        RangedParam.__init__(self, name, description, default)

    def createInputPanel(self):
        return IntPanel(self)

    @property
    def typeClass(self):
        return int.class

    @property
    def typeName(self):
        return "Integer"


#import ca.nengo.ui.configurable.panels.LongPanel;

class LongParam(RangedParam):
    def createInputPanel(self):
        return LongPanel(self)

    @property
    def typeClass(self):
        return long.class

    @property
    def typeName(self):
        return "Long"

#import ca.nengo.model.impl.NodeFactory;
#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.PropertyInputPanel;
#import ca.nengo.ui.configurable.panels.NodeFactoryPanel;

class NodeFactoryParam(Parameter):
    def createInputPanel(self):
        return NodeFactoryPanel(self)

    @property
    def typeClass(self):
        return NodeFactory.class

    @property
    def typeName(self):
        return "Node Factory"


class IndicatorPDFParam(Parameter):
    def createInputPanel(self):
        return IndicatorPDFPanel(self)

    @property
    def typeClass(self):
        return IndicatorPDF.class

    @property
    def typeName(self):
        return "Indicator PDF"

class ListSelectorParam(Parameter):
    def __init__(self, name, description, default, items):
        self.items = items
        Parameter.__init__(self, name, description, default)

    def createInputPanel(self):
        return ListSelectorPanel(self, self.items)

    @property
    def typeClass(self):
        return Object.class

    @property
    def typeName(self):
        return "List"


#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.PropertyInputPanel;
#import ca.nengo.ui.configurable.panels.StringPanel;

class StringParam(Parameter):
    def createInputPanel(self):
        return StringPanel(self)

    @property
    def typeClass(self):
        return String.class

    @property
    def typeName(self):
        return "Text"


#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.panels.TerminationWeightsInputPanel;

class TerminationWeightsParam(Parameter):
    def __init__(self, name, description, default, dimensionality):
        self.dimensionality = dimensionality
        Parameter.__init__(self, name, description, default)

    def createInputPanel(self):
        return TerminationWeightsInputPanel(self)

    @property
    def typeClass(self):
        return float[][].class

    @property
    def typeName(self):
        return "Coupling Matrix"



#import ca.nengo.ui.configurable.Property;

class RangedParam(Parameter):
    def __init__(self, name, description, default, minimum, maximum):
        self.checkRange = minimum is not None and maximum is not None
        self.minimum = minimum
        self.maximum = maximum
        Parameter.__init__(self, name, description, default)

