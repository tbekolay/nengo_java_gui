from .configuration import uienvironment, nengoinstance

# import ca.nengo.ui.lib.world.piccolo.WorldObjectImpl;

from edu.umd.cs.piccolo.activities import PActivity, PInterpolatingActivity


class Pulsator(object):
    """Pulsates the target World Object until finished."""
    PULSATION_RATE_PER_SEC = 1
    PULSATION_STATE_TRANSITION = 1000 / (PULSATION_RATE_PER_SEC * 2)

    def __init__(self, target):
        self.target = target
        self.original_transparency = self.target.transparency
        self.pulsating = True
        self.fade_activity = None
        self.fader_delegate = FaderDelegate(self)
        self.direction = 'out'
        self.pulsate()

    def pulsate(self):
        if self.pulsating:
            assert (self.fade_activity is None
                    or self.fade_activity.isStepping(),
                    "activities are overlapping")

            if self.direction == 'in':
                self.direction = 'out'
                self.fade_activity = Fader(
                    self.target, Pulsator.PULSATION_STATE_TRANSITION, 1.)
            elif self.direction == 'out':
                self.direction = 'in'
                self.fade_activity = Fader(
                    self.target, Pulsator.PULSATION_STATE_TRANSITION, 0.)
            else:
                assert False, "Unsupported operation"

            self.fade_activity.delegate = self.fader_delegate
            nengoinstance.addActivity(self.fade_activity)

    def finish(self):
        self.is_pulsating = False
        self.fade_activity.terminate(PActivity.TERMINATE_AND_FINISH)
        self.target.transparency = self.original_transparency


class FaderDelegate(PActivity.PActivityDelegate):
    def __init__(self, pulsator):
        PActivity.PActivityDelegate.__init__(self)
        self.pulsator = pulsator

    def activityFinished(self, activity):
        self.pulsator.pulsate()

    def activityStarted(self, activity):
        pass

    def activityStepped(self, activity):
        pass


class Fader(PInterpolatingActivity):
    """Activity which gradually changes the transparency of a node"""

    def __init__(self, target, duration, end_transparency):
        PInterpolatingActivity.__init__(self, duration,
            int(1000 / uienvironment['ANIMATION_TARGET_FRAME_RATE']))
        self.target = target
        self.start_transparency = None
        self.end_transparency = end_transparency

    def activityStarted(self):
        self.start_transparency = self.target.transparency

    def getRelativeTargetValue(self):
        return self.target.transparency

    def setRelativeTargetValue(self, zeroToOne):
        self.super__setRelativeTargetValue(zeroToOne)
        transparency = self.start_transparency + (
            (self.end_transparency - self.start_transparency) * (zeroToOne))
        self.target.transparency = transparency

    relativeTargetValue = property(getRelativeTargetValue,
                                   setRelativeTargetValue)
