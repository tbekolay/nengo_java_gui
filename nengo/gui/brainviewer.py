#import ca.nengo.ui.lib.world.WorldObject;
#import ca.nengo.ui.lib.world.handlers.AbstractStatusHandler;
#import ca.nengo.ui.lib.world.handlers.EventConsumer;
#import ca.nengo.ui.lib.world.piccolo.WorldGroundImpl;
#import ca.nengo.ui.lib.world.piccolo.WorldImpl;
#import ca.nengo.ui.lib.world.piccolo.WorldObjectImpl;
#import ca.nengo.ui.lib.world.piccolo.primitives.PXImage;
#import ca.nengo.ui.lib.world.piccolo.primitives.Text;
#import edu.umd.cs.piccolo.event.PDragSequenceEventHandler;
#import edu.umd.cs.piccolo.event.PInputEvent;

class BrainViewer(World):

    def __init__(self):
        World.__init__(self, "Brain View", BrainViewGround())
        self.statusBarHandler = None

        # getSky().setScale(2);
        # setBounds(parentToLocal(getFullBounds()));
        # addInputEventListener(new EventConsumer());

        # Old init()
        self.sideView = BrainSideImage()
        self.frontView = BrainFrontImage()
        self.topView = BrainTopImage()

        self.ground.addChild(BrainImageWrapper(self.sideView))
        self.ground.addChild(BrainImageWrapper(self.frontView))
        self.ground.addChild(BrainImageWrapper(self.topView))

    @property
    def zCoord(self):
        return self.topView.coord

    @property
    def yCoord(self):
        return self.frontView.coord

    @property
    def xCoord(self):
        return self.sideView.coord


class BrainViewGround(WorldGround):
    def layoutChildren(self):
        x = 0
        maxHeight = 0

        for wo in self.children:
            if wo.height > maxHeight:
                maxHeight = wo.height

        for wo in self.children:
            wo.setOffset(x, maxHeight - wo.height)
            x += wo.width + 10


class BrainImageWrapper(WorldObject):
    def __init__(self, brainImage):
        WorldObject.__init__(self)
        self.brainImage = brainImage
        self.addChild(WorldObject(PXImage(brainImage)))

        self.label = Text()
        self.addChild(self.label)
        self.updateLabel()

        self.addInputEventListener(EventConsumer())
        self.addInputEventListener(BrainImageMouseHandler())

        self.layoutChildren()
        self.setBounds(self.parentToLocal(self.fullBounds))
        # addChild(new Border(this, Style.COLOR_FOREGROUND));

    def updateLabel(self):
        self.label.text = self.brainImage.viewName + " ("
                          + self.brainImage.coordName + " coord: " 
                          + self.brainImage.coord + ")"

    def layoutChildren(self):
        WorldObject.layoutChildren(self)
        self.label.setOffset(0, self.brainImage.height + 10)


class BrainImageMouseHandler(PDragSequenceEventHandler):
    def __init__(self):
        PDragSequenceEventHandler.__init__(self)
        self.roundingError = 0.0

    def dragActivityStep(self, event):
        dx = (event.canvasPosition.x - self.mousePressedCanvasPoint.x) / 30.0
        dxInteger = int(dx)
        self.roundingError += dx - dxInteger

        if self.roundingError > 1:
            dxInteger += 1
            self.roundingError -= 1.0
        elif roundingError < -1:
            self.roundingError += 1.0
            dxInteger -= 1

        self.brainImage.coord = self.brainImage.coord() + dxInteger
        self.updateLabel()
        self.repaint()


class BrainViewStatusHandler(AbstractStatusHandler):
    def getStatusMessage(self, event):
        return "Z Coord: " + self.world.zCoord

#import java.awt.image.BufferedImage;
#import java.awt.image.ColorModel;
#import java.awt.image.DataBuffer;
#import java.awt.image.DataBufferByte;
#import java.awt.image.IndexColorModel;
#import java.awt.image.Raster;
#import java.awt.image.SampleModel;
#import java.awt.image.SinglePixelPackedSampleModel;
#import java.awt.image.WritableRaster;

class AbstractBrainImage2D(BufferedImage):
    brainColorModel = IndexColorModel(8, 256,
        [i * 0.8 for i in xrange(256)],
        [i * 0.8 for i in xrange(256)],
        [i * 1.0 for i in xrange(256)])

    @staticmethod
    def getBrainRaster(width, height):
        return Raster.createWritableRaster(
            AbstractBrainImage2D.getBrainSampleModel(width, height), None)

    @staticmethod
    def getBrainSampleModel(width, height):
        return SinglePixelPackedSampleModel(
            DataBuffer.TYPE_BYTE, width, height, [0xff])

    def __init__(self, width, height):
        BufferedImage.__init__(self.brainColorModel,
                               self.getBrainRaster(width, height),
                               False, None)
        self.imageWidth = width
        self.imageHeight = height

        imageWidth = width;
        imageHeight = height;
        self.coordDefault = 0
        self.coord = self.coordDefault

    def updateViewCoord(self):
        imageArray = [0.0 for _ in xrange(self.imageHeight * self.imageWidth)]
        imageArrayIndex = 0
        for imageY in xrange(self.imageHeight - 1, -1, -1):
            for imageX in xrange(self.imageWidth):
                # image.getRaster().setPixel(x, y, new int[] { 0 });
                imageArray[imageArrayIndex] = self.getImageByte(imageX, imageY)
                imageArrayIndex += 1

        buffer = DataBufferByte(imageArray, len(imageArray), 0)
        self.data = Raster.createWritableRaster(
            self.getBrainSampleModel(width, height), buffer, None)

    @property
    def coordMax(self):
        raise NotImplementedError

    @property
    def coordMin(self):
        raise NotImplementedError

    @property
    def coord(self):
        return self.viewCoord

    @coord.setter
    def coord(self, coord):
        coord = min(coord, self.coordMax)
        coord = max(coord, self.coordMin)
        self.viewCoord = coord
        self.updateViewCoord()

    def getImageByte(self, x, y):
        raise NotImplementedError

    @property
    def viewName(self):
        raise NotImplementedError

    @property
    def coordName(self):
        raise NotImplementedError

#import java.awt.Canvas;
#import java.awt.Component;
#import java.awt.Frame;
#import java.awt.Graphics;
#import java.awt.event.ComponentAdapter;
#import java.awt.event.ComponentEvent;
#import java.io.File;
#import java.io.FileInputStream;
#import java.io.FileNotFoundException;
#import java.io.IOException;


class BrainFrontImage(AbstractBrainImage2D):
    def __init__(self):
        AbstractBrainImage2D.__init__(BrainData.X_DIMENSIONS,
                                      BrainData.Z_DIMENSIONS)

    @property
    def coordMax(self):
        return len(BrainData.voxelData[0]) - BrainData.Y_START - 1

    @property
    def coordMin(self)
        return -BrainData.Y_START

    def getImageByte(self, imageX, imageY):
        return BrainData.voxelData[imageY][self.coord + BrainData.Y_START][imageX]

    @property
    def coordName(self):
        return "Y(mm)"

    @property
    def viewName(self):
        return "Front View"


class BrainSideImage(AbstractBrainImage2D):
    def __init__(self):
        AbstractBrainImage2D.__init__(BrainData.Y_DIMENSIONS,
                                      BrainData.Z_DIMENSIONS)

    @property
    def coordMax(self):
        return len(BrainData.voxelData[0][0]) - BrainData.X_START - 1

    @property
    def coordMin(self):
        return -BrainData.X_START

    def getImageByte(self, imageX, imageY):
        return BrainData.voxelData[imageY][imageX][self.coord + BrainData.X_START]

    @property
    def coordName(self):
        return "X(mm)"

    @property
    def viewName(self):
        return "Side View"


class BrainTopImage(AbstractBrainImage2D):
    def __init__(self):
        AbstractBrainImage2D.__init__(BrainData.X_DIMENSIONS,
                                      BrainData.Y_DIMENSIONS)

    @property
    def coordMax(self):
        return len(BrainData.voxelData) - BrainData.Z_START - 1

    @property
    def coordMin(self):
        return -BrainData.Z_START

    def getImageByte(self, imageX, imageY):
        return BrainData.voxelData[self.coord + BrainData.Z_START][imageY][imageX]

    @property
    def coordName(self):
        return "Z(mm)"

    @property
    def viewName(self):
        return "Top View"


class BrainData(object):
    X_DIMENSIONS = 181
    Y_DIMENSIONS = 217
    Z_DIMENSIONS = 181
    X_START = 72
    Y_START = 126
    Z_START = 90

    DATA_FILE_NAME = "t1_icbm_normal_1mm_pn3_rf20.rawb"
    DATA_FOLDER = "data"
    DATA_FILE = File(BrainData.DATA_FOLDER, BrainData.DATA_FILE_NAME);

    VOXEL_DATA = None

    @staticmethod
    def processFile():
        if BrainData.VOXEL_DATA is not None:
            return

        BrainData.VOXEL_DATA = [[0 for _ in xrange(BrainData.Z_DIMENSIONS)]
                                for _ in xrange(BrainData.Y_DIMENSIONS)]]

        try:
            fileStream = FileInputStream(BrainData.DATA_FILE)

            for zIndex in xrange(BrainData.Z_DIMENSIONS):
                for yIndex in xrange(BrainData.Y_DIMENSIONS):
                    fileStream.read(VOXEL_DATA[zIndex][yIndex])

            if fileStream.available() != 0:
                raise IOException("File size incorrect, does not match data dimensions")
            fileStream.close();
        except Exception, e:
            e.printStackTrace()

BrainData.processFile()

class BrainTestResized(ComponentAdapter):
    def componentResized(self, event):
        event.source.repaint()


class BrainTestCanvas(Canvas):
    def __init__(self):
        self.image = BrainTopImage())
        self.addComponentListener(BrainTestResized())

    @imagePosition.setter
    def imagePosition(self, zCoord):
        self.image.coord = zCoord
        self.repaint()

    def paint(self, g):
        if self.image is not None:
            g.drawImage(self.image, 0, 0, None)


if __name__ == '__main__':
    canvas = BrainTestCanvas()
    frame = Frame("BrainView")
    frame.add(canvas)
    frame.setSize(300, 200)
    frame.setVisible(True)

    for i in range(-50, 51):
        canvas.imagePosition = i
        time.sleep(0.025)
