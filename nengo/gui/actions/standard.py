from __future__ import with_statement

import java.io.Serializable
from java.lang import InterruptedException

from java.lang import ThreadDeath
import javax.swing.AbstractAction
import javax.swing.Action
import javax.swing.JMenuItem
from javax.swing import SwingUtilities

from .. import messages, RunWrapper

import threading


class StandardAction(java.io.Serializable):
    """A standard non-reversible action"""

    serialVersionUID = 20

    def __init__(self, action, name, description=None, spawn_thread=False):
        self.threadlock = threading.Lock()
        self.finished = False
        self.action = action

        self.name = name
        if description is None:
            self.description = name
        else:
            self.description = description
        self.enabled = True

        # If true, this action will spawn a new thread, which allows the
        # action to proceed without the blocking UI.
        # If false, this action will execute inside
        # the Swing Event dispatcher thread.
        self.spawn_thread = spawn_thread

    def blockUntilComplete(self):
        """Blocks the calling thread until this action is completed."""
        while not self.finished:
            with self.threadlock:
                try:
                    self.wait()
                except InterruptedException, e:
                    e.printStackTrace()
                    break

    def postAction(self):
        """A subclass may put something here to do after an action
        has completed successfully.

        """
        pass

    def doActionInternal(self):
        """Does the action"""
        try:
            try:
                self.action()
            # TODO Remove all thread.stop() and get rid of this
            except ThreadDeath, e:
                # NengoGraphics.getInstance().getProgressIndicator().stop()
                # UserMessages.showWarning("Interrupted action: Thread was forced to quit.")
                pass
            self.postAction()
        except Exception, e:
            e.printStackTrace()
            messages.showWarning("Could not perform action: " + e.toString())
        finally:
            self.finished = True
            with self.threadlock:
                self.notifyAll()

    def doAction(self):
        """Does the action layer, starts an appropriate thread"""
        if self.spawn_thread and SwingUtilities.isEventDispatchThread():
            threading.Thread(target=self.doActionInternal).start()
        elif self.spawn_thread or SwingUtilities.isEventDispatchThread():
            # In the thread we want to be
            self.doActionInternal()
        else:
            SwingUtilities.invokeLater(RunWrapper(self.doActionInternal))

    def doSomething(self, isUndo):
        # TODO: What the eff is this for?!
        pass

    def toSwingAction(self):
        return SwingAction(
            self.doAction,
            self.name,
            description=self.description,
            enabled=self.enabled,
            icon=None,
            need_event=False
        )


class SwingAction(javax.swing.AbstractAction):
    """Action which can be used by swing components."""
    serialVersionUID = 20

    def __init__(self, action, name,
                 description=None, enabled=True, icon=None, need_event=False):
        javax.swing.AbstractAction.__init__(self, name)
        self.action = action
        self.enabled = enabled
        self.icon = icon
        if icon is not None:
            self.setIcon(javax.swing.Action.SMALL_ICON, icon)
        if description is not None:
            self.description = description
            self.setText(javax.swing.Action.SHORT_DESCRIPTION, description)
        else:
            self.description = name
        self.name = name
        self.need_event = need_event

    def actionPerformed(self, actionevent):
        if self.needEvent:
            self.action(actionevent)
        else:
            self.action()

    def createMenuItem(self):
        return javax.swing.JMenuItem(self.name, actionListener=self,
                                     enabled=self.enabled)


class TargetAction(SwingAction):
    def actionPerformed(self, event):
        if self.needEvent:
            self.action(self.getTarget(), event)
        else:
            self.action(self.getTarget())


class DisabledAction(StandardAction):
    def __init__(self, description, disable_message):
        StandardAction.__init__(self, description)
        self.disable_message = disable_message
        self.enabled = False

    def action(self):
        messages.showWarning(self.disable_message)


