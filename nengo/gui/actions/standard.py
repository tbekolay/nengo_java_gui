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


package ca.nengo.ui.lib.objects.activities;

import javax.swing.SwingUtilities;

import ca.nengo.ui.lib.actions.StandardAction;
import ca.nengo.ui.lib.world.piccolo.WorldObjectImpl;
import ca.nengo.ui.NengoGraphics;


class TrackedAction(StandardAction):
    """An action which is tracked by the UI.

    Since tracked actions are slow and have UI messages associated with them,
    they do never execute inside the Swing dispatcher thread.

    """

    def __init__(self, name, wo):
        StandardAction.__init__(self, name, None, False)
        self.taskName = name
        self.trackedMsg = None
        self.wo = wo

    def setTrackedMsg(self):
        self.trackedMsg = TrackedStatusMsg(self.taskName, self.wo)

    def doAction(self):
        SwingUtilities.invokeLater(make_runnable(self.setTrackedMsg))
        nengoinstance.progressIndicator.start(self.taskName)
        StandardAction.doAction(self)

    def doActionInternal(self):
        nengoinstance.progressIndicator.setThread()
        StandardAction.doActionInternal(self)

    def postAction(self):
        StandardAction.postAction()
        nengoinstance.progressIndicator.stop()
        SwingUtilities.invokeLater(make_runnable(self.trackedMsg.finished))


#import ca.nengo.ui.lib.Style.NengoStyle;
#import ca.nengo.ui.lib.util.UIEnvironment;
#import ca.nengo.ui.lib.world.piccolo.WorldObjectImpl;
#import ca.nengo.ui.lib.world.piccolo.primitives.Text;

class TrackedStatusMsg(object):
    """Displays and removes a task message from the application status bar.

    """

    def __init__(self, name, wo=None):
        self.name = name
        self.wo = wo
        if self.wo is not None:
            self.text = Text(self.name)
            self.text.setPaint(NengoStyle.COLOR_NOTIFICATION)
            self.text.setOffset(0, -taskText.height)
            self.wo.addChild(self.text)
            self.name = wo.name + ": " + self.name
        nengoinstance.universe.addTaskStatusMsg(self.name)

    def finished(self):
        """Removes the task message from the application status bar."""
        nengoinstance.universe.removeTaskStatusMsg(self.name)
        if self.text is not None:
            self.text.removeFromParent()



#import java.util.ArrayList;
#import java.util.Iterator;
#import java.util.List;

#import javax.swing.JOptionPane;

#import ca.nengo.model.Node;
#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.actions.UserCancelledException;
#import ca.nengo.ui.lib.objects.models.ModelObject;
#import ca.nengo.ui.lib.util.UIEnvironment;
#import ca.nengo.ui.lib.world.WorldObject;

class ClearAllAction(StandardAction):
    def action(self):
        response = JOptionPane.showConfirmDialog(nengoinstance
                "Are you sure you want to remove all objects from Nengo?",
                "Clear all?", JOptionPane.YES_NO_OPTION)
        if response == 0:
            for model in nengoinstance.world.ground.children
                nengoinstance.removeNodeModel(model.model)

            # clear script console
            nengoinstance.scriptConsole.reset(False)
        else:
            raise UserCancelledException

#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;

class ConfigureAction(StandardAction):
    def __init__(self, model):
        self.model = model
        StandardAction.__init__(self, "Inspector")

    def action(self):
        nengoinstance.configureObject(self.model)


#import java.awt.geom.Point2D;
#import java.util.ArrayList;
#import java.util.Collection;

#import ca.nengo.model.Node;
#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.world.piccolo.WorldImpl;
#import ca.nengo.ui.models.UINeoNode;

class CopyAction(StandardAction):
    def __init__(self, description, nodeUIs):
        StandardAction.__init__(self, description)
        self.nodeUIs = nodeUIs

    def action(self):
        nodes = []
        offsets = []

        # compute the mean of all the nodes' positions
        averagePoint = [0.0, 0.0]
        for nodeUI in self.nodeUIs:
            averagePoint[0] += nodeUI.offset.x
            averagePoint[1] += nodeUI.offset.y
        averagePoint[0] /= len(self.nodeUIs)
        averagePoint[1] /= len(self.nodeUIs)

        world = None
        for nodeUI in self.nodeUIs:
            if world is None and nodeUI.world is not None:
                world = nodeUI.world

            try:
                nodes.append(nodeUI.model.clone())
                offsets.append(Point2D.Double(nodeUI.offset.x - averagePoint[0],
                                              nodeUI.offset.y - averagePoint[1]))
            except Exception, e:
                raise ValueError("Could not clone node", e)

        nengoinstance.clipboard.setContents(nodes, offsets, world)

    def processNodeUI(self, nodeUI):
        pass

#import ca.nengo.config.ui.NewConfigurableDialog;
#import ca.nengo.model.Node;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.actions.UserCancelledException;
#import ca.nengo.ui.lib.util.UIEnvironment;
#import ca.nengo.ui.models.NodeContainer;
#import ca.nengo.ui.models.NodeContainer.ContainerException;
#import ca.nengo.ui.models.UINeoNode;
#import ca.nengo.ui.models.nodes.UINodeViewable;

class CreateModelAdvancedAction(StandardAction):
    def __init__(self, container, objType):
        StandardAction.__init__(self, objType.simpleName)
        self.objType = objType
        self.container = container

    def action(self):
        obj = NewConfigurableDialog.showDialog(nengoinstance, objType, None)
        if obj is None:
            raise UserCancelledException
        elif isinstance(obj, Node):
            CreateModelAction.ensureNonConflictingName(node, container)
            nodeUI = container.addNodeModel(obj)
            if isinstance(nodeUI, UINodeViewable):
                nodeUI.openViewer()
        else:
            raise TypeError("Sorry we do not support adding that type of object yet")


#import java.awt.geom.Point2D;
#import java.util.ArrayList;
#import java.util.Collection;

#import ca.nengo.model.Node;
#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.world.piccolo.WorldImpl;
#import ca.nengo.ui.models.UINeoNode;

class CutAction(StandardAction):
    def __init__(self, description, nodeUIs):
        StandardAction.__init__(self, description)
        self.nodeUIs = nodeUIs

    def action(self):
        nodes = []
        offsets = []

        # compute the mean of all the nodes' positions
        averagePoint = [0.0, 0.0]
        for nodeUI in self.nodeUIs:
            averagePoint[0] += nodeUI.offset.x
            averagePoint[1] += nodeUI.offset.y
        averagePoint[0] /= len(self.nodeUIs)
        averagePoint[1] /= len(self.nodeUIs)

        world = None
        for nodeUI in self.nodeUIs:
            if world is None and nodeUI.world is not None:
                world = nodeUI.world

            try:
                nodes.append(nodeUI.model.clone())
                offsets.append(Point2D.Double(nodeUI.offset.x - averagePoint[0],
                                              nodeUI.offset.y - averagePoint[1]))
            except Exception, e:
                raise ValueError("Could not clone node", e)

        # This removes the node from its parent and externalities
        for nodeUI in self.nodeUIs:
            nodeUI.destroyModel()

        nengoinstance.clipboard.setContents(nodes, offsets, world)


#import java.util.Collection;

#import ca.nengo.model.SimulationMode;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.models.UINeoNode;

class DefaultModeAction(StandardAction):
    def __init__(self, description, nodeUIs):
        StandardAction.__init__(self, description)
        self.nodeUIs = nodeUIs

    def action(self):
        for nodeUI in self.nodeUIs:
            nodeUI.model.mode = SimulationMode.DEFAULT

class DirectModeAction(StandardAction):
    def __init__(self, description, nodeUIs):
        StandardAction.__init__(self, description)
        self.nodeUIs = nodeUIs

    def action(self):
        for nodeUI in self.nodeUIs:
            nodeUI.model.mode = SimulationMode.DIRECT


class RateModeAction(StandardAction):
    def __init__(self, description, nodeUIs):
        StandardAction.__init__(self, description)
        self.nodeUIs = nodeUIs

    def action(self):
        for nodeUI in self.nodeUIs:
            nodeUI.model.mode = SimulationMode.RATE

#import javax.swing.JFileChooser;

#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.world.piccolo.primitives.Text;
#import ca.nengo.ui.lib.world.piccolo.primitives.Universe;
#import com.itextpdf.text.pdf.PdfWriter;
#import com.itextpdf.text.Document;
#import com.itextpdf.text.DocumentException;
#import com.itextpdf.text.pdf.PdfTemplate;
#import com.itextpdf.text.pdf.PdfContentByte;

#import java.awt.Component;
#import java.awt.Graphics2D;
#import java.awt.geom.AffineTransform;
#import java.io.File;
#import java.io.FileOutputStream;
#import java.io.IOException;

class GeneratePDFAction(StandardAction):
    def action(self):
        name = "Nengo"

        fileChooser = JFileChooser()
        fileChooser.dialogTitle = "Save layout as PDF"
        fileChooser.selectedFile = File(name + ".pdf")

        ng = nengoinstance

        if fileChooser.showSaveDialog(ng) == JFileChooser.APPROVE_OPTION:
            file = fileChooser.selectedFile

            universe = ng.universe
            w = universe.size.width
            h = universe.size.height

            # Top of page method: prints to the top of the page
            pw = 550
            ph = 800

            # create PDF document and writer
            doc = Document()
            writer = PdfWriter.getInstance(doc, FileOutputStream(file))
            doc.open()

            cb = writer.directContent

            # create a template
            tp = cb.createTemplate(pw, ph)
            g2 = tp.createGraphicsShapes(pw, ph)

            # scale the template to fit the page
            at = AffineTransform()
            s = Math.min(pw / w, ph / h)
            at.scale(s, s)
            g2.transform = at

            # print the image to the template
            # turning off setUseGreekThreshold allows small text to print
            Text.useGreekThreshold = False
            universe.paint(g2)
            Text.useGreekThreshold = True
            g2.dispose()

            # add the template
            cb.addTemplate(tp, 20, 0)

            # clean up everything
            doc.close()

#import java.io.File;
#import java.io.IOException;

#import javax.swing.JFileChooser;

#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.actions.UserCancelledException;
#import ca.nengo.ui.lib.objects.activities.TrackedAction;
#import ca.nengo.ui.lib.util.UserMessages;
#import ca.nengo.ui.models.UINeoNode;

class GeneratePythonScriptTrackedAction(TrackedAction):
    def __init__(self, nontracked):
        self.nontracked = nontracked
        TrackedAction.__init__(self, "Generating Python script")

    def action(self):
        self.nontracked.saveSuccessful = self.nontracked.generateScript()


class GeneratePythonScriptAction(StandardAction):
    def __init__(self, nodeUI, blocking=True):
        StandardAction.__init__(self, "Generate script for " + nodeUI.name)
        self.fileobj = None  # File to be saved to
        self.nodeUI = nodeUI
        # Whether or not the last save attempt was successful.
        self.saveSuccessful = False
        self.blocking = blocking

    def action(self):
        self.saveSuccessful = false;
        returnVal = JFileChooser.CANCEL_OPTION

        NengoGraphics.FileChooser.selectedFile = File(
            self.nodeUI.fileName.replace(' ', '_').replace(".nef", "") + ".py")

        returnVal = NengoGraphics.FileChooser.showSaveDialog()

        if returnVal == JFileChooser.APPROVE_OPTION:
            file = NengoGraphics.FileChooser.selectedFile
            GeneratePythonScriptTrackedAction(self).doAction()
        else:
            raise UserCancelledException

    def generateScript(self):
        try:
            self.nodeUI.generateScript(self.fileobj)
        except IOException, e:
            UserMessages.showError("Could not generate script: " + e.toString())
            return False
        except OutOfMemoryError, e:
            UserMessages.showError("Out of memory, please increase memory size: " + e.toString())
            return False
        return True

#import java.io.File;
#import java.io.FileInputStream;
#import java.io.IOException;

#import javax.swing.JFileChooser;
#import javax.swing.SwingUtilities;

#import org.python.core.PyClass;
#import org.python.util.PythonInterpreter;
#import org.python.util.PythonObjectInputStream;

#import ca.nengo.model.Node;
#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.objects.activities.TrackedAction;
#import ca.nengo.ui.lib.util.UserMessages;
#import ca.nengo.ui.models.NodeContainer;
#import ca.nengo.ui.models.NodeContainer.ContainerException;
#import ca.nengo.ui.models.UINeoNode;
#import ca.nengo.ui.models.nodes.UINodeViewable;

class LoadNefFileAction(TrackedAction):
    def __init__(self, openaction):
        self.openaction = openaction
        TrackedAction.__init__(self, "Loading network")

    def action(self):
        if self.openaction.fileobj.name.endsWith(".py"):
            try:
                nengoinstance.progressIndicator.start("Running " + self.openaction.fileobj.path)
                nengoinstance.scriptConsole.addVariable("scriptname", self.openaction.fileobj.path)
                nengoinstance.pythonInterpreter.execfile(self.openaction.fileobj.path)
            except RuntimeException, e:
                if e.toString() == "ca.nengo.ui.util.ScriptInterruptException":
                    nengoinstance.progressIndicator.stop()
                    UserMessages.showDialog("Stopped", "Stopped opening " + self.openaction.fileobj.name)
                else:
                    UserMessages.showError("Runtime exception:<br>" + e)
                return

            try:
                # loading Python-based objects requires using a
                # PythonObjectInputStream from within a
                # PythonInterpreter.
                # loading sometimes fails if a new interpreter is
                # created, so
                # we use the one from the NengoGraphics.
                pi = nengographics.pythonInterpreter
                pi.set("___inStream", PythonObjectInputStream(FileInputStream(self.openaction.fileobj)))
                obj = pi.eval("___inStream.readObject()")
                objLoaded = obj.__tojava__(Class.forName("ca.nengo.model.Node"))
                pi.exec("del ___inStream")

                SwingUtilities.invokeLater(make_runnable(
                    lambda: self.openaction.processLoadedObject(objLoaded)))
            except IOException:
                UserMessages.showError("IO Exception loading file")
            except ClassNotFoundException, e:
                e.printStackTrace();
                UserMessages.showError("Class not found")
            except ClassCastException:
                UserMessages.showError("Incorrect file version")
            except OutOfMemoryError:
                UserMessages.showError("Out of memory loading file");
            except ImportError, e:
                if e.value == "no module named main":
                    UserMessages.showError("Error: this file was "
                        + "built using Python class definitions that "
                        + "cannot be found.<br>To fix this problem, "
                        + "make a 'main.py' file in 'simulator-ui/lib/Lib' "
                        + "<br>and place the required python class definitions "
                        + "inside.")
                elif e.value.startsWith("no module named "):
                    UserMessages.showError("Error: this file was "
                        + "built using Python class definitions in <br>a file "
                        + "named " + e.value.substring(16) + ", which"
                        + "cannot be found.<br>To fix this problem, please "
                        + "place this file in 'simulator-ui/lib/Lib'.")
                else:
                    UserMessages.showError("Python error interpretting file:<br>" + e)
            except AttributeError, e:
                attr = e.value.substring(value.lastIndexOf(' ') + 1)
                UserMessages.showError("Error: this file uses a Python "
                    + "definition of the class " + attr + ", but this definition "
                    + "cannot be found.<br>If this class was defined in a "
                    + "separate .py file, please place this file in "
                    + "'simulator-ui/lib/Lib'.<br>Otherwise, please place the "
                    + "class definition in 'simulator-ui/lib/Lib/main.py' "
                    + "and restart the simulator.")
            except Exception, e:
                UserMessages.showError("Python error interpretting file:<br>" + e)


class OpenNefFileAction(StandardAction):
    def __init__(self, nodeContainer):
        self.nodeContainer = nodeContainer
        self.fileobj = None

    def action(self):
        response = NengoGraphics.FileChooser.showOpenDialog()
        if response == JFileChooser.APPROVE_OPTION:
            self.fileobj = NengoGraphics.FileChooser.selectedFile
            LoadNefFileAction(self).doAction()

    def processLoadedObject(self, objLoaded):
        """Wraps the loaded object and adds it to the Node Container."""
        if isinstance(objLoaded, Node):
            nodeUI = self.nodeContainer.addNodeModel(objLoaded)
            if isinstance(nodeUI, UINodeViewable):
                nodeUI.openViewer()
        else:
            UserMessages.showError("File does not contain a Node")

#import java.awt.geom.Point2D;
#import java.util.ArrayList;

#import ca.nengo.model.Node;
#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.world.piccolo.WorldImpl;
#import ca.nengo.ui.models.NodeContainer;
#import ca.nengo.ui.models.NodeContainer.ContainerException;
#import ca.nengo.ui.util.NengoClipboard;

class PasteAction(StandardAction):
    def __init__(self, description, nodeContainer, fromTopMenu):
        StandardAction.__init__(self, description)
        self.nodeContainer = nodeContainer
        self.posX = None
        self.poxY = None
        self.fromTopMenu = False

    def action(self):
        clipboard = nengoinstance.clipboard
        if clipboard.hasContents():
            nodes = clipboard.contents
            offsets = clipboard.offsets

            for node, offset in zip(nodes, offsets):
                try:
                    CreateModelAction.ensureNonConflictingName(node, self.nodeContainer)
                    if self.posX is None or self.posY is None:
                        self.nodeContainer.addNodeModel(node, self.posX, self.posY)
                    else:
                        self.nodeContainer.addNodeModel(node, self.posX + offset.x, self.posY + offset.y)

                except ContainerException, e:
                    # Did the attempt to paste to the mouse location fail?
                    # If so, try to paste into the network that the clipboard contents came from
                    if self.fromTopMenu:
                        CreateModelAction.ensureNonConflictingName(node, clipboard.sourceWorld)
                        clipboard.sourceWorld.addNodeModel(node)
        else:
            raise ValueError("Clipboard is empty")

    def setPosition(self, x, y):
        self.posX = x
        self.posY = y

#import javax.swing.JDialog;

#import ca.nengo.math.Function;
#import ca.nengo.ui.configurable.ConfigException;
#import ca.nengo.ui.configurable.ConfigResult;
#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.descriptors.PFloat;
#import ca.nengo.ui.configurable.managers.ConfigManager;
#import ca.nengo.ui.configurable.managers.ConfigManager.ConfigMode;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.util.UIEnvironment;
#import ca.nengo.ui.util.DialogPlotter;

class PlotFunctionAction(StandardAction):
    """Plots a function node, which can contain multiple functions."""
    pEnd = PFloat("End")
    pIncrement = PFloat("Increment")
    pStart = PFloat("Start")
    propD = [pStart, pIncrement, pEnd]

    def __init__(self, name, func, dialogParent):
        StandardAction.__init__(self, "Plot function")
        self.name = name
        self.func = func
        self.dialogParent = dialogParent
        pStart.description = "Time (in seconds) to start the graph (usually 0)"
        pIncrement.description = "Resolution (in seconds) of the graph (usually 0.001)"
        pEnd.description = "Time (in seconds) of the end of the graph"

    def action(self):
        ConfigResult properties = ConfigManager.configure(propD,
            "Function Node plotter", nengoinstance, ConfigMode.TEMPLATE_NOT_CHOOSABLE)
        title = self.name + " - Function Plot"

        start = properties.getValue(pStart)
        end = properties.getValue(pEnd)
        increment = properties.getValue(pIncrement)

        if increment == 0:
            raise ValueError("Please use a non-zero increment")

        plotter = DialogPlotter(self.dialogParent)
        plotter.doPlot(self.func, start, increment, end, title + " ("
                       + self.func.class.simpleName + ")")


#import ca.nengo.math.Function;
#import ca.nengo.model.impl.FunctionInput;
#import ca.nengo.plot.Plotter;
#import ca.nengo.ui.configurable.ConfigException;
#import ca.nengo.ui.configurable.ConfigResult;
#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.descriptors.PFloat;
#import ca.nengo.ui.configurable.descriptors.PInt;
#import ca.nengo.ui.configurable.managers.ConfigManager;
#import ca.nengo.ui.configurable.managers.ConfigManager.ConfigMode;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.util.UIEnvironment;

class PlotFunctionNodeAction(StandardAction):
    pEnd = new PFloat("End");
    pIncrement = new PFloat("Increment");
    pStart = new PFloat("Start");
    # static final PropDescriptor pTitle = new PTString("Title");

    def __init__(self, name, actionName, fin):
        StandardAction.__init__(self, "Plot function input", actionName)
        self.name = name
        self.fin = fin
        self.pFunctionIndex = None

    def action(self):
        self.pFunctionIndex = PInt("Function index", 0, 0, self.fin.functions.length - 1)
        propDescriptors = [self.pFunctionIndex, self.pStart, self.pIncrement, self.pEnd]
        properties = ConfigManager.configure(propDescriptors,
            "Function plotter", nengoinstance, ConfigMode.TEMPLATE_NOT_CHOOSABLE)
        self.completeConfiguration(properties)

    def completeConfiguration(self, properties):
        title = self.name + " - Function Plot"

        functionIndex = properties.getValue(self.pFunctionIndex)
        start = properties.getValue(self.pStart)
        end = properties.getValue(self.pEnd)
        increment = properties.getValue(self.pIncrement)

        if increment == 0:
            raise ValueError("Cannot plot with infinite steps because step size is 0")

        functions = self.fin.functions

        if functionIndex >= len(functions):
            raise ValueError("Function index out of bounds")

        func = self.fin.functions[functionIndex]
        Plotter.plot(func, start, increment, end, title + " ("
                     + func.class.simpleName + ")")

#import ca.nengo.plot.Plotter;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.util.SpikePattern;

class PlotSpikePattern(StandardAction):
    """Action for Plotting the Spike Pattern."""

    def __init__(self, spikePattern):
        StandardAction.__init__(self, "Plot spike pattern", "Plot spikes")
        self.spikePattern = spikePattern

    def action(self):
        Plotter.plot(self.spikePattern)

#import ca.nengo.plot.Plotter;
#import ca.nengo.ui.configurable.ConfigException;
#import ca.nengo.ui.configurable.ConfigResult;
#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.descriptors.PFloat;
#import ca.nengo.ui.configurable.descriptors.PInt;
#import ca.nengo.ui.configurable.managers.ConfigManager.ConfigMode;
#import ca.nengo.ui.configurable.managers.UserConfigurer;
#import ca.nengo.ui.dataList.ProbePlotHelper;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.util.UIEnvironment;
#import ca.nengo.ui.lib.util.UserMessages;
#import ca.nengo.util.DataUtils;
#import ca.nengo.util.TimeSeries;

class PlotTimeSeries(StandardAction):
    """Action for Plotting with additional options."""

    def __init__(self, actionName, timeSeries, plotName, showUserConfigDialog,
                 defaultTau, defaultSubSampling):
        StandardAction.__init__(self, actionName)
        self.timeSeries = timeSeries
        self.showUserConfigDialog = showUserConfigDialog
        self.plotName = plotName + " [ " + timeSeries.name + " ]"
        self.tauFilter = defaultTau
        self.subSampling = defaultSubSampling

    def action(self):
        pTauFilter = PFloat("Time constant of display filter [0 = off]", self.tauFilter)
        pSubSampling = PInt("Subsampling [0 = off]", self.subSampling)

        if self.showUserConfigDialog:
            result = UserConfigurer.configure([pTauFilter, pSubSampling],
                                              "Plot Options",
                                              nengoinstance,
                                              ConfigMode.TEMPLATE_NOT_CHOOSABLE)

            tauFilter = result.getValue(pTauFilter)
            subSampling = result.getValue(pSubSampling)

            ProbePlotHelper.instance.defaultTauFilter = tauFilter
            ProbePlotHelper.instance.defaultSubSampling = subSampling

        timeSeriesToShow = timeSeries

        if subSampling != 0:
            timeSeriesToShow = DataUtils.subsample(timeSeriesToShow, subSampling)

        if tauFilter != 0:
            timeSeriesToShow = DataUtils.filter(timeSeriesToShow, tauFilter)

        Plotter.plot(timeSeriesToShow, self.plotName)


#import java.util.ArrayList;

#import javax.swing.JOptionPane;

#import ca.nengo.ui.lib.actions.UserCancelledException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.objects.models.ModelObject;
#import ca.nengo.ui.lib.util.UIEnvironment;

class RemoveModelAction(StandardAction):
    """Action for removing this UI Wrapper and the model."""

    def __init__(self, name, modelsToRemove):
        self.modelsToRemove = modelsToRemove
        StandardAction.__init__(self, "Remove " + "selection"
                                if len(modelsToRemove > 1)
                                else modelsToRemove[0].typeName, actionName)

    def action(self):
        response = JOptionPane.showConfirmDialog(nengoinstance,
            "Once an object has been removed, it cannot be undone.",
            "Are you sure?", JOptionPane.YES_NO_OPTION)
        if response == 0:
            for modelToRemove in self.modelsToRemove:
                modelToRemove.destroyModel()
            self.modelsToRemove = None
        else:
            raise UserCancelledException

#import java.util.Collection;

#import javax.swing.JOptionPane;

#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.objects.models.ModelObject;
#import ca.nengo.ui.lib.util.UIEnvironment;

class RemoveModelsAction(StandardAction):
    """Action for removing a collection of UI Wrappers and their models."""

    def __init__(self, objectsToRemove, typeName="Objects", showWarning=False):
        StandardAction.__init__(self, "Remove " + typeName + "s")
        self.objectsToRemove = objectsToRemove
        self.typeName = typeName
        self.showWarning = showWarning

    def action(self):
        if self.showWarning:
            response = JOptionPane.showConfirmDialog(nengoinstance,
                "Once these " + self.typeName
                + "s have been removed, it cannot be undone.", "Are you sure?",
                JOptionPane.YES_NO_OPTION)

        if response != 0:
            return

        try:
            for model in self.objectsToRemove:
                model.destroyModel()
        except Exception, e:
            raise ValueError("Could not remove all objects: " + e.getMessage(), e)

#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.world.WorldObject;

class RemoveObjectAction(StandardAction):
    """Action for removing this UI Wrapper and the model."""
    def __init__(self, name, objectToRemove):
        StandardAction.__init__(self, "Remove " + objectToRemove.name, name)
        self.objectToRemove = objectToRemove

    def action(self):
        self.objectToRemove.destroy()
        self.objectToRemove = None

#import org.python.util.PythonInterpreter;

#import ca.nengo.sim.Simulator;
#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.models.nodes.UINetwork;

class RunInteractivePlotsAction(StandardAction):
    def __init__(self, uiNetwork):
        StandardAction.__init__(self, "Run interactive plots", "Interactive Plots")
        self.uiNetwork = uiNetwork

    def action(self):
        simulator = uiNetwork.simulator
        pi = nengoinstance.pythonInterpreter

        simulator.resetNetwork(False, True)
        pi.set("_interactive_network", uiNetwork)
        pi.exec("import timeview")
        pi.exec("reload(timeview)")
        pi.exec("timeview.View(_interactive_network.model,ui=_interactive_network.viewerEnsured)")
        pi.exec("del _interactive_network")

#import javax.swing.SwingUtilities;

#import ca.nengo.model.SimulationException;
#import ca.nengo.sim.Simulator;
#import ca.nengo.sim.SimulatorEvent;
#import ca.nengo.sim.SimulatorListener;
#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.configurable.ConfigException;
#import ca.nengo.ui.configurable.ConfigResult;
#import ca.nengo.ui.configurable.ConfigSchemaImpl;
#import ca.nengo.ui.configurable.Property;
#import ca.nengo.ui.configurable.descriptors.PBoolean;
#import ca.nengo.ui.configurable.descriptors.PFloat;
#import ca.nengo.ui.configurable.managers.ConfigManager;
#import ca.nengo.ui.configurable.managers.ConfigManager.ConfigMode;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.objects.activities.TrackedAction;
#import ca.nengo.ui.lib.objects.activities.TrackedStatusMsg;
#import ca.nengo.ui.lib.util.UIEnvironment;
#import ca.nengo.ui.lib.util.UserMessages;
#import ca.nengo.ui.models.nodes.UINetwork;

class RunSimulatorAction(StandardAction):
    pEndTime = PFloat("End time");
    pShowDataViewer = PBoolean("Open data viewer after simulation")
    pStartTime = PFloat("Start time")
    pStepSize = PFloat("Step size")

    zProperties = ConfigSchemaImpl([
        RunSimulatorAction.pStartTime,
        RunSimulatorAction.pStepSize,
        RunSimulatorAction.pEndTime,
        RunSimulatorAction.pShowDataViewer
    ])

    def __init__(self, actionName, uiNetwork, startTime=None, endTime=None, stepTime=None):
        StandardAction.__init__(self, "Run simulator", actionName)
        self.uiNetwork = uiNetwork
        pStartTime.description = "Time (in seconds) of the start of the simulation (usually 0)"
        pStepSize.description = "Size (in seconds) of the simulation timestep (usually 0.001)"
        pEndTime.description = "Time (in seconds) of the end of the simulation"
        pShowDataViewer.description = "Whether to automatically display any Probed data after running the simulation"
        self.startTime = startTime
        self.endTime = endTime
        self.stepTime = stepTime
        self.showDataViewer = False
        self.configured = (self.startTime is not None
                           and self.endTime is not None
                           and self.stepTime is not None)

    def action(self):
        if not self.configured:
            properties = ConfigManager.configure(self.zProperties,
                self.uiNetwork.typeName, "Run " + self.uiNetwork.fullName,
                nengoinstance, ConfigMode.TEMPLATE_NOT_CHOOSABLE)

            self.startTime = properties.getValue(self.pStartTime)
            self.endTime = properties.getValue(self.pEndTime)
            self.stepTime = properties.getValue(self.pStepSize)
            self.showDataViewer = properties.getValue(self.pShowDataViewer)

            simulatorActivity = RunSimulatorActivity(self, self.startTime,
                self.endTime, self.stepTime, self.showDataViewer)
            simulatorActivity.doAction()

class RunSimulatorActivity(TrackedAction, SimulatorListener):
    """Activity which will run the simulation."""
    def __init__(self, action, start, end, step, showDataViewer):
        TrackedAction.__init__(self, "Simulation started")
        self.runsim = runsim
        self.start = start
        self.end = end
        self.step = step
        self.showDataViewer = showDataViewer
        self.currentProgress = 0
        self.progressMsg = None

    def action(self):
        simulator = self.runsim.uiNetwork.getSimulator();
        simulator.resetNetwork(False, True);
        simulator.addSimulatorListener(nengoinstance.progressIndicator)

        try:
            simulator.run(self.start, self.end, self.step)
        finally:
            simulator.removeSimulatorListener(nengoinstance.progressIndicator)

            nengoinstance.captureInDataViewer(self.runsim.uiNetwork.model)

            if self.showDataViewer:
                SwingUtilities.invokeLater(make_runnable(
                    lamdba: nengoinstance.setDataViewerVisible(True)))

    def setMsg(self):
        if self.progressMsg is not None:
            self.progressMsg.finished()
        self.progressMsg = TrackedStatusMsg(str(self.currentProgress * 100) + "%% - simulation running")

    def processEvent(self, event):
        """Track events from the simulator and show progress in the UI."""
        if event.type == SimulatorEvent.Type.FINISHED:
            if self.progressMsg is not None:
                SwingUtilities.invokeLater(make_runnable(self.progressMsg.finished))

        if event.progress - self.currentProgress > 0.01:
            self.currentProgress = event.progress
            SwingUtilities.invokeLater(make_runnable(self.setMsg))

#import java.io.File;
#import java.io.IOException;

#import javax.swing.JFileChooser;

#import ca.nengo.ui.NengoGraphics;
#import ca.nengo.ui.lib.actions.ActionException;
#import ca.nengo.ui.lib.actions.StandardAction;
#import ca.nengo.ui.lib.actions.UserCancelledException;
#import ca.nengo.ui.lib.objects.activities.TrackedAction;
#import ca.nengo.ui.lib.util.UserMessages;
#import ca.nengo.ui.models.UINeoNode;

class SaveNodeActivity(TrackedAction):
    def __init__(self, nontracked):
        self.nontracked = nontracked
        TrackedAction.__init__(self, "Saving model")

    def action(self):
        self.nontracked.saveSuccessful = self.nontracked.saveModel()


class SaveNodeAction(StandardAction):
    def __init__(self, nodeUI, blocking=True):
        StandardAction.__init__(self, "Save " + nodeUI.name)
        self.fileobj = None
        # If blocking, then saving occurs in the same thread before returning.
        # Important for saving on exit.
        self.blocking = blocking
        self.nodeUI = nodeUI

    def action(self):
        self.saveSuccessful = False
        returnVal = JFileChooser.CANCEL_OPTION

        NengoGraphics.FileChooser.selectedFile = File(nodeUI.fileName)
        returnVal = NengoGraphics.FileChooser.showSaveDialog()

        if returnVal == JFileChooser.APPROVE_OPTION:
            self.fileobj = NengoGraphics.FileChooser.selectedFile

            if self.blocking:
                self.saveSuccessful = self.saveModel()
            else:
                SaveNodeActivity(self).doAction()
        else:
            raise UserCancelledException

    def saveModel(self):
        try:
            self.nodeUI.saveModel(self.fileobj)
        except IOException, e:
            UserMessages.showError("Could not save file: " + e.toString())
            return False
        except OutOfMemoryError, e:
            UserMessages.showError("Out of memory, please increase memory size: " + e.toString())
            return False
        return True

#import ca.nengo.ui.lib.AppFrame;

class ExitAction(StandardAction):
    def __init__(self, appFrame, description):
        StandardAction.__init__(self, description)
        self.appFrame = appFrame

    def action(self):
        self.appFrame.exitAppFrame()

#import java.io.IOException;

#import javax.swing.JOptionPane;

#import ca.nengo.ui.lib.util.UIEnvironment;

class OpenURLAction(StandardAction):
    browsers = ["google-chrome", "chromium", "firefox", "opera", "konqueror"]

    def __init__(self, helpstring, url):
        StandardAction.__init__(self, "Open URL", helpstring)
        self.url = url

    def action(self):
        os = System.getProperty("os.name").toLowerCase()
        if os.startsWith("win"):
            Runtime.runtime.exec("rundll32 url.dll,FileProtocolHandler " + self.url)
        elif os.startsWith("mac"):
            Runtime.runtime.exec("open " + self.url)
        else:
            ran = False
            for browser in self.browsers:
                try:
                    if Runtime.runtime.exec(["which", browser]).waitFor() == 0:
                        Runtime.runtime.exec([browser, self.url])
                        ran = True
                        break
                except InterruptedException, e:
                    ran = False

            if not ran:
                JOptionPane.showMessageDialog(nengoinstance,
                    "Could not open browser automatically. "
                    + "Please navigate to" + self.url,
                    "URL can't be opened", JOptionPane.INFORMATION_MESSAGE)

#import java.util.Collection;

#import javax.swing.JOptionPane;

#import ca.nengo.ui.lib.objects.models.ModelObject;
#import ca.nengo.ui.lib.util.UIEnvironment;
#import ca.nengo.ui.lib.world.WorldObject;

class RemoveObjectsAction(StandardAction):
    def __init__(self, objectsToRemove, actionName):
        StandardAction.__init__(self, actionName)
        self.objectsToRemove = objectsToRemove

    def action(self):
        response = JOptionPane.showConfirmDialog(nengoinstance,
            "You are about to remove " + len(self.objectsToRemove) + " Objects.",
            "Continue?", JOptionPane.YES_NO_OPTION)

        if response == JOptionPane.YES_OPTION:
            for wo in self.objectsToRemove:
                if isinstance(wo, ModelObject):
                    # If it's a model, make sure that's destroyed as well
                    wo.destroyModel()
                else:
                    #* Just destroy the UI representation
                    wo.destroy()

#import ca.nengo.ui.lib.world.piccolo.WorldImpl;

class ZoomToFitAction(StandardAction):
    def __init__(self, actionName, world):
        StandardAction.__init__(self, "Zoom to fit", actionName)
        self.world = world

    def action(self):
        if self.world is not None:
            self.world.zoomToFit()


#import ca.nengo.ui.lib.AuxillarySplitPane;

class SetSplitPaneVisibleAction(StandardAction):
    def __init__(self, actionName, splitPane, visible):
        StandardAction.__init__(self, actionName)
        self.visible = visible
        self.splitPane = splitPane

    def action(self):
        self.splitPane.auxVisible = self.visible
