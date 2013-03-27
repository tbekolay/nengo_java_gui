# from java.awt import Font
from javax.swing import ButtonGroup
from javax.swing import JMenu, JMenuItem, JPopupMenu
from javax.swing import JLabel, JRadioButtonMenuItem

from .style import NengoStyle


class BaseMenuBuilder(object):
    """Used to build a menu. The created menu can later be converted to a Swing
    component."""
    def __init__(self, style=NengoStyle()):
        self.style = style
        assert self.style is None or isinstance(self.style, NengoStyle)

    def addAction(self, action):
        raise NotImplementedError

    def addActionsRadio(self, actions, selected=0):
        group = ButtonGroup()

        for i, action in enumerate(actions):
            item = JRadioButtonMenuItem(action.toSwingAction())
            item.selected = (i == selected)
            self.applyStyle(item)
            group.add(item)
            self.menu.add(item)

    def addLabel(self, msg):
        item = JLabel(msg)
        self.applyStyle(item)
        self.menu.add(item)

    def addSection(self, name, fontstyle=None):
        """Creates a new section in the Popup menu."""
        if self.isFirstSection:
            self.isFirstSection = False
        else:
            self.menu.addSeparator()  # menu.add(JSeparator()) ???

        label = JLabel(name)
        label.setLocation(4, 4)
        if fontstyle is not None:
            label.font = fontstyle
        self.applyStyle(label)
        self.menu.add(label)

    def addSubMenu(self, label):
        mb = MenuBuilder(label, style=self.style)
        self.menu.add(mb.menu)
        return mb

    def isCustomStyle(self):
        return type(self.style) != type(NengoStyle())

    def applyStyle(self, item, isTitle=False):
        if self.style is not None:
            self.style.applyMenuStyle(item, isTitle)

    def reset(self):
        """Removes all elements to start over"""
        self.menu.removeAll()


class MenuBuilder(BaseMenuBuilder):
    def __init__(self, label, style=NengoStyle()):
        BaseMenuBuilder.__init__(self, style)
        self.menu = JMenu(label)
        self.isFirstSection = True
        if style is not None:
            self.applyStyle(self.menu, self.style)

    def addAction(self, action, mnemonic= -1, shortcut=None):
        item = JMenuItem(action.toSwingAction())
        if shortcut is not None:
            item.accelerator = shortcut
        if mnemonic != -1:
            item.mnemonic = mnemonic

        self.applyStyle(item)
        self.menu.add(item)


class PopupMenuBuilder(BaseMenuBuilder):
    """Used to build a popup menu. The created menu can later be converted to a
    Swing component."""
    def __init__(self, label, style=NengoStyle()):
        BaseMenuBuilder.__init__(self, style)
        self.label = label
        self.isFirstSection = True
        self.menu = JPopupMenu(self.label)
        self.applyStyle(self.menu)

        if label is not None and label != "":
            self.addSection(label, self.style.FONT_LARGE)

    def addAction(self, action, section=None, index=None):
        assert section is not None and index is not None

        if section is not None:
            comps = self.menu.components
            for i, comp in enumerate(comps):
                if isinstance(comp, JLabel) and comp.text == section:
                    index = i + 1
                    break

        if index is None:
            index = self.menu.componentCount

        item = JMenuItem(action.toSwingAction())
        self.applyStyle(item)
        self.menu.insert(item, index)
