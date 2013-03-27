from java.awt import Color, Container, Font
from javax.swing import JComponent, UIManager
from javax.swing.tree import DefaultTreeCellRenderer


class NengoStyle(object):
    GTK = UIManager.systemLookAndFeelClassName == "com.sun.java.swing.plaf.gtk.GTKLookAndFeel"

    ANIMATION_DROP_IN_WORLD_MS = 200

    # ## Colors
    COLOR_BACKGROUND = Color.black
    COLOR_FOREGROUND = Color.white
    COLOR_BACKGROUND2 = Color.darkGray
    COLOR_FOREGROUND2 = Color.gray
    COLOR_BORDER_SELECTED = Color.orange
    COLOR_DARK_BLUE = Color(0, 0, 80)

    COLOR_CONFIGURE_BACKGROUND = Color.white

    # ## Button colors
    COLOR_BUTTON_BACKGROUND = Color.darkGray
    COLOR_BUTTON_BORDER = Color.darkGray

    COLOR_BUTTON_HIGHLIGHT = Color.black

    COLOR_BUTTON_SELECTED = Color.gray
    COLOR_DARKBORDER = Color.darkGray

    # ## Other colors
    COLOR_DISABLED = Color.gray
    COLOR_ANCHOR = Color.lightGray
    COLOR_HIGH_SALIENCE = Color(150, 0, 0)

    # ## Search colors
    COLOR_SEARCH_BOX_BORDER = Color.green
    COLOR_SEARCH_BAD_CHAR = Color.red

    # ## Named colors
    COLOR_LIGHT_PURPLE = Color(225, 180, 255)
    COLOR_LIGHT_BLUE = Color(176, 220, 246)
    COLOR_LIGHT_GREEN = Color(176, 246, 182)

    # ## Line colors
    COLOR_LINE = COLOR_LIGHT_GREEN

    COLOR_LINE_HIGHLIGHT = Color.red

    COLOR_LINEEND = COLOR_LIGHT_GREEN

    COLOR_LINEENDWELL = COLOR_LIGHT_BLUE
    COLOR_LINEIN = Color(0, 128, 0)

    COLOR_MENU_BACKGROUND = Color.black
    COLOR_NOTIFICATION = Color.orange

    COLOR_TOOLTIP_BORDER = Color(100, 149, 237)

    # ## Fonts
    FONT_FAMILY = UIManager.defaults.getFont("TabbedPane.font").family

    FONT_BOLD = Font(FONT_FAMILY, Font.BOLD, 14)
    FONT_BUTTONS = Font(FONT_FAMILY, Font.PLAIN, 14)
    FONT_LARGE = Font(FONT_FAMILY, Font.BOLD, 18)
    FONT_NORMAL = Font(FONT_FAMILY, Font.PLAIN, 14)

    FONT_SMALL = Font(FONT_FAMILY, Font.PLAIN, 10)
    FONT_BIG = Font(FONT_FAMILY, Font.BOLD, 16)

    FONT_WINDOW_BUTTONS = Font("sansserif", Font.BOLD, 16)
    FONT_XLARGE = Font(FONT_FAMILY, Font.BOLD, 22)
    FONT_XXLARGE = Font(FONT_FAMILY, Font.BOLD, 32)

    FONT_MENU_TITLE = Font(FONT_FAMILY, Font.BOLD, 13)
    FONT_MENU = Font(FONT_FAMILY, Font.BOLD, 12)

    # ## Search fonts
    FONT_SEARCH_TEXT = Font(FONT_FAMILY, Font.BOLD, 30)
    FONT_SEARCH_RESULT_COUNT = Font(FONT_FAMILY, Font.BOLD, 22)

    def applyStyle(self, item):
        if isinstance(item, JComponent):
            item.border = None
            item.background = self.COLOR_BACKGROUND
            item.foreground = self.COLOR_FOREGROUND
        elif isinstance(item, Container):
            item.background = self.COLOR_BACKGROUND
            item.foreground = self.COLOR_FOREGROUND
        elif isinstance(item, DefaultTreeCellRenderer):
            item.backgroundNonSelectionColor = self.COLOR_BACKGROUND
            item.backgroundSelectionColor = self.COLOR_BACKGROUND2
            item.textNonSelectionColor = self.COLOR_FOREGROUND
            item.textSelectionColor = self.COLOR_FOREGROUND

    def applyMenuStyle(self, item, is_title):
        item.opaque = True
        # item.border = None
        item.background = self.COLOR_BACKGROUND
        item.foreground = self.COLOR_FOREGROUND
        if is_title:
            item.font = self.FONT_MENU_TITLE
        else:
            item.font = self.FONT_MENU

    def createFont(self, size, bold=False):
        weight = Font.PLAIN
        if bold:
            weight = Font.BOLD
        return Font(self.FONT_FAMILY, weight, size)

    @staticmethod
    def colorAdd(c1, c2):
        r = min(c1.red + c2.red, 255)
        g = min(c1.green + c2.green, 255)
        b = min(c1.blue + c2.blue, 255)
        return Color(r, g, b)

    @staticmethod
    def colorScale(c, scale):
        r = min(int(round(c.red * scale)), 255)
        g = min(int(round(c.green * scale)), 255)
        b = min(int(round(c.blue * scale)), 255)
        return Color(r, g, b)
