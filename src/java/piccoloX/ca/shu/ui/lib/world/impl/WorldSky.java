package ca.shu.ui.lib.world.impl;

import java.awt.geom.Rectangle2D;
import java.util.Collection;

import sun.reflect.generics.reflectiveObjects.NotImplementedException;

import ca.shu.ui.lib.world.World;
import ca.shu.ui.lib.world.WorldLayer;
import ca.shu.ui.lib.world.WorldObject;
import edu.umd.cs.piccolo.PCamera;
import edu.umd.cs.piccolo.PNode;

public class WorldSky extends PCamera implements WorldLayer {

	@Override
	public void translateView(double arg0, double arg1) {
		// TODO Auto-generated method stub
		super.translateView(arg0, arg1);

	}

	/**
	 * 
	 */
	private static final long serialVersionUID = -7467076877836999849L;

	World world;

	public void addWorldObject(WorldObject node) {
		addChild((PNode) node);
	}

	public World getWorld() {
		return world;
	}

	public WorldSky(World world) {
		super();
		this.world = world;

	}

	public Collection<WorldObject> getChildrenAtBounds(Rectangle2D bounds) {
		throw new NotImplementedException();
	}

	public void addToWorldLayer(WorldObject wo) {

		addChild((PNode) wo);
	}

	public void addChildW(WorldObject child) {
		throw new NotImplementedException();
	}

	public void endDrag() {
		throw new NotImplementedException();
	}

	public WorldLayer getWorldLayer() {
		throw new NotImplementedException();
	}

	public boolean isDraggable() {
		throw new NotImplementedException();
	}

	public void justDropped() {
		throw new NotImplementedException();
	}

	public void addedToWorld() {
		throw new NotImplementedException();
	}

	public void popState(State state) {
		throw new NotImplementedException();
	}

	public void pushState(State state) {
		throw new NotImplementedException();

	}

	public void removedFromWorld() {
		throw new NotImplementedException();
	}

	public void startDrag() {
		throw new NotImplementedException();
	}

	public String getName() {
		throw new NotImplementedException();
	}

	public void setDraggable(boolean isDraggable) {
		throw new NotImplementedException();
	}

	public void destroy() {
		throw new NotImplementedException();
	}

	public void doubleClicked() {
		throw new NotImplementedException();

	}

}
