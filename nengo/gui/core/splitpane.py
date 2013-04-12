import java.awt.BorderLayout;
import java.awt.Container;
import java.awt.Dimension;
from java.awt.event import ComponentListener
import java.awt.event.FocusAdapter;
import java.awt.event.FocusEvent;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;

import javax.swing.BorderFactory;
import javax.swing.JLabel;
import javax.swing.JPanel;
from javax.swing import JSplitPane


class AuxResizeListener(ComponentListener):
    def __init__(self, comp):
        ComponentListener.__init__(self)
        self.comp = comp

    def componentHidden(self, event):
        pass

    def componentMoved(self, event):
        pass

    def componentResized(self, event):
        self.comp.updateAuxSize()

    def componentShown(self, event):
        pass


class LeftFocusListener(FocusAdapter):
    def __init__(self, comp):
        FocusAdapter.__init__(self)
        self.comp = comp

    def focusGained(self, event):
        if self.comp.auxPanel is not None:
            self.comp.auxPanel.requestFocusInWindow()


class HideButtonListener(MouseListener):
    def __init__(self, pane, button):
        MouseListener.__init__(self)
        self.pane = pane
        self.button = button

    def mouseClicked(self, event):
        self.pane.auxVisible = False

    def mouseEntered(self, event):
        self.button.background = NengoStyle.COLOR_FOREGROUND2

    def mouseExited(self, event):
        self.button.background = None

    def mousePressed(self, event):
        pass

    def mouseReleased(self, event):
        pass


class AuxillarySplitPane(JSplitPane):
    """Customized split pane implementation which holds main and an auxillary
    container which can be hidden.

    """

    MINIMUM_WIDTH = 300
    MINIMUM_HEIGHT = 200

    ORIENTATIONS = ['top', 'bottom', 'left', 'right']

    @staticmethod
    def getJSplitPaneOrientation(orientation):
        if orientation == 'left' or orientation == 'right':
            return JSplitPane.HORIZONTAL_SPLIT
        else:
            return JSplitPane.VERTICAL_SPLIT

    def __init__(self, mainPanel, auxPanel, auxTitle, orientation,
                 showTitle=True, minsize=Dimension(
                     AuxillarySplitPane.MINIMUM_WIDTH,
                     AuxillarySplitPane.MINIMUM_HEIGHT)):
        if orientation not in self.ORIENTATIONS:
            raise ValueError("Orientation should be one of "
                             "top, bottom, left, right")

        JSplitPane.__init__(self,
            AuxillarySplitPane.getJSplitPaneOrientation(orientation))
        self.mainPanel = mainPanel
        self.auxTitle = auxTitle

        self.orientation = orientation
        self.minimumSize = minsize
        self.showTitle = showTitle
        self.resizable = True

        self.auxPanelVisibleSize
        self.auxPanelWr

        self.addComponentListener(AuxResizeListener(self))
        self.init(auxPanel)

    def init(self, auxPanel):
        NengoStyle.applyStyle(self)
        self.oneTouchExpandable = True
        self.border = None
        self.setAuxPane(auxPanel, self.auxTitle)
        self.setAuxVisible(False)

    def setAuxPane(self, auxPanel, auxTitle):
        self.auxPanelWr = self.createAuxPanelWrapper(auxPanel, auxTitle)

        if auxPanel is None:
            self.setAuxVisible(False)
        else:
            self.setAuxVisible(True, True)

        if self.orientation == 'left':
            self.leftComponent = self.auxPanelWr
            self.rightComponent = self.mainPanel
        elif self.orientation == 'right':
            self.leftComponent = self.mainPanel
            self.rightComponent = self.auxPanelWr
        elif self.orientation == 'bottom':
            self.topComponent = self.mainPanel
            self.bottomComponent = self.auxPanelWr
        elif self.orientation == 'top':
            self.topComponent = self.auxPanelWr
            self.bottomComponent = self.mainPanel

    def createAuxPanelWrapper(self, auxPanel, auxTitle):
        # Initialize auxillary panel
        leftPanel = JPanel()
        leftPanel.layout = BorderLayout()
        leftPanel.addFocusListener(LeftFocusListener(self))

        # NengoStyle.applyStyle(leftPanel);

        if self.showTitle:
            # Create auxillary panel's title bar

            titleBar = JPanel()
            titleBar.border = BorderFactory.createEmptyBorder(0, 0, 5, 0))
            NengoStyle.applyStyle(titleBar)
            titleBar.background = NengoStyle.COLOR_BACKGROUND2
            titleBar.opaque = True
            titleBar.layout = BorderLayout()

            titleLabel = JLabel(title)

            titleLabel.font = NengoStyle.FONT_BIG
            NengoStyle.applyStyle(titleLabel)
            titleLabel.background = NengoStyle.COLOR_BACKGROUND2
            titleLabel.opaque = True

            hideButtonTxt = " >> " if self.orientation == 'right' else " << "

            hideButton = JLabel(hideButtonTxt)
            NengoStyle.applyStyle(hideButton)
            hideButton.background = NengoStyle.COLOR_BACKGROUND2
            hideButton.opaque = True

            # Keep in this order, Swing puts items added first on top.
            # We want the button to be on top
            titleBar.add(hideButton, BorderLayout.EAST)
            titleBar.add(titleLabel, BorderLayout.WEST)

            hideButton.addMouseListener(HideButtonListener(self, hideButton))

            leftPanel.add(titleBar, BorderLayout.NORTH)

        leftPanel.minimumSize = self.minimumSize

        if auxPanel is not None:
            # NengoStyle.applyStyle(auxPanel)
            leftPanel.add(auxPanel, BorderLayout.CENTER)

        return leftPanel

    @resizable.setter
    def resizable(self, resizable):
        if resizable != self.resizable:
            self.resizable = resizable
            self.setProperDividerSize(self.isAuxVisible, resizable)
            if not resizable:
                self.dividerLocation = 0

    @property
    def isAuxVisible(self):
        return self.auxPanelWr.isVisible()

    @isAuxVisible.setter
    def isAuxVisible(self, visible):
        self.setAuxVisible(visible, False)

    def setAuxVisible(self, visible, resetDividerLocation=False):
        if visible:
            minAuxSize = self.minAuxSize
            if self.auxPanelVisibleSize < minAuxSize or resetDividerLocation:
                self.setAuxPanelSize(minAuxSize)
            else:
                self.setAuxPanelSize(self.auxPanelVisibleSize)

            self.setProperDividerSize(visible, self.resizable)

            if not self.auxPanelWr.visible:
                self.auxPanelWr.requestFocus()
                self.auxPanelWr.visible = True
            self.auxPanelWr.requestFocusInWindow()
        else:
            self.auxPanelWr.visible = False
            self.setProperDividerSize(visible, self.resizable)

    def setProperDividerSize(self, visible, resizable):
        """Set the divider size, given whether the panel
        will be visible or resizable."""
        if visible and resizable:
            self.dividerSize = 2
        else:
            self.dividerSize = 0

    def updateAuxSize(self):
        self.auxPanelSize(self.auxPanelVisibleSize)

    @dividerLocation.setter
    def dividerLocation(self, location):
        JSplitPane.setDividerLocation(self, location)
        newAuxPanelSize = self.flipLocation(location)
        if newAuxPanelSize >= self.minAuxSize):
            self.auxPanelVisibleSize = newAuxPanelSize

    @auxPanelSize.setter
    def auxPanelSize(self, size):
        self.dividerLocation = self.flipLocation(size)

    @property
    def splitDim(self):
        """Return the size in the split direction."""
        if self.orientation == 'top' or self.orientation == 'bottom':
            return self.height
        else:
            return self.width

    def flipLocation(self, location):
        """Turn a location into an auxPanelSize, or vice versa."""
        if self.flippedOrientation:
            return self.splitDim - location
        else:
            return location

    @property
    def minAuxSize(self):
        """Get the minimum size of the auxPanel, in the split direction."""
        if self.orientation == 'top' or self.orientation == 'bottom':
            return self.auxPanelWr.minimumSize.height
        else:
            return self.auxPanelWr.minimumSize.width

    @property
    def flippedOrientation(self):
        """Whether the orientation requires flipping the location
        (right or bottom).

        """
        return self.orientation == 'bottom' or self.orientation == 'right'
