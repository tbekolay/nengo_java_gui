package ca.shu.ui.lib.objects.widgets;

import java.awt.AlphaComposite;
import java.awt.Color;
import java.awt.Composite;
import java.awt.Graphics2D;
import java.awt.Stroke;
import java.awt.geom.Point2D;

import ca.shu.ui.lib.objects.GEdge;
import ca.shu.ui.lib.world.impl.WorldObject;
import edu.umd.cs.piccolo.PNode;
import edu.umd.cs.piccolo.util.PPaintContext;

public class AffinityHalo extends GEdge {

	public AffinityHalo(WorldObject startNode, WorldObject endNode) {
		super(startNode, endNode);
		// TODO Set a thicker stroke for the affinity halo
		
//		this.setStroke(new Stroke( ))
	}

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	private AlphaComposite makeComposite(float alpha) {
		int type = AlphaComposite.SRC_OVER;
		return (AlphaComposite.getInstance(type, alpha));
	}

	// Nodes that override the visual representation of their super
	// class need to override a paint method.
	public void paint(PPaintContext aPaintContext) {
		Graphics2D g2 = aPaintContext.getGraphics();
		Composite originalComposite = g2.getComposite();
		g2.setComposite(makeComposite((float) 0.2));

		super.paint(aPaintContext);

		g2.setComposite(originalComposite);
	}

	public void updateEdge() {

		reset();

		// Note that the node's "FullBounds" must be used (instead of just the
		// "Bound")
		// because the nodes have non-identity transforms which must be included
		// when
		// determining their position.

		WorldObject start = getStartNode();
		WorldObject end = getEndNode();

		double sH = start.getHeight();
		double sW = start.getWidth();
		double eH = end.getHeight();
		double eW = end.getWidth();

		Point2D s0 = toLocal(start, 0, 0);
		Point2D s1 = toLocal(start, sW, 0);
		Point2D s2 = toLocal(start, 0, sH);
		Point2D s3 = toLocal(start, sW, sH);

		Point2D e0 = toLocal(end, 0, 0);
		Point2D e1 = toLocal(end, eW, 0);
		Point2D e2 = toLocal(end, 0, eH);
		Point2D e3 = toLocal(end, eW, eH);

		Point2D[] path = { s0, e0, s0, 
				s1, e1, s1, s3, e3, s3, s2, e2, s2, s0, e0, s0 };

		// double x1 = 0;
		// double y1 = getStartNode().getHeight();
		//
		// double x2 = 0;
		// double y2 = getEndNode().getHeight();
		//
		// double x3 = getEndNode().getWidth();
		// double y3 = 0;
		//
		// double x4 = getStartNode().getWidth();
		// double y4 = 0;
		//
		// Point2D[] path = { toLocal(getStartNode(), x1, y1),
		// toLocal(getEndNode(), x2, y2), toLocal(getEndNode(), x3, y3),
		// toLocal(getStartNode(), x4, y4), };

		this.setPaint(Color.black);
		this.setPathToPolyline(path);
		this.closePath();

	}
}