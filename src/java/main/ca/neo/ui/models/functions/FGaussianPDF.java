package ca.neo.ui.models.functions;

import ca.neo.math.impl.ConstantFunction;
import ca.neo.math.impl.GaussianPDF;
import ca.neo.ui.views.objects.configurable.struct.PTFloat;
import ca.neo.ui.views.objects.configurable.struct.PTInt;
import ca.neo.ui.views.objects.configurable.struct.PropertyStructure;

public class FGaussianPDF extends ConfigurableFunction {
	static final PropertyStructure[] propStruct = new PropertyStructure[] {
			new PTFloat("Mean"), new PTFloat("Variance"), new PTFloat("Peak") };


	public Class getFunctionClass() {
		return GaussianPDF.class;
	}

	public PropertyStructure[] getPropertiesSchema() {
		return propStruct;
	}

	public String getTypeName() {
		return "Gaussian PDF";
	}

}
