package ca.neo.ui;

import java.awt.event.ActionEvent;

import javax.swing.AbstractAction;
import javax.swing.JMenuBar;

import ca.neo.model.Network;
import ca.neo.ui.models.nodes.PNetwork;
import ca.neo.ui.util.UIBuilder;
import ca.neo.ui.views.objects.configurable.managers.DialogConfig;
import ca.neo.ui.widgets.Toolbox;
import ca.neo.util.Environment;
import ca.shu.ui.lib.util.GraphicsEnvironment;
import ca.shu.ui.lib.util.MenuBuilder;
import ca.shu.ui.lib.world.WorldObject;
import ca.shu.ui.lib.world.impl.GFrame;

public class NeoGraphics extends GFrame {

	public NeoGraphics(String title) {
		super(title + " - NEO Workspace");

		/*
		 * Only one instance of NeoWorld may be running at once
		 */
		GraphicsEnvironment.setInstance(this);

		Environment.setUserInterface(true);

	}

	private static final long serialVersionUID = 1L;

	public static void main(String[] args) {
		GraphicsEnvironment.setInstance(new NeoGraphics("NEOWorld"));
	}

	Toolbox canvasView;

	@Override
	public void constructMenuBar(JMenuBar menuBar) {
		MenuBuilder menu = new MenuBuilder("Start");
		menuBar.add(menu.getJMenu());
		menu.addAction(new CreateNetworkAction());
	}

	public Toolbox getCanvasView() {
		return canvasView;
	}

	/**
	 * 
	 * @param object
	 *            Object to be added to the top-level world
	 * @return the object being added
	 */
	public WorldObject addWorldObject(WorldObject object) {
		getWorld().getGround().catchObject(object);
		return object;
	}

	public void showCanvas() {
		if (canvasView == null) {
			System.out.println("Creating canvas");
			canvasView = new Toolbox();
			getWorld().getSky().addChild(canvasView);
		}
	}

	class CanvasAction extends AbstractAction {
		private static final long serialVersionUID = 1L;

		public CanvasAction() {
			super("Show Canvas");
		}

		public void actionPerformed(ActionEvent e) {
			showCanvas();
		}

	}

	class CreateNetworkAction extends AbstractAction {
		private static final long serialVersionUID = 1L;

		public CreateNetworkAction() {
			super("New Network");
		}

		public void actionPerformed(ActionEvent e) {
			(new Thread() {
				public void run() {
					PNetwork network;
					network = new PNetwork();
					new DialogConfig(network);

					if (network.isModelCreated())
						getWorld().getGround().catchObject(network);
				}
			}).start();

		}
	}

}
