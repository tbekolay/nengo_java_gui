package ca.shu.ui.lib.objects;

import ca.shu.ui.lib.Style.Style;
import ca.shu.ui.lib.world.WorldObject;
import edu.umd.cs.piccolo.nodes.PPath;

public class GContextButton extends WorldObject {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	Tooltip buttons;

	PPath circle;

	WorldObject node;

	public GContextButton(WorldObject node) {
		super();
		this.node = node;
		this.setSelectable(false);

		circle = PPath.createEllipse(0, 0, 25, 25);
		circle.setPaint(Style.COLOR_FOREGROUND);
		// circle.setStrokePaint(Color.white);

		circle.setPickable(false);

		addToLayout(circle);

	}

	@Override
	public Tooltip getTooltip() {
		// G node = new GFramedNode();
		Tooltip buttons = new Buttons();

		// node.addToLayout(buttons);
		// node
		// .setOffset(this.getWidth() - node.getWidth(),
		// this.getHeight() + 10);

		// node.setFrameVisible(true);
		return buttons;
	}

	class Buttons extends Tooltip {
		private static final long serialVersionUID = 1L;

		@Override
		protected void initButtons() {

			addButton(new GButton("Expand", new Runnable() {
				public void run() {
					node.animateToScale(node.getScale() * 1.5, 1000);
				}
			}));

			addButton(new GButton("Shrink", new Runnable() {
				public void run() {
					node.animateToScale(node.getScale() / 1.5, 1000);
				}
			}));

			addButton(new GButton("Close", new Runnable() {
				public void run() {
					node.removeFromParent();
				}
			}));
		}

	}

}
