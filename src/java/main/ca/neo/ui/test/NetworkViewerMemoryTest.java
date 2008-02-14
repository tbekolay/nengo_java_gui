package ca.neo.ui.test;

import java.lang.reflect.InvocationTargetException;

import javax.swing.SwingUtilities;

import ca.neo.math.Function;
import ca.neo.math.impl.ConstantFunction;
import ca.neo.model.Network;
import ca.neo.model.StructuralException;
import ca.neo.model.Termination;
import ca.neo.model.Units;
import ca.neo.model.impl.FunctionInput;
import ca.neo.model.impl.NetworkImpl;
import ca.neo.model.nef.NEFEnsemble;
import ca.neo.model.nef.NEFEnsembleFactory;
import ca.neo.model.nef.impl.NEFEnsembleFactoryImpl;
import ca.neo.ui.NeoGraphics;
import ca.neo.ui.models.nodes.UINetwork;

/**
 * Just a quick check for one type of memory leaks in Network Viewer.
 * 
 * @author Shu
 */
public class NetworkViewerMemoryTest {
	private static int i;
	private static NeoGraphics neoGraphics;
	// private static NetworkViewer netView;
	private static final int NUM_OF_LOOPS = 500;
//	private static Window window;

	// private static Window[] windows;
	public static Network createNetwork() throws StructuralException {

		Network network = new NetworkImpl();

		Function f = new ConstantFunction(1, 1f);
		// Function f = new SineFunction();
		FunctionInput input = new FunctionInput("input", new Function[] { f }, Units.UNK);
		network.addNode(input);

		NEFEnsembleFactory ef = new NEFEnsembleFactoryImpl();

		NEFEnsemble integrator = ef.make("integrator", 500, 1, "integrator1", false);
		network.addNode(integrator);
		integrator.collectSpikes(true);

		// Plotter.plot(integrator);
		// Plotter.plot(integrator, NEFEnsemble.X);

		float tau = .05f;

		Termination interm = integrator.addDecodedTermination("input",
				new float[][] { new float[] { tau } }, tau, false);
		// Termination interm = integrator.addDecodedTermination("input", new
		// float[][]{new float[]{1f}}, tau);
		network.addProjection(input.getOrigin(FunctionInput.ORIGIN_NAME), interm);

		Termination fbterm = integrator.addDecodedTermination("feedback",
				new float[][] { new float[] { 1f } }, tau, false);
		network.addProjection(integrator.getOrigin(NEFEnsemble.X), fbterm);

		// System.out.println("Network creation: " + (System.currentTimeMillis()
		// - start));
		return network;
	}

	static UINetwork network;

	public static long getApproximateUsedMemory() {
		System.gc();
		System.runFinalization();
		long totalMemory = Runtime.getRuntime().totalMemory();
		long free = Runtime.getRuntime().freeMemory();
		return totalMemory - free;
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {

		printMemoryUsed("Start");
		neoGraphics = new NeoGraphics();

		// Window windows = new Window[NUM_OF_LOOPS];
		for (i = 0; i < NUM_OF_LOOPS; i++) {

			try {

				SwingUtilities.invokeAndWait(new Runnable() {
					public void run() {

						try {
							network = new UINetwork(createNetwork());
							neoGraphics.getWorld().getGround().addChild(network);
							network.openViewer();
							// network.openViewer();
							//							
							// netView = new NetworkViewer(network);
							//							
							// window = new Window(
							// .getGround(), network);
						} catch (StructuralException e) {
							e.printStackTrace();
						}

					}
				});
				Thread.sleep(2000);

				SwingUtilities.invokeAndWait(new Runnable() {
					public void run() {
						network.destroy();
					}
				});

			} catch (InterruptedException e) {
				e.printStackTrace();
			} catch (InvocationTargetException e) {
				e.getTargetException().printStackTrace();
			}
			printMemoryUsed("Loop # " + i);
		}

	}

	public static void printMemoryUsed(String msg) {
		System.out.println("*** " + msg + " ***");
		System.out.println("Approximate used memory: " + getApproximateUsedMemory() / 1024 + " k");
	}

}
