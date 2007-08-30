package ca.shu.ui.lib.activities;

import edu.umd.cs.piccolo.PNode;
import edu.umd.cs.piccolo.activities.PInterpolatingActivity;

/**
 * Activity which gradually changes the transparency of an node
 * 
 * @author Shu Wu
 */
public class Fader extends PInterpolatingActivity {

	private PNode node;

	private float startingTransparency;

	private float targetTransparency;

	/**
	 * @param target
	 *            Node target
	 * @param duration
	 *            Duration of the activity
	 * @param finalOpacity
	 *            Transparency target
	 */
	public Fader(PNode target, long duration, float finalOpacity) {
		super(duration, 25);
		this.node = target;
		this.targetTransparency = finalOpacity;
	}

	@Override
	public void setRelativeTargetValue(float zeroToOne) {

		super.setRelativeTargetValue(zeroToOne);

		float transparency = startingTransparency
				+ ((targetTransparency - startingTransparency) * (zeroToOne));

		node.setTransparency(transparency);

	}

	@Override
	protected void activityStarted() {
		startingTransparency = node.getTransparency();
	}

}
