package ca.neo.ui.actions;

import ca.neo.model.Network;
import ca.shu.ui.lib.actions.StandardAction;
import ca.shu.ui.lib.exceptions.ActionException;

/**
 * TODO: Implement this
 * 
 * @author Shu Wu
 * 
 */
public class SetSimulatorAction extends StandardAction {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	Network network;

	public SetSimulatorAction(String actionName, Network network) {
		super("Set simulator", actionName);
		this.network = network;
	}

	@Override
	protected void action() throws ActionException {
		// TODO Auto-generated method stub

	}

}
