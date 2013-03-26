from jip.embed import require
require('org.simplericity.macify:macify:1.6')

from java.lang import Runnable, System
from org.simplericity.macify.eawt import DefaultApplication

from .core import Nengo


class RunWrapper(Runnable):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.func(*self.args, **self.kwargs)

def start():
    System.setProperty("apple.laf.useScreenMenuBar", "true")
    System.setProperty("com.apple.mrj.application.apple.menu.about.name",
                       "Nengo")
    application = DefaultApplication()
    nengo = Nengo()
    nengo.application = application

if __name__ == '__main__':
    start()


"""Consider!!

from threading import Thread
import time

def make_imports():
    import unicodedata

background_import = Thread(target=make_imports)
background_import.start()

print "Do something else while we wait for the import"
for i in xrange(10):
    print i
    time.sleep(0.1)
print "Now join..."
background_import.join()

print "And actually use unicodedata"
import unicodedata
"""
