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

#import java.util.Vector;

#import ca.nengo.ui.lib.AppFrame;
#import ca.nengo.ui.lib.util.UserMessages;

class ReversableActionManager(object):
    """Manages reversable actions."""

    # Max number of undo steps to reference
    MAX_UNDO_ACTIONS = 5


    def __init__(self, parent):
        self.parent = parent
        self.reversibleActions = []
        self.undoStepCount = 0

    def updateParent(self):
        """Updates the application parent that reversable actions have changed."""
        self.parent.reversibleActionsUpdated()

    def addReversibleAction(self, action):
        while self.undoStepCount > 0:
            del self.reversibleActions[-1]
            self.undoStepCount -= 1
        self.reversibleActions.append(action)

        if len(self.reversibleActions) > self.MAX_UNDO_ACTIONS:
            self.reversibleActions[0].finalizeAction()
            del self.reversibleActions[0]
        self.updateParent()

    def canRedo(self):
        return self.undoStepCount > 0

    def canUndo(self):
        return len(self.reversibleActions) - self.undoStepCount > 0

    def getRedoActionDescription(self):
        if self.canRedo():
            return self.reversibleActions[-self.undoStepCount].description
        else:
            return "None"

    def getUndoActioNDescription(self):
        if self.canUndo():
            return self.reversibleActions[-1 - self.undoStepCount].description
        else:
            return "None"

    def redoAction(self):
        action = self.reversibleActions[-self.undoStepCount]
        self.undoStepCount -= 1
        action.doAction()
        self.updateParent()

    def undoAction(self):
        if self.canUndo():
            action = self.reversibleActions[-1 - self.undoStepCount]
            self.undoStepCount += 1
            action.undoAction()
        else:
            UserMessages.showError("Cannot undo anymore steps")
        self.updateParent()


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


# import java.util.Map.Entry;

# import ca.nengo.model.SimulationException;
# import ca.nengo.ui.lib.actions.ActionException;
# import ca.nengo.ui.lib.actions.ReversableAction;
# import ca.nengo.ui.models.UINeoNode;
# import ca.nengo.ui.models.nodes.widgets.UIProbe;

class AddProbeAction(ReversibleAction):
    def __init__(self, node, state):
        self.node = node
        self.state = state
        ReversibleAction.__init__(self.state.key + " - " + self.state.value)
        self.probeCreated = None

    def action(self):
        try:
            self.probeCreated = self.node.addProbe(self.state.key)
        except Exception, e:
            raise ValueError("Probe could not be added: " + e.message, True, e)

    def undo(self):
        self.node.removeProbe(self.probeCreated)

# import java.util.Collection;
# import java.util.HashMap;

# import javax.swing.JOptionPane;

# import ca.nengo.model.SimulationException;
# import ca.nengo.ui.lib.actions.ActionException;
# import ca.nengo.ui.lib.actions.ReversableAction;
# import ca.nengo.ui.lib.objects.models.ModelObject;
# import ca.nengo.ui.lib.util.UIEnvironment;
# import ca.nengo.ui.lib.util.UserMessages;
# import ca.nengo.ui.models.UINeoNode;
# import ca.nengo.ui.models.nodes.widgets.UIProbe;


class AddProbesAction(ReversibleAction):
    def __init__(self, nodes):
        ReversibleAction.__init__(self, "Add probes")
        self.createdProbes = {}
        self.nodes = nodes

    def action(self):
        stateName = JOptionPane.showInputDialog(nengoinstance,
                "State name to probe (Case Sensitive): ",
                "Adding probes", JOptionPane.QUESTION_MESSAGE)

        if stateName is not None and stateName != "":
            successCount = 0
            failed = 0

            for node in self.nodes:
                if isinstance(node, UINeoNode):
                    try:
                        probeCreated = node.addProbe(stateName)
                        self.createdProbes[node] = probeCreated
                        successCount += 1
                    except:
                        failed += 1

            if failed > 0:
                UserMessages.showWarning(successCount
                        + " probes were successfully added. <BR> However it was not added to "
                        + failed
                        + " nodes. The state name specified may not exist on those nodes.")

    def undo(self):
        for node in self.nodes:
            if isinstance(node, UINeoNode):
                node.removeProbe(self.createdProbes[node])


#import javax.swing.JOptionPane;
#import javax.swing.SwingUtilities;

#import ca.nengo.model.Node;
#import ca.nengo.model.StructuralException;
#import ca.nengo.ui.configurable.ConfigException;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.ReversableAction;
#import ca.nengo.ui.lib.actions.UserCancelledException;
#import ca.nengo.ui.lib.util.UIEnvironment;
#import ca.nengo.ui.lib.util.UserMessages;
#import ca.nengo.ui.models.NodeContainer;
#import ca.nengo.ui.models.NodeContainer.ContainerException;
#import ca.nengo.ui.models.UINeoNode;
#import ca.nengo.ui.models.constructors.AbstractConstructable;
#import ca.nengo.ui.models.constructors.ConstructableNode;
#import ca.nengo.ui.models.constructors.ModelFactory;
#import ca.nengo.ui.models.nodes.UINodeViewable;

class CreateModelAction(ReversibleAction):

    @staticmethod
    def ensureNonConflictingName(node, container):
        newName = node.name
        i = 0

        # Check if the name itself is valid
        while True:
            try:
                node.name = newName
                break
            except ValueError:
                newName = JOptionPane.showInputDialog(nengoinstance,
                        "Names cannot contain '.' or ':', please enter a new name", newName);
                if newName is None or newName == "":
                    raise UserCancelledException

        originalName = node.name

        while container.getNodeModel(newName) is not None:
            # Avoid duplicate names
            while container.getNodeModel(newName) is not None:
                i += 1
                newName = originalName + " (" + i + ")"
            newName = JOptionPane.showInputDialog(nengoinstance,
                    "Node already exists, please enter a new name", newName)

            if newName is None or newName == "":
                raise UserCancelledException

        node.name = newName

    def __init__(self, modeltype, container, constructable):
        ReversibleAction.__init__(self, "Create new " + modeltype, modeltype, False)
        self.container = container
        self.constructable = constructable
        self.nodeCreated = None

    def add_and_open(self):
        self.ensureNonConflictingName(self.node, self.container)
        try:
            nodeCreated = container.addNodeModel(self.node, self.posX, self.posY)
            if isinstance(nodeCreated, UINodeViewable):
                if not isinstance(nodeCreated, UINEFEnsemble):
                    nodeCreated.openViewer()
        except ContainerException, e:
            UserMessages.showWarning("Could not add node: " + e.getMessage())
        except UserCancelledException, e:
            e.defaultHandleBehavior()

    def action(self):
        node = ModelFactory.constructModel(constructable)
        if node is None:
            raise Exception("No model was created")
        elif isinstance(node, Node):
            SwingUtilities.invokeAndWait(make_runnable(self.add_and_open))
        else:
            raise Exception("Can not add model of the type: " + node.class.simpleName)

    def setPosition(self, x, y):
        self.posX = x
        self.posY = y

    def undo(self):
        if self.nodeCreated is not None:
            self.nodeCreated.destroy()

#import java.awt.geom.Point2D;

#import ca.nengo.ui.lib.misc.WorldLayout;
#import ca.nengo.ui.lib.world.World;
#import ca.nengo.ui.lib.world.WorldObject;


class LayoutAction(ReversibleAction):
    def __init__(self, world, description, actionName):
        ReversibleAction.__init__(self, description, actionName)
        self.world = world

    def action(self):
        self.savedLayout = WorldLayout("", self.world, False)
        self.applyLayout()

    def applyLayout(self):
        raise NotImplementedError

    def restoreNodePositions(self):
        for node in self.world.ground.children:
            savedPosition = self.savedLayout.getPosition(node)
            if savedPosition is not None:
                node.setOffset(savedPosition)

    def undo(self):
        self.restoreNodePositions()

