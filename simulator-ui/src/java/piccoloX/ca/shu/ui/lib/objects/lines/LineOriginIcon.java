package ca.shu.ui.lib.objects.lines;

import java.awt.Color;
import java.awt.Graphics2D;

import ca.shu.ui.lib.Style.Style;
import ca.shu.ui.lib.world.PaintContext;
import ca.shu.ui.lib.world.piccolo.WorldObjectImpl;

/**
 * Icon for a line end well
 * 
 * @author Shu Wu
 */
public class LineOriginIcon extends WorldObjectImpl {

	private static final int _LINE_END_HEIGHT = 30;

	private static final int _LINE_END_WIDTH = 30;

	private static final long serialVersionUID = 1L;

	protected static final double ICON_RADIUS = Math
			.sqrt((_LINE_END_WIDTH * _LINE_END_WIDTH)
					+ (_LINE_END_HEIGHT * _LINE_END_HEIGHT)) / 2;

	private Color color = Style.COLOR_FOREGROUND;

	public LineOriginIcon() {
		super();
		this.setBounds(0, 0, _LINE_END_WIDTH, _LINE_END_HEIGHT);
		setColor(Style.COLOR_LINEENDWELL);

	}

	@Override
	public void paint(PaintContext paintContext) {
		super.paint(paintContext);
		Graphics2D g2 = paintContext.getGraphics();
		Color bright2 = Style.colorAdd(color, new Color(0.4f, 0.4f, 0.4f));
		if (paintContext.getScale() < 0.5) {
			g2.setColor(color);
			g2.fillOval(0, 0, _LINE_END_WIDTH, _LINE_END_HEIGHT);
		} else {

			Color color = getColor();

			Color dark = Style.colorAdd(Style.colorTimes(color, 0.65),
					new Color(0.05f, 0.05f, 0.05f));
			Color medium = color;
			Color bright1 = Style.colorAdd(color,
					new Color(0.15f, 0.15f, 0.15f));

			Color hilite = Style.colorAdd(Style.colorTimes(color, 0.5),
					new Color(0.5f, 0.5f, 0.5f));

			g2.setColor(dark);
			g2.fillOval(0, 0, _LINE_END_WIDTH, _LINE_END_HEIGHT);
			g2.setColor(medium);
			g2.fillOval(_LINE_END_WIDTH / 4, 0, _LINE_END_WIDTH / 2,
					_LINE_END_HEIGHT);
			g2.setColor(bright1);
			g2.fillOval(_LINE_END_WIDTH / 6, _LINE_END_HEIGHT / 2,
					2 * _LINE_END_WIDTH / 3, _LINE_END_HEIGHT / 3);
			g2.setColor(bright2);
			g2.fillOval(_LINE_END_WIDTH / 6 + 2, _LINE_END_HEIGHT / 2 + 2,
					2 * _LINE_END_WIDTH / 3 - 4, _LINE_END_HEIGHT / 3 - 2);

			g2.setColor(hilite);
			g2.fillOval(_LINE_END_WIDTH / 3 - 1, _LINE_END_HEIGHT / 6,
					_LINE_END_WIDTH / 3 + 2, 3 * _LINE_END_HEIGHT / 16);
		}
	}

	public Color getColor() {
		return color;
	}

	public void setColor(Color color) {
		this.color = color;
	}

}
