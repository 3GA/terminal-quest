# introduction.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A chapter of the story


import os

from linux_story import KanoCmd
from linux_story.IStep import IStep


class StepTemplateLs(IStep):
    TerminalClass = KanoCmd


# ----------------------------------------------------------------------------------------


class Step1(StepTemplateLs):
    story = [
        _("Hello {}.").format("{{yb:" + os.environ['LOGNAME'] + "}}"),
        _("Welcome to the dark side of your Kano."),
        _("You've entered a perilous world where words wield power."),
        _("Ready? Press {{gb:Enter}} to begin.")
    ]
    start_dir = "~/my-house/my-room"
    end_dir = "~/my-house/my-room"

    def next(self):
        return 1, 1
