from javax.swing import JOptionPane, JScrollPane, JTextArea

from .configuration import nengoinstance

import traceback


def showDialog(msg, title, parent=nengoinstance):
    JOptionPane.showMessageDialog(parent, msg, title,
                                  JOptionPane.INFORMATION_MESSAGE)


def showText(msg, title, msgtype=JOptionPane.PLAIN_MESSAGE,
             parent=nengoinstance):
    editor = JTextArea(30, 50, editable=False, caretPosition=0)
    editor.text = msg
    JOptionPane.showMessageDialog(parent, JScrollPane(editor),
                                  title, msgtype)


def showWarning(msg, title="Warning", parent=nengoinstance):
    JOptionPane.showMessageDialog(parent, msg, title,
                                  JOptionPane.WARNING_MESSAGE)


def showError(msg, parent=nengoinstance):
    JOptionPane.showMessageDialog(parent, "<HTML>" + msg + "</HTML>", "Error",
                                  JOptionPane.ERROR_MESSAGE)
    traceback.print_stack()


def askDialog(msg, parent=nengoinstance):
    return JOptionPane.showInputDialog(parent, msg)
