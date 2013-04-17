# import java.awt.BorderLayout;

# import javax.swing.JDialog;
# import javax.swing.JPanel;

# import org.jfree.chart.ChartPanel;
# import org.jfree.chart.JFreeChart;

# import ca.nengo.plot.impl.DefaultPlotter;

class DialogPlotter(DefaultPlotter):
    """Plotter uses dialog rather than frames to support parent-child relationship
    with NengoGraphics components.

    """

    def __init__(self, parent):
        DefaultPlotter.__init__(self)
        self.parent = parent

    def showChart(self, chart, title):
        panel = ChartPanel(chart)

        dialog = JDialog(self.parent, title)
        dialog.contentPane.add(panel, BorderLayout.CENTER)

        dialog.pack()
        dialog.visible = True
