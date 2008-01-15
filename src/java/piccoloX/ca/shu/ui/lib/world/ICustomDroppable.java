package ca.shu.ui.lib.world;

import java.util.Collection;

/**
 * An object which accepts a list of drop targets. It differs from IDroppable in
 * that the Drag Handler does add any drop behavior.
 * 
 * @author Shu Wu
 */
public interface ICustomDroppable {

	public void droppedOnTargets(Collection<IWorldObject> targets);

}
