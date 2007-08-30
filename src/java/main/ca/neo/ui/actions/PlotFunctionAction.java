package ca.neo.ui.actions;

import ca.neo.math.Function;
import ca.neo.model.impl.FunctionInput;
import ca.neo.plot.Plotter;
import ca.neo.ui.configurable.ConfigException;
import ca.neo.ui.configurable.ConfigParam;
import ca.neo.ui.configurable.ConfigParamDescriptor;
import ca.neo.ui.configurable.IConfigurable;
import ca.neo.ui.configurable.descriptors.CFloat;
import ca.neo.ui.configurable.descriptors.CInt;
import ca.neo.ui.configurable.managers.UserTemplateConfigurer;
import ca.shu.ui.lib.actions.StandardAction;
import ca.shu.ui.lib.exceptions.ActionException;

public class PlotFunctionAction extends StandardAction implements IConfigurable {
	private static final long serialVersionUID = 1L;

	static final ConfigParamDescriptor pEnd = new CFloat("End");
	static final ConfigParamDescriptor pIncrement = new CFloat("Increment");
	static final ConfigParamDescriptor pStart = new CFloat("Start");
	// static final PropDescriptor pTitle = new PTString("Title");
	FunctionInput functionInput;
	ConfigParamDescriptor pFunctionIndex;
	String plotName;

	public PlotFunctionAction(String plotName, String actionName,
			FunctionInput functionInput) {
		super("Plot function input", actionName);
		this.plotName = plotName;
		this.functionInput = functionInput;

	}

	@Override
	protected void action() throws ActionException {
		pFunctionIndex = new CInt("Function index", 0, functionInput
				.getFunctions().length - 1);

		UserTemplateConfigurer config = new UserTemplateConfigurer(this);
		try {
			config.configureAndWait();
		} catch (ConfigException e) {
			e.defaultHandledBehavior();
		}

	}

	public void completeConfiguration(ConfigParam properties)
			throws ConfigException {
		String title = plotName + " - Function Plot";

		int functionIndex = (Integer) properties.getProperty(pFunctionIndex);
		float start = (Float) properties.getProperty(pStart);
		float end = (Float) properties.getProperty(pEnd);
		float increment = (Float) properties.getProperty(pIncrement);

		Function[] functions = functionInput.getFunctions();

		if (functionIndex >= functions.length) {
			throw new ConfigException("Function index out of bounds");

		}
		Function function = functionInput.getFunctions()[functionIndex];
		Plotter.plot(function, start, increment, end, title + " ("
				+ function.getClass().getSimpleName() + ")");

	}

	public ConfigParamDescriptor[] getConfigSchema() {

		ConfigParamDescriptor[] properties = { pFunctionIndex, pStart,
				pIncrement, pEnd };
		return properties;

	}

	public String getTypeName() {
		return "Function plotter";
	}

}