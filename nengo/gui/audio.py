#import javax.sound.sampled.*;

class Clicker(object):
    BUFFER_SIZE = 1000
    SAMPLE_RATE = 44100  # Hz

    def __init__(self):
        self.started = False
        self.line = None
        self.value = [None]
        self.targetBytesAvailable = 5000
        self.steps = 0

    def start(self):
        if self.started:
            return False
        format = AudioFormat(self.SAMPLE_RATE, 8, 1, False, True)
        info = DataLine.Info(SourceDataLine.class, format, self.BUFFER_SIZE)
        if not AudioSystem.isLineSupported(info):
            return False

        try:
            self.line = AudioSystem.getLine(info)
            self.line.open(format)
        except LineUnavailableException,  e:
            return False

        line.start()
        return True

    def set(self, b):
        avail = self.line.available()

        if avail < self.targetBytesAvailable:
            self.steps -= 1
        else:
            self.steps += 1

        self.steps = max(2, self.steps)
        self.steps = min(self.steps, self.BUFFER_SIZE - 1)

#        if (avail<=0) return;
#        int steps;

#        if (avail<100) {
#            steps=1;
#        } else if (avail>700) {
#            steps=100;
#        } else {
#            steps=(avail-100)/7+1;
#        }

#        steps=avail;
#        if (steps<0) steps=0;
#        if (steps>bufferSize) steps=bufferSize;
#        //System.err.println("steps: "+steps+"  avail: "+avail);

#        //value[bufferSize-1]=b;
        self.value[0] = b
#        line.write(value,0,(int)steps);

#        //line.write(value,(int)(bufferSize-steps),(int)steps);

    def stop(self):
        self.line.close()
