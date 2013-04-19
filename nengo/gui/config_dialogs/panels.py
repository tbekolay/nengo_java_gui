#import java.awt.Component;
#import java.awt.Container;
#import java.awt.event.ActionEvent;
#import java.awt.event.ActionListener;

#import javax.swing.BorderFactory;
#import javax.swing.BoxLayout;
#import javax.swing.JButton;
#import javax.swing.JDialog;
#import javax.swing.JEditorPane;
#import javax.swing.JLabel;
#import javax.swing.JOptionPane;
#import javax.swing.JPanel;
#import javax.swing.event.HyperlinkEvent;
#import javax.swing.event.HyperlinkListener;

#import ca.nengo.ui.lib.actions.OpenURLAction;
#import ca.nengo.ui.lib.Style.NengoStyle;

class URLListener(HyperlinkListener):
    def hyperlinkUpdate(self, event):
        if event.eventType == HyperlinkEvent.EventType.ACTIVATED: 
            OpenURLAction(event.description, event.description).doAction()


class HelpAction(ActionListener):
    def __init__(self, help, param):
        self.help = help
        self.param = param
        ActionListener.__init__(self)

    def actionPerformed(self, event):
        editor = JEditorPane("text/html", self.param.tooltip)
        editor.editable = False
        editor.opaque = False
        editor.addHyperlinkListener(URLListener())
        JOptionPane.showMessageDialog(self.help, editor, self.param.name,
                                      JOptionPane.INFORMATION_MESSAGE, None)


class PropertyInputPanel(object):
    """Swing Input panel to be used to enter in the value for a ConfigParam."""

    def __init__(self, param):
        self.param = param

        label = JLabel(self.param.name)
        label.foreground = NengoStyle.COLOR_DARK_BLUE
        label.font = NengoStyle.FONT_BOLD

        help = JButton("<html><u>?</u></html>")
        help.focusable = False
        help.foreground = Color(120, 120, 180)
        help.borderPainted = False
        help.contentAreaFilled = False
        help.focusPainted = False
        help.addActionListener(HelpAction(help, self.param))

        labelPanel = JPanel()
        labelPanel.layout = BoxLayout(labelPanel, BoxLayout.X_AXIS)
        labelPanel.alignmentX = JPanel.LEFT_ALIGNMENT
        labelPanel.add(label)
        labelPanel.add(help);
        #labelPanel.add(Box.createHorizontalGlue())  # use this to right-justify question marks
        labelPanel.setMaximumSize(labelPanel.minimumSize)  # use this to keep question marks on left

        self.innerPanel = JPanel()
        self.innerPanel.layout = BoxLayout(self.innerPanel, BoxLayout.X_AXIS)
        self.innerPanel.alignmentX = JPanel.LEFT_ALIGNMENT 

        self.statusMessage = JLabel("")
        self.statusMessage.foreground = NengoStyle.COLOR_HIGH_SALIENCE

        self.outerPanel = JPanel()
        self.outerPanel.name = self.param.name
        self.outerPanel.toolTipText = self.param.tooltip
        self.outerPanel.layout = BoxLayout(self.outerPanel, BoxLayout.Y_AXIS)
        self.outerPanel.alignmentY = JPanel.TOP_ALIGNMENT
        self.outerPanel.border = BorderFactory.createEmptyBorder(0, 0, 10, 0)
        self.outerPanel.add(labelPanel)
        self.outerPanel.add(self.innerPanel)
        self.outerPanel.add(self.statusMessage)

    def add(self, comp):
        self.innerPanel.add(comp)

    @property
    def dialogParent(self):
        parent = self.outerPanel.parent
        while parent is not None:
            if isinstance(parent, JDialog):
                return parent
            parent = parent.parent
        raise RuntimeException("Input panel does not have a dialog parent")

    def removeFromPanel(self, comp):
        self.innerPanel.remove(comp)

    @property
    def statusMsg(self):
        return self.statusMessage.text

    @statusMsg.setter
    def statusMsg(self, msg):
        self.statusMessage.text = msg

    @property
    def name(self):
        return self.outerPanel.name

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, value):
        raise NotImplementedError

    @property
    def enabled(self):
        return self.innerPanel.isEnabled()

    @enabled.setter
    def enabled(self, enabled):
        self.innerPanel.setEnabled(enabled)

    @property
    def valueSet(self):
        raise NotImplementedError


#import java.awt.event.FocusEvent;
#import java.awt.event.FocusListener;

#import javax.swing.JTextField;

#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.PropertyInputPanel;

class PropertyTextPanel(PropertyInputPanel):
   
    protected enum TextError {
        NoError, ValueNotSet, InvalidFormat
    }
    
    protected String valueNotSetMessage = "Value not set";
    protected String invalidFormatMessage = "Invalid number format";
    
    /**
     * Text field component
     */
    protected JTextField textField;

    public PropertyTextPanel(Property property, int columns) {
        super(property);
        
        textField = new JTextField(columns);
        textField.addFocusListener(new TextFieldFocusListener());
        add(textField);
    }
    
    protected String getText() {
        return textField.getText();
    }
    
    /**
     * Check if a string is valid as the value for this property, and set
     * the appropriate status message.
     * @param value the current text
     * @return true if the text is valid, false otherwise
     */
    protected abstract TextError checkValue(String value);
    
    protected void valueUpdated() {
        TextError error = checkValue(getText());
        switch (error) {
        case ValueNotSet:
            setStatusMsg(valueNotSetMessage);
            break;
        case InvalidFormat:
            setStatusMsg(invalidFormatMessage);
            break;
        default:
            setStatusMsg("");
        }
    }
    
    public boolean isValueSet() {
        return (checkValue(getText()) == TextError.NoError);
    }
    
    @Override
    public void setValue(Object value) {
        textField.setText(value.toString());
        checkValue(getText());
    }
    
    @Override
    public void setEnabled(boolean enabled) {
        super.setEnabled(enabled);
        textField.setEnabled(enabled);
    }
    
    protected class TextFieldFocusListener implements FocusListener {

        public void focusGained(FocusEvent e) {
        }

        public void focusLost(FocusEvent e) {
            valueUpdated();
        }
    }
    

}



#import javax.swing.JCheckBox;
#import javax.swing.JLabel;

#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.PropertyInputPanel;

class BooleanPanel(PropertyInputPanel):
    def __init__(self, param):
        PropertyInputPanel.__init__(self, param)

        self.checkBox = JCheckBox()
        self.checkBox.selected = False
        self.add(self.checkBox)

        self.label = JLabel("Enable")
        self.add(self.label)

    @property
    def value(self):
        return self.checkBox.isSelected().booleanValue()

    @value.setter
    def value(self, val):
        self.checkBox.selected = val

    @property
    def valueSet(self):
        return True


#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.PropertyInputPanel;
#import ca.nengo.ui.configurable.matrixEditor.CouplingMatrixImpl;
#import ca.nengo.ui.configurable.matrixEditor.MatrixEditor;
#import ca.nengo.ui.lib.util.Util;

class CouplingMatrixPanel(PropertyInputPanel):
    def __init__(self, param, fromSize, toSize):
        PropertyInputPanel.__init__(self, param)
        self.couplingMatrix = CouplingMatrix(fromSize, toSize)
        self.editor = MatrixEditor(self.couplingMatrix)
        self.add(self.editor)

    @property
    def value(self):
        self.editor.finishEditing()
        return self.couplingMatrix.data

    @value.setter
    def value(self, val):
        # Transfers the new matrix values to the editor
        if isinstance(val, float[][]):
            matrix = val

            if len(matrix[0]) == couplingMatrix.fromSize and len(matrix) == couplingMatrix.toSize:
                for i in xrange(len(matrix)):
                    for j in xrange(len(matrix[0])):
                        self.editor.setValueAt(matrix[i][j], i, j)
            else:
                Util.debugMsg("Termination weights not applied because they don't match dimensions");

    @property
    def valueSet(self):
        return True

#import ca.nengo.ui.configurable.Property;

class FloatPanel(PropertyTextPanel):
    COLUMNS = 10

    @property
    def value(self):
        return float(self.text)

    def checkValue(self, textValue):
        if textValue is None or textValue == "":
            return TextError.ValueNotSet
        elif not textValue.matches("\\s*-??[0-9]*[.]??[0-9]*([eE][-|\\+]??[0-9]+)??\\s*"):
            return TextError.InvalidFormat
        else:
            return TextError.NoError

#import java.awt.event.ActionEvent;
#import java.awt.event.ItemEvent;
#import java.awt.event.ItemListener;

#import javax.swing.AbstractAction;
#import javax.swing.JButton;
#import javax.swing.JComboBox;
#import javax.swing.JDialog;

#import ca.nengo.math.Function;
#import ca.nengo.ui.actions.PlotFunctionAction;
#import ca.nengo.ui.configurable.PropertyInputPanel;
#import ca.nengo.ui.configurable.descriptors.PFunction;
#import ca.nengo.ui.configurable.descriptors.functions.AbstractFn;
#import ca.nengo.ui.configurable.descriptors.functions.ConfigurableFunction;
#import ca.nengo.ui.configurable.descriptors.functions.FnAdvanced;
#import ca.nengo.ui.lib.util.UserMessages;
#import ca.nengo.ui.lib.util.Util;

/**
 * Input Panel for editing an individual Function
 * 
 * @author Shu Wu
 */
public class FunctionPanel extends PropertyInputPanel {

    /**
     * Combo box for selecting a function type, types of function are stored in
     * PTFunction.functions
     */
    private JComboBox comboBox;

    private ConfigurableFunction[] configurableFunctionsList;

    /**
     * Function
     */
    private Function function = new ca.nengo.math.impl.ConstantFunction(1,0f);
    ;

    private JButton newBtn;

    private JButton previewBtn;
    private JButton configureBtn;
    /**
     * Currently selected item in the comboBox
     */
    private ConfigurableFunction selectedConfigurableFunction;

    /**
     * @param property TODO
     * @param functions TODO
     */
    public FunctionPanel(PFunction property, ConfigurableFunction[] functions) {
        super(property);
        this.configurableFunctionsList = functions;

        initPanel();
    }

    private void initPanel() {
        comboBox = new JComboBox(configurableFunctionsList);
        selectedConfigurableFunction = (AbstractFn) comboBox.getSelectedItem();

        comboBox.addItemListener(new ItemListener() {
            public void itemStateChanged(ItemEvent e) {
                if (comboBox.getSelectedItem() != selectedConfigurableFunction) {
                    setValue(null);
                    updateSelection(comboBox.getSelectedItem());
                }
            }
        });

        add(comboBox);

        newBtn = new JButton(new NewParametersAction());
        add(newBtn);

        configureBtn = new JButton(new EditAction());
        add(configureBtn);

        previewBtn = new JButton(new PreviewFunctionAction());
        add(previewBtn);

        updateSelection(comboBox.getSelectedItem());
    }

    private void updateSelection(Object selectedItem) {
        selectedConfigurableFunction = (ConfigurableFunction) comboBox.getSelectedItem();

        if (selectedItem instanceof FnAdvanced) {
            newBtn.setEnabled(true);
        } else {
            newBtn.setEnabled(false);
        }

    }

    /**
     * Previews the function
     */
    protected void previewFunction() {

        if (function != null) {
            (new PlotFunctionAction("Function preview", function, getDialogParent())).doAction();
        } else {
            UserMessages.showWarning("Please set this function first.");
        }
    }

    /**
     * Sets up the function using the configurable Function wrapper
     * 
     * @param resetValue
     *            Whether to reset the ConfigurableFunction's value before
     *            editing
     */
    protected void setParameters(boolean resetValue) {

        /*
         * get the JDialog parent
         */
        JDialog parent = getDialogParent();

        if (parent != null) {
            if (resetValue) {
                selectedConfigurableFunction.setFunction(null);
            }

            /*
             * Configure the function
             */
            Function function = selectedConfigurableFunction.configureFunction(parent);

            setValue(function);
        } else {
            UserMessages.showError("Could not attach properties dialog");
        }

    }

    @Override
    public PFunction getDescriptor() {
        return (PFunction) super.getDescriptor();
    }

    @Override
    public Function getValue() {
        return function;
    }

    @Override
    public boolean isValueSet() {
        if (function != null) {

            if (function.getDimension() != getDescriptor().getInputDimension()) {
                setStatusMsg("Input dimension must be " + getDescriptor().getInputDimension()
                        + ", it is currently " + function.getDimension());
                return false;
            }
            return true;

        } else {
            setStatusMsg("Function parameters not set");

            return false;
        }

    }

    @Override
    public void setValue(Object value) {

        if (value != null && value instanceof Function) {

            function = (Function) value;
            boolean configurableFunctionFound = false;

            /*
             * Updates the combo box to reflect the function type set
             */
            for (ConfigurableFunction element : configurableFunctionsList) {

                if (element.getFunctionType().isInstance(function)) {
                    selectedConfigurableFunction = element;
                    selectedConfigurableFunction.setFunction(function);

                    comboBox.setSelectedItem(selectedConfigurableFunction);
                    configurableFunctionFound = true;
                    break;
                }
            }

            if (!configurableFunctionFound) {
                Util.Assert(false, "Unsupported function");
            }

            if (isValueSet()) {
                setStatusMsg("");
            }

        } else {
            function = new ca.nengo.math.impl.ConstantFunction(1,0f);
        }

    }

    /**
     * Set up the parameters of a new function
     * 
     * @author Shu Wu
     */
    class NewParametersAction extends AbstractAction {

        private static final long serialVersionUID = 1L;

        public NewParametersAction() {
            super("New");
        }

        public void actionPerformed(ActionEvent e) {
            setParameters(true);
        }

    }

    /**
     * Preview the funciton
     * 
     * @author Shu Wu
     */
    class PreviewFunctionAction extends AbstractAction {

        private static final long serialVersionUID = 1L;

        public PreviewFunctionAction() {
            super("Preview");
        }

        public void actionPerformed(ActionEvent e) {
            previewFunction();
        }

    }

    /**
     * Set up the parameters of the existing function
     * 
     * @author Shu Wu
     */
    class EditAction extends AbstractAction {

        private static final long serialVersionUID = 1L;

        public EditAction() {
            super("Set");
        }

        public void actionPerformed(ActionEvent e) {
            setParameters(false);
        }

    }

}

#import java.awt.Container;
#import java.awt.event.ActionEvent;

#import javax.swing.AbstractAction;
#import javax.swing.JButton;
#import javax.swing.JDialog;
#import javax.swing.JLabel;
#import javax.swing.JTextField;

#import ca.nengo.math.Function;
#import ca.nengo.math.impl.ConstantFunction;
#import ca.nengo.ui.configurable.ConfigException;
#import ca.nengo.ui.configurable.ConfigResult;
#import ca.nengo.ui.configurable.ConfigSchema;
#import ca.nengo.ui.configurable.ConfigSchemaImpl;
#import ca.nengo.ui.configurable.IConfigurable;
#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.PropertyInputPanel;
#import ca.nengo.ui.configurable.descriptors.PFunction;
#import ca.nengo.ui.configurable.descriptors.PFunctionArray;
#import ca.nengo.ui.configurable.managers.UserConfigurer;
#import ca.nengo.ui.lib.util.UserMessages;
#import ca.nengo.ui.lib.util.Util;

/**
 * Input panel for entering an Array of Functions
 * 
 * @author Shu Wu
 */
public class FunctionArrayPanel extends PropertyInputPanel {

    /**
     * Function array
     */
    private Function[] myFunctionsWr;

    /**
     * Text field component for entering the dimensions of the function array
     */
    private JTextField tf;
    private int inputDimension;

    /**
     * @param property TODO
     * @param inputDimension TODO
     */
    public FunctionArrayPanel(PFunctionArray property, int inputDimension) {
        super(property);
        initPanel();
        this.inputDimension = inputDimension;
    }

    /**
     * Edits the Function Array using a child dialog
     */
    protected void editFunctionArray() {
        if (!isOutputDimensionsSet()) {
            UserMessages.showWarning("Output dimensions not set");
            return;
        }

        /*
         * get the JDialog parent
         */
        Container parent = getJPanel().getParent();
        while (parent != null) {
            if (parent instanceof JDialog) {
                break;
            }
            parent = parent.getParent();
        }

        if (parent != null && parent instanceof JDialog) {
            ConfigurableFunctionArray configurableFunctions = new ConfigurableFunctionArray(
                    getInputDimension(), getOutputDimension(), getValue());

            UserConfigurer config = new UserConfigurer(configurableFunctions, parent);
            try {
                config.configureAndWait();
                setValue(configurableFunctions.getFunctions());
            } catch (ConfigException e) {
                e.defaultHandleBehavior();
            }

        } else {
            UserMessages.showError("Could not attach properties dialog");
        }

    }

    @Override
    public PFunctionArray getDescriptor() {
        return (PFunctionArray) super.getDescriptor();
    }

    /**
     * @return TODO
     */
    public int getOutputDimension() {
        Integer integerValue = new Integer(tf.getText());
        return integerValue.intValue();
    }

    @Override
    public Function[] getValue() {
        return myFunctionsWr;
    }

    private void initPanel() {
        JLabel dimensions = new JLabel("Output Dimensions: ");
        tf = new JTextField(10);
        add(dimensions);
        add(tf);

        JButton configureFunction = new JButton(new EditFunctions());
        add(tf);
        add(configureFunction);

    }

    /**
     * @return True if Function Array dimensions has been set
     */
    public boolean isOutputDimensionsSet() {
        String textValue = tf.getText();

        if (textValue == null || textValue.compareTo("") == 0) {
            return false;
        }

        try {
            @SuppressWarnings("unused")
            Integer value = getOutputDimension();

        } catch (NumberFormatException e) {
            return false;
        }

        return true;
    }

    @Override
    public boolean isValueSet() {
        if (!isOutputDimensionsSet()) {
            return false;
        }
        
        if (myFunctionsWr != null && (myFunctionsWr.length == getOutputDimension())) {
            return true;
        } else {
            setStatusMsg("Functions not set");
        }
        
        if (myFunctionsWr == null || myFunctionsWr.length != getOutputDimension()) {
            myFunctionsWr = new Function[getOutputDimension()];
            for (int i=0; i<getOutputDimension(); i++) {
                myFunctionsWr[i] = new ConstantFunction(inputDimension, 0.0f);
            }
            return true;
        }

        return false;
    }

    /**
     * @param dimensions
     *            Dimensions of the function array
     */
    public void setDimensions(int dimensions) {
        tf.setText(dimensions + "");

    }

    @Override
    public void setValue(Object value) {
        Function[] functions = (Function[]) value;

        /*
         * Check that the functions are of the correct dimension before
         * committing
         */
        for (Function function : functions) {
            if (function.getDimension() != getInputDimension()) {
                Util.debugMsg("Saved functions are of a different dimension, they can't be used");
                return;
            }
        }

        if (value != null) {
            myFunctionsWr = functions;
            setDimensions(myFunctionsWr.length);
            setStatusMsg("");
        } else {

        }
    }

    /**
     * Edit Functions Action
     * 
     * @author Shu Wu
     */
    class EditFunctions extends AbstractAction {

        private static final long serialVersionUID = 1L;

        public EditFunctions() {
            super("Set Functions");
        }

        public void actionPerformed(ActionEvent e) {
            editFunctionArray();

        }

    }

    /**
     * @return TODO
     */
    public int getInputDimension() {
        return inputDimension;
    }
}

/**
 * Configurable object which creates an array of functions
 * 
 * @author Shu Wu
 */
/**
 * @author Shu
 */
class ConfigurableFunctionArray implements IConfigurable {

    /**
     * Number of functions to be created
     */
    private int outputDimension;

    /**
     * Dimensions of the functions to be created
     */
    private int inputDimension;

    /**
     * Array of functions to be created
     */
    private Function[] myFunctions;

    private Function[] defaultValues;

    /**
     * @param inputDimension TODO
     * @param outputDimension
     *            Number of functions to create
     * @param defaultValues TODO
     */
    public ConfigurableFunctionArray(int inputDimension, int outputDimension,
            Function[] defaultValues) {
        super();
        this.defaultValues = defaultValues;
        init(inputDimension, outputDimension);

    }

    /**
     * Initializes this instance
     * 
     * @param outputDimension
     *            number of functions to create
     */
    private void init(int inputDimension, int outputDimension) {
        this.inputDimension = inputDimension;
        this.outputDimension = outputDimension;
    }

    /*
     * (non-Javadoc)
     * 
     * @see ca.nengo.ui.configurable.IConfigurable#completeConfiguration(ca.nengo.ui.configurable.ConfigParam)
     */
    public void completeConfiguration(ConfigResult properties) {
        myFunctions = new Function[outputDimension];
        for (int i = 0; i < outputDimension; i++) {
            myFunctions[i] = ((Function) properties.getValue("Function " + i));

        }

    }

    /*
     * (non-Javadoc)
     * 
     * @see ca.nengo.ui.configurable.IConfigurable#getConfigSchema()
     */
    public ConfigSchema getSchema() {
        Property[] props = new Property[outputDimension];

        for (int i = 0; i < outputDimension; i++) {

            Function defaultValue = null;

            if (defaultValues != null && i < defaultValues.length && defaultValues[i] != null) {
                defaultValue = defaultValues[i];

            }
            PFunction function = new PFunction("Function " + i, inputDimension, false, defaultValue);
            function.setDescription("The function to use for dimension "+i);

            props[i] = function;
        }

        return new ConfigSchemaImpl(props);
    }

    /**
     * @return Functions created
     */
    public Function[] getFunctions() {
        return myFunctions;
    }

    /*
     * (non-Javadoc)
     * 
     * @see ca.nengo.ui.configurable.IConfigurable#getTypeName()
     */
    public String getTypeName() {
        return outputDimension + "x Functions";
    }

    public void preConfiguration(ConfigResult props) throws ConfigException {
        // do nothing
    }

    public String getDescription() {
        return getTypeName();
    }
    public String getExtendedDescription() {
        return null;
    }
    

}
#import ca.nengo.ui.configurable.descriptors.PInt;

/**
 * Input Panel for entering Integers
 * 
 * @author Shu Wu
 */
public class IntegerPanel extends PropertyTextPanel {
    
    private static int COLUMNS = 10;

    public IntegerPanel(PInt property) {
        super(property, COLUMNS);
    }

    @Override
    public PInt getDescriptor() {
        return (PInt) super.getDescriptor();
    }

    @Override
    public Integer getValue() {
        Integer integerValue = new Integer(getText());
        return integerValue.intValue();
    }

    @Override
    protected TextError checkValue(String textValue) {
        if (textValue == null || textValue.compareTo("") == 0) {
            return TextError.ValueNotSet;
        }

        try {
            Integer value = getValue();

            if (getDescriptor().isCheckRange()) {
                if (value > getDescriptor().getMax()
                        || value < getDescriptor().getMin()) {
                    return TextError.InvalidFormat;
                }
            }

        } catch (NumberFormatException e) {
            return TextError.InvalidFormat;
        }

        return TextError.NoError;
    }

}

#import ca.nengo.ui.configurable.descriptors.PLong;

/**
 * Input panel for entering Longs
 * 
 * @author Shu Wu
 */
public class LongPanel extends PropertyTextPanel {

    private static int COLUMNS = 10;

    public LongPanel(PLong property) {
        super(property, COLUMNS);
    }

    @Override
    public PLong getDescriptor() {
        return (PLong) super.getDescriptor();
    }

    @Override
    public Long getValue() {
        Long longValue = new Long(getText());
        return longValue;
    }

    @Override
    protected TextError checkValue(String textValue) {
        if (textValue == null || textValue.compareTo("") == 0) {
            return TextError.ValueNotSet;
        }

        try {
            Long value = getValue();

            if (getDescriptor().isCheckRange()) {
                if (value > getDescriptor().getMax()
                        || value < getDescriptor().getMin()) {
                    return TextError.InvalidFormat;
                }
            }

        } catch (NumberFormatException e) {
            return TextError.InvalidFormat;
        }

        return TextError.NoError;
    }

}


#import java.awt.event.ActionEvent;
#import java.awt.event.ItemEvent;
#import java.awt.event.ItemListener;
#import java.lang.reflect.Constructor;

#import javax.swing.AbstractAction;
#import javax.swing.JButton;
#import javax.swing.JComboBox;
#import javax.swing.JLabel;
#import javax.swing.JTextField;

#import ca.nengo.config.ClassRegistry;
#import ca.nengo.math.impl.IndicatorPDF;
#import ca.nengo.model.impl.NodeFactory;
#import ca.nengo.model.neuron.impl.ALIFNeuronFactory;
#import ca.nengo.model.neuron.impl.LIFNeuronFactory;
#import ca.nengo.model.neuron.impl.PoissonSpikeGenerator;
#import ca.nengo.model.neuron.impl.PoissonSpikeGenerator.LinearNeuronFactory;
#import ca.nengo.model.neuron.impl.PoissonSpikeGenerator.SigmoidNeuronFactory;
#import ca.nengo.model.neuron.impl.SpikeGeneratorFactory;
#import ca.nengo.model.neuron.impl.SpikingNeuronFactory;
#import ca.nengo.model.neuron.impl.SynapticIntegratorFactory;
#import ca.nengo.ui.configurable.ConfigException;
#import ca.nengo.ui.configurable.ConfigResult;
#import ca.nengo.ui.configurable.ConfigSchema;
#import ca.nengo.ui.configurable.ConfigSchemaImpl;
#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.PropertyInputPanel;
#import ca.nengo.ui.configurable.descriptors.PBoolean;
#import ca.nengo.ui.configurable.descriptors.PFloat;
#import ca.nengo.ui.lib.util.UserMessages;
#import ca.nengo.ui.models.constructors.AbstractConstructable;
#import ca.nengo.ui.models.constructors.ModelFactory;

/**
 * Input Panel for selecting and configuring a Node Factory
 * 
 * @author Shu Wu
 */
public class NodeFactoryPanel extends PropertyInputPanel {

    private static ConstructableNodeFactory[] NodeFactoryItems = new ConstructableNodeFactory[] {
        new CLinearNeuronFactory(), new CSigmoidNeuronFactory(), new CLIFNeuronFactory(),
        new CALIFNeuronFactory(), new CSpikingNeuronFactory() };

    private JComboBox factorySelector;

    private NodeFactory myNodeFactory;

    private ConstructableNodeFactory selectedItem;

    /**
     * @param property TODO
     */
    public NodeFactoryPanel(Property property) {
        super(property);
        init();
    }

    private void configureNodeFactory() {
        selectedItem = (ConstructableNodeFactory) factorySelector.getSelectedItem();

        try {
            NodeFactory model = (NodeFactory) ModelFactory.constructModel(selectedItem);
            setValue(model);
        } catch (ConfigException e) {
            e.defaultHandleBehavior();
        } catch (Exception e) {
            UserMessages.showError("Could not configure Node Factory: " + e.getMessage());
        }
    }

    private void init() {

        factorySelector = new JComboBox(NodeFactoryItems);
        add(factorySelector);

        /*
         * Reset value if the combo box selection has changed
         */
        factorySelector.addItemListener(new ItemListener() {
            public void itemStateChanged(ItemEvent e) {
                if (factorySelector.getSelectedItem() != selectedItem) {
                    setValue(null);
                }
            }

        });

        JButton configureBtn = new JButton(new AbstractAction("Set") {
            private static final long serialVersionUID = 1L;

            public void actionPerformed(ActionEvent arg0) {
                configureNodeFactory();
            }
        });

        add(configureBtn);

    }

    @Override
    public Object getValue() {
        return myNodeFactory;
    }

    @Override
    public boolean isValueSet() {
        if (myNodeFactory != null) {
            return true;
        } else {
            setStatusMsg("Node Factory must be set");
            return false;
        }
    }

    @Override
    public void setValue(Object value) {
        if (value == null) {
            myNodeFactory = null;
            return;
        }

        if (value instanceof NodeFactory) {
            myNodeFactory = (NodeFactory) value;
            setStatusMsg("");

            /*
             * Update the combo box selector with the selected Node Factory
             */
            boolean foundComboItem = false;
            for (ConstructableNodeFactory nodeFactoryItem : NodeFactoryItems) {

                if (nodeFactoryItem.getType().isInstance(myNodeFactory)) {
                    selectedItem = nodeFactoryItem;
                    factorySelector.setSelectedItem(selectedItem);
                    foundComboItem = true;
                    break;
                }
            }
            if (!foundComboItem) {
                throw new IllegalArgumentException("Unsupported Node Factory");
            }

        } else {
            throw new IllegalArgumentException("Value is not a Node Factory");
        }
    }
}

abstract class ConstructableNodeFactory extends AbstractConstructable {
    
    // Parameters common to many neurons
    static final Property pInterceptDefault = new PIndicatorPDF("Intercept","Range of the uniform distribution of neuron x-intercepts, (typically -1 to 1)");
    static final Property pMaxRateDefault = new PIndicatorPDF("Max rate [Hz]","Maximum neuron firing rate [10 to 100Hz for cortex]");
    static final Property pTauRCDefault = new PFloat("tauRC [s]","Membrane time constant, in seconds [typically ~0.02s]");
    static final Property pTauRefDefault = new PFloat("tauRef [s]","Refractory period, in seconds [typically ~0.002s]");
    
    private String name;
    private Class<? extends NodeFactory> type;

    public ConstructableNodeFactory(String name, Class<? extends NodeFactory> type) {
        super();
        this.name = name;
        this.type = type;
    }

    protected final Object configureModel(ConfigResult configuredProperties) throws ConfigException {
        NodeFactory nodeFactory = createNodeFactory(configuredProperties);

        if (!getType().isInstance(nodeFactory)) {
            throw new ConfigException("Expected type: " + getType().getSimpleName() + " Got: "
                    + nodeFactory.getClass().getSimpleName());
        } else {
            return nodeFactory;
        }
    }

    abstract protected NodeFactory createNodeFactory(ConfigResult configuredProperties)
            throws ConfigException;

    public Class<? extends NodeFactory> getType() {
        return type;
    }

    public final String getTypeName() {
        return name;
    }

    @Override
    public String toString() {
        return this.name;
    }

}

class CALIFNeuronFactory extends ConstructableNodeFactory {
    static final Property pIncN = new PIndicatorPDF("IncN","Increment of adaptation-related ion with each spike");
    static final Property pTauN = new PFloat("tauN [s]","Time constant of adaptation-related ion, in seconds");
    
    static final Property pIntercept = pInterceptDefault;
    static final Property pMaxRate = pMaxRateDefault;
    static final Property pTauRC = pTauRCDefault;
    static final Property pTauRef = pTauRefDefault;

    static final ConfigSchema zConfig = new ConfigSchemaImpl(new Property[] { pTauRC,
            pTauN, pTauRef, pMaxRate, pIntercept, pIncN });

    public CALIFNeuronFactory() {
        super("Adapting LIF Neuron", ALIFNeuronFactory.class);
    }

    @Override
    protected NodeFactory createNodeFactory(ConfigResult configuredProperties) {
        Float tauRC = (Float) configuredProperties.getValue(pTauRC);
        Float tauRef = (Float) configuredProperties.getValue(pTauRef);
        Float tauN = (Float) configuredProperties.getValue(pTauN);
        IndicatorPDF maxRate = (IndicatorPDF) configuredProperties.getValue(pMaxRate);
        IndicatorPDF intercept = (IndicatorPDF) configuredProperties.getValue(pIntercept);
        IndicatorPDF incN = (IndicatorPDF) configuredProperties.getValue(pIncN);

        return new ALIFNeuronFactory(maxRate, intercept, incN, tauRef, tauRC, tauN);
    }

    @Override
    public ConfigSchema getSchema() {
        return zConfig;
    }

}

class CLIFNeuronFactory extends ConstructableNodeFactory {
    
    static final Property pIntercept = pInterceptDefault;
    static final Property pMaxRate = pMaxRateDefault;
    static final Property pTauRC = pTauRCDefault;
    static final Property pTauRef = pTauRefDefault;

    static final ConfigSchema zConfig = new ConfigSchemaImpl(new Property[] { pTauRC,
            pTauRef, pMaxRate, pIntercept });

    public CLIFNeuronFactory() {
        super("LIF Neuron", LIFNeuronFactory.class);
    }

    @Override
    protected NodeFactory createNodeFactory(ConfigResult configuredProperties) {
        Float tauRC = (Float) configuredProperties.getValue(pTauRC);
        Float tauRef = (Float) configuredProperties.getValue(pTauRef);
        IndicatorPDF maxRate = (IndicatorPDF) configuredProperties.getValue(pMaxRate);
        IndicatorPDF intercept = (IndicatorPDF) configuredProperties.getValue(pIntercept);

        return new LIFNeuronFactory(tauRC, tauRef, maxRate, intercept);
    }

    @Override
    public ConfigSchema getSchema() {
        return zConfig;
    }

}

/**
 * Constructable Linear Neuron Factory
 * 
 * @author Shu Wu
 */
class CLinearNeuronFactory extends ConstructableNodeFactory {

    static final Property pIntercept = pInterceptDefault;
    static final Property pMaxRate = pMaxRateDefault;
    
    static final Property pRectified = new PBoolean("Rectified","Whether to constrain the neuron outputs to be positive");
    static final ConfigSchema zConfig = new ConfigSchemaImpl(new Property[] {
            pMaxRate, pIntercept, pRectified });

    public CLinearNeuronFactory() {
        super("Linear Neuron", LinearNeuronFactory.class);
    }

    @Override
    protected NodeFactory createNodeFactory(ConfigResult configuredProperties) {
        IndicatorPDF maxRate = (IndicatorPDF) configuredProperties.getValue(pMaxRate);
        IndicatorPDF intercept = (IndicatorPDF) configuredProperties.getValue(pIntercept);
        Boolean rectified = (Boolean) configuredProperties.getValue(pRectified);

        LinearNeuronFactory factory = new PoissonSpikeGenerator.LinearNeuronFactory(maxRate,
                intercept, rectified);

        return factory;
    }

    @Override
    public ConfigSchema getSchema() {
        return zConfig;
    }

}

class CSigmoidNeuronFactory extends ConstructableNodeFactory {

    static final Property pInflection = new PIndicatorPDF("Inflection","Range of x-values for the center point of the sigmoid");

    static final Property pMaxRate = pMaxRateDefault;
    static final Property pSlope = new PIndicatorPDF("Slope","Range of slopes for the sigmoid");
    static final ConfigSchema zConfig = new ConfigSchemaImpl(new Property[] { pSlope,
            pInflection, pMaxRate });

    public CSigmoidNeuronFactory() {
        super("Sigmoid Neuron", SigmoidNeuronFactory.class);
    }

    @Override
    protected NodeFactory createNodeFactory(ConfigResult configuredProperties) {
        IndicatorPDF slope = (IndicatorPDF) configuredProperties.getValue(pSlope);
        IndicatorPDF inflection = (IndicatorPDF) configuredProperties.getValue(pInflection);
        IndicatorPDF maxRate = (IndicatorPDF) configuredProperties.getValue(pMaxRate);

        return new PoissonSpikeGenerator.SigmoidNeuronFactory(slope, inflection, maxRate);
    }

    @Override
    public ConfigSchema getSchema() {
        return zConfig;
    }

}

/**
 * Customizable Neuron Factory Description Schema
 * 
 * @author Shu Wu
 */
class CSpikingNeuronFactory extends ConstructableNodeFactory {
    private static final Property pBias = new PIndicatorPDF("bias","Range of biases for the spiking neurons");
    private static final Property pScale = new PIndicatorPDF("scale","Range of gains for the spiking neurons");

    private static PListSelector getClassSelector(String selectorName, Class<?>[] classes) {
        ClassWrapper[] classWrappers = new ClassWrapper[classes.length];

        for (int i = 0; i < classes.length; i++) {
            classWrappers[i] = new ClassWrapper(classes[i]);
        }

        return new PListSelector(selectorName, classWrappers);
    }

    private Property pSpikeGenerator;

    private Property pSynapticIntegrator;

    public CSpikingNeuronFactory() {
        super("Customizable Neuron", SpikingNeuronFactory.class);
    }

    private Object constructFromClass(Class<?> type) throws ConfigException {
        try {
            Constructor<?> ct = type.getConstructor();
            try {
                return ct.newInstance();
            } catch (Exception e) {
                throw new ConfigException("Error constructing " + type.getSimpleName() + ": "
                        + e.getMessage());
            }
        } catch (SecurityException e1) {
            e1.printStackTrace();
            throw new ConfigException("Security Exception");
        } catch (NoSuchMethodException e1) {
            throw new ConfigException("Cannot find zero-arg constructor for: "
                    + type.getSimpleName());
        }
    }

    @Override
    protected NodeFactory createNodeFactory(ConfigResult configuredProperties)
            throws ConfigException {
        Class<?> synapticIntegratorClass = ((ClassWrapper) configuredProperties
                .getValue(pSynapticIntegrator)).getWrapped();
        Class<?> spikeGeneratorClass = ((ClassWrapper) configuredProperties
                .getValue(pSpikeGenerator)).getWrapped();

        IndicatorPDF scale = (IndicatorPDF) configuredProperties.getValue(pScale);
        IndicatorPDF bias = (IndicatorPDF) configuredProperties.getValue(pBias);

        /*
         * Construct Objects from Classes
         */
        SynapticIntegratorFactory synapticIntegratorFactory = (SynapticIntegratorFactory) constructFromClass(synapticIntegratorClass);
        SpikeGeneratorFactory spikeGeneratorFactory = (SpikeGeneratorFactory) constructFromClass(spikeGeneratorClass);

        return new SpikingNeuronFactory(synapticIntegratorFactory, spikeGeneratorFactory, scale,
                bias);
    }

    @Override
    public ConfigSchema getSchema() {
        /*
         * Generate these descriptors Just-In-Time, to show all possible
         * implementations in ClassRegistry
         */
        pSynapticIntegrator = getClassSelector("Synaptic Integrator", ClassRegistry.getInstance()
                .getImplementations(SynapticIntegratorFactory.class).toArray(new Class<?>[] {}));
        pSpikeGenerator = getClassSelector("Spike Generator", ClassRegistry.getInstance()
                .getImplementations(SpikeGeneratorFactory.class).toArray(new Class<?>[] {}));

        return new ConfigSchemaImpl(new Property[] { pSynapticIntegrator,
                pSpikeGenerator, pScale, pBias });
    }

    /**
     * Wraps a Class as a list item
     */
    private static class ClassWrapper {
        Class<?> type;

        public ClassWrapper(Class<?> type) {
            super();
            this.type = type;
        }

        public Class<?> getWrapped() {
            return type;
        }

        @Override
        public String toString() {
            /*
             * Return a name string that is at most two atoms long
             */
            String canonicalName = type.getCanonicalName();
            String[] nameAtoms = canonicalName.split("\\.");
            if (nameAtoms.length > 2) {
                return nameAtoms[nameAtoms.length - 2] + "." + nameAtoms[nameAtoms.length - 1];

            } else {
                return canonicalName;
            }

        }
    }
}

    private static class IndicatorPDFPanel extends PropertyInputPanel {
        JTextField highValue;
        JTextField lowValue;

        public Panel(Property property) {
            super(property);

            add(new JLabel("Low: "));
            lowValue = new JTextField(10);
            add(lowValue);

            add(new JLabel("High: "));
            highValue = new JTextField(10);
            add(highValue);

        }

        @Override
        public Object getValue() {
            String minStr = lowValue.getText();
            String maxStr = highValue.getText();

            if (minStr == null || maxStr == null) {
                return null;
            }

            try {
                Float min = new Float(minStr);
                Float max = new Float(maxStr);

                return new IndicatorPDF(min, max);
            } catch (NumberFormatException e) {
                setStatusMsg("Invalid number format");
                return null;
            } catch (IllegalArgumentException e) {
                setStatusMsg("Low must be less than or equal to high");
                return null;
            }

        }

        @Override
        public boolean isValueSet() {
            if (getValue() != null) {
                return true;
            } else {
                return false;
            }

        }

        @Override
        public void setValue(Object value) {
            if (value instanceof IndicatorPDF) {
                IndicatorPDF pdf = (IndicatorPDF) value;
                lowValue.setText((new Float(pdf.getLow())).toString());
                highValue.setText((new Float(pdf.getHigh())).toString());
            }
        }
    }

    private static class ListSelectorPanel extends PropertyInputPanel {
        private JComboBox comboBox;

        public Panel(Property property, Object[] items) {
            super(property);
            comboBox = new JComboBox(items);
            add(comboBox);
        }

        @Override
        public Object getValue() {
            return comboBox.getSelectedItem();
        }

        @Override
        public boolean isValueSet() {
            return true;
        }

        @Override
        public void setValue(Object value) {
            comboBox.setSelectedItem(value);
        }

    }
    


#import ca.nengo.ui.configurable.Property;

/**
 * Input Panel for Strings
 * 
 * @author Shu Wu
 */
public class StringPanel extends PropertyTextPanel {

    private static int COLUMNS = 10;

    public StringPanel(Property property) {
        super(property, COLUMNS);
        invalidFormatMessage = "Invalid text format";
    }

    @Override
    public Object getValue() {
        return getText();
    }
    
    @Override
    protected TextError checkValue(String text) {
        if (text == null || text.equals("")) {
            return TextError.ValueNotSet;
        } else {
            return TextError.NoError;
        }
    }

}

#import java.awt.Container;
#import java.awt.event.ActionEvent;

#import javax.swing.AbstractAction;
#import javax.swing.JButton;
#import javax.swing.JDialog;
#import javax.swing.JLabel;
#import javax.swing.JTextField;

#import ca.nengo.ui.configurable.ConfigException;
#import ca.nengo.ui.configurable.ConfigResult;
#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.PropertyInputPanel;
#import ca.nengo.ui.configurable.descriptors.PCouplingMatrix;
#import ca.nengo.ui.configurable.descriptors.PTerminationWeights;
#import ca.nengo.ui.configurable.managers.ConfigManager;
#import ca.nengo.ui.lib.util.UserMessages;
#import ca.nengo.ui.lib.util.Util;

/**
 * Input panel for Termination Weights Matrix
 * 
 * @author Shu
 */
public class TerminationWeightsInputPanel extends PropertyInputPanel {

    /**
     * The termination weights matrix
     */
    private float[][] matrix;

    /**
     * Text field containing the user-entered dimensions of the weights
     */
    private JTextField tf;

    /**
     * @param property TODO
     */
    public TerminationWeightsInputPanel(PTerminationWeights property) {
        super(property);
        initPanel();
    }

    /**
     * @return The dimensions of this termination
     */
    private int getDimensions() {

        Integer integerValue = new Integer(tf.getText());
        return integerValue.intValue();

    }

    /**
     * @return True if dimensions have been set
     */
    private boolean isDimensionsSet() {
        String textValue = tf.getText();

        if (textValue == null || textValue.compareTo("") == 0) {
            return false;
        }

        try {
            @SuppressWarnings("unused")
            Integer value = getDimensions();

        } catch (NumberFormatException e) {
            return false;
        }

        return true;
    }

    /**
     * @param dimensions
     *            New dimensions
     */
    private void setDimensions(int dimensions) {
        tf.setText(dimensions + "");
    }

    /**
     * Edits the termination weights matrix
     */
    protected void editMatrix() {
        if (!isDimensionsSet()) {
            UserMessages.showWarning("Input dimensions not set");
            return;
        }

        /*
         * get the JDialog parent
         */
        Container parent = getJPanel().getParent();
        while (parent != null) {
            if (parent instanceof JDialog) {
                break;
            }
            parent = parent.getParent();
        }

        if (parent != null && parent instanceof JDialog) {
            Property pCouplingMatrix;
            if (isValueSet()) {
                /*
                 * Create a property descriptor with a set matrix
                 */
                pCouplingMatrix = new PCouplingMatrix(getValue());
            }
            else {
                /*
                 * Create a property descriptor with no default value
                 */
                pCouplingMatrix = new PCouplingMatrix(getFromSize(), getToSize());
            }

            String configName = getFromSize() + " to " + getToSize() + " Coupling Matrix";

            try {
                ConfigResult result = ConfigManager.configure(
                        new Property[] { pCouplingMatrix }, configName, parent,
                        ConfigManager.ConfigMode.STANDARD);

                setValue(result.getValue(pCouplingMatrix));
            } catch (ConfigException e) {
                e.defaultHandleBehavior();
            }

        } else {
            UserMessages.showError("Could not attach properties dialog");
        }

    }

    /**
     * @return From size, of the matrix to be created
     */
    protected int getFromSize() {
        return getDimensions();
    }

    /**
     * @return To size, of the matrix to be created
     */
    protected int getToSize() {
        return getDescriptor().getEnsembleDimensions();
    }

    private void initPanel() {
        JLabel dimensions = new JLabel("Input Dim: ");
        tf = new JTextField(10);
        add(dimensions);
        add(tf);

        JButton configureFunction = new JButton(new EditMatrixAction());

        add(tf);
        add(configureFunction);
    }

    @Override
    public PTerminationWeights getDescriptor() {
        return (PTerminationWeights) super.getDescriptor();
    }

    @Override
    public float[][] getValue() {
        return matrix;
    }

    @Override
    public boolean isValueSet() {
        if (!isDimensionsSet()) {
            return false;
        }

        if (matrix != null && matrix[0].length == getDimensions()) {
            return true;
        } else if (getFromSize() == getToSize()){
            matrix = new float[getFromSize()][getToSize()];
            for (int i=0; i<getFromSize(); i++) {
                for (int j=0; j<getFromSize(); j++) {
                    if (i==j) {
                        matrix[i][j]=1;
                    } else {
                        matrix[i][j]=0;
                    }
                }
            }
            return true; // default to identity matrix when applicable, if not already set
        }
        setStatusMsg("Matrix not set");
        return false;
    }

    @Override
    public void setValue(Object value) {
        if ((value != null) && (value instanceof float[][])
                && (getToSize() == ((float[][]) value).length)) {
            matrix = (float[][]) value;
            setDimensions(matrix[0].length);

            if (isValueSet()) {
                setStatusMsg("");
            }
        } else {
            Util.debugMsg("Saved termination weights don't fit, they will be replaced");
        }
    }

    /**
     * User triggered action to edit the termination weights matrix
     * 
     * @author Shu Wu
     */
    class EditMatrixAction extends AbstractAction {

        private static final long serialVersionUID = 1L;

        public EditMatrixAction() {
            super("Set Weights");
        }

        public void actionPerformed(ActionEvent e) {
            editMatrix();
        }
    }
}

