from javax.swing import SwingUtilities

from .. import messages, RunWrapper
from ..configuration import nengoinstance
from .standard import StandardAction

import threading
import weakref


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


class DragAction(ReversibleAction):
    """Action which allows the dragging of objects by the selection handler
    to be done and undone.

    NOTE: Special care is taken for Window objects. These objects maintain
    their own Window state, and are thus immune to this action handler's
    undo action.

    """

    serialVersionUID = 30

    def __init__(self, selected_nodes):
        ReversibleAction.__init__(self, "Drag operation")
        self.selected_nodes_ref = []
        self.object_states = weakref.WeakKeyDictionary()

        for node in selected_nodes:
            self.selected_nodes_ref.append(weakref.ref(node))
            self.object_states[node.parent] = node.offset

    @staticmethod
    def isObjectDragUndoable(obj):
        return not isinstance(obj, Window)

    def setFinalPositions(self):
        """Stores the final positions based on the node offsets.

        Called from selection handler after dragging has ended.

        """
        for ref in self.selected_nodes_ref:
            node = ref()
            if node is not None:
                state = self.object_states.get(node.parent, None)
                if state is not None:
                    state.setFinalState(node.parent, node.offset)

    def action(self):
        for ref in self.selected_nodes_ref:
            node = ref()
            if node is not None:
                state = self.object_states.get(node.parent, None)
                f_parent = state.finalParentRef.get()
                if f_parent is not None:
                    f_parent.addChile(node)
                    node.offset = state.finalOffset
                    try:
                        self.dropNode(node)
                    except:
                        self.undo()

    @staticmethod
    def dropNode(node):
        if ((hasattr(node, 'acceptTarget') and hasattr(node, 'justDropped'))
                or hasattr(node, 'droppedOnTargets')):
            world_layer = node.worldLayer

            all_targets = world_layer.findIntersectingNodes(
                node.localToGlobal(node.bounds))

            # Do not allow a Node to be dropped on a child of itself
            good_targets = [target for target in all_targets
                            if not node.isAncestorOf(target)]

            if hasattr(node, 'droppedOnTargets'):
                node.droppedOnTargets(good_targets)

            if hasattr(node, 'acceptTarget'):
                target = None
                for test_target in good_targets:
                    if node.acceptTarget(test_target):
                        target = test_target
                        break

                if target is None:
                    if node.acceptTarget(world_layer):
                        target = world_layer

                if target is not None:
                    position = target.globalToLocal(node.localToGlobal(0, 0))
                    node.offset = position
                    target.addChild(node)
                    node.justDropped()

    def undo(self):
        for ref in self.selected_nodes_ref:
            node = ref()
            if node is not None and self.isObjectDragUndoable(node):
                state = self.object_states.get(node.parent, None)
                i_parent = state.initialParentRef.get()
                if i_parent is not None:
                    i_parent.addChild(node)
                    node.offset = state.initialOffset
                    self.dropNode(node)

    @property
    def reversible(self):
        for ref in self.selected_nodes_ref:
            if ref() is not None and self.isObjectDragUndoable(ref()):
                return True
        return False


class ObjectState(object):
    """Stores UI state variables required to do and undo drag operations."""
    def __init__(self, parent, offset):
        self.initial_parent = parent
        self.final_parent = None
        self.initial_offset = offset
        self.final_offset = None

    def setFinalState(self, parent, offset):
        self.final_parent = parent
        self.final_offset = offset
