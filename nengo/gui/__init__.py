from jip.embed import require
require('org.simplericity.macify:macify:1.6')

from java.lang import System
from org.simplericity.macify.eawt import DefaultApplication

from .core import Nengo


def start():
    System.setProperty("apple.laf.useScreenMenuBar", "true")
    System.setProperty("com.apple.mrj.application.apple.menu.about.name",
                       "Nengo")
    application = DefaultApplication()
    nengo = Nengo()
    nengo.application = application

if __name__ == '__main__':
    start()
