from javax.swing import SwingUtilities

from .. import messages, RunWrapper
from ..configuration import nengoinstance
from .standard import StandardAction

import threading


class ReversibleAction(StandardAction):
    """"A reversible action than can be undone."""
    serialVersionUID = 30

    def __init__(self, *args, **kwargs):
        StandardAction.__init__(self, *args, **kwargs)
        # TODO: necessary? instanceof Reversible is better
        # self.reversible = True

    def undoInternal(self):
        """Handles exceptions from undo"""
        try:
            self.undo()
        except Exception, e:
            e.printStackTrace()
            messages.showWarning("Unexpected exception: " + e.toString())

    def finalizeAction(self):
        """Override this function if completing the action requires two stages.

        First stage does the action but it can still be undone (leaving some
        threads intact). This function is the second (optional stage). It
        completes the action in such a way that it cannot be undone.

        """
        pass

    def postAction(self):
        """Only add the action once to the Action manager."""
        if not self.finished and isinstance(self, ReversibleAction):
            SwingUtilities.invokeLater(RunWrapper(
                lambda: nengoinstance.actionManager.addReversibleAction(self)))

    def undo(self):
        """Returns whether the undo was successful."""
        raise NotImplementedError

    def undoAction(self):
        """Undo the action."""
        if not self.finished:
            messages.showError("Action was never done, so it can't be undone")
            return

        """Does the action layer, starts an appropriate thread"""
        if self.spawn_thread and SwingUtilities.isEventDispatchThread():
            threading.Thread(target=self.undoInternal).start()
        elif self.spawn_thread or SwingUtilities.isEventDispatchThread():
            # In the thread we want to be
            self.undoInternal()
        else:
            SwingUtilities.invokeLater(RunWrapper(self.undoInternal))
