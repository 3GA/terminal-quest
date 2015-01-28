#!/usr/bin/env python

# Spellbook.py
#
# Copyright (C) 2014 Kano Computing Ltd
# License: GNU General Public License v2 http://www.gnu.org/licenses/gpl-2.0.txt
#
# Author: Caroline Clark <caroline@kano.me>


import os
import sys
from gi.repository import Gtk, Gdk

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from linux_story.paths import common_media_dir


class Spellbook(Gtk.EventBox):

    SPELLBOOK_BORDER = 1
    SPELL_BORDER = 1
    CMD_HEIGHT = 80
    CMD_WIDTH = 80
    HEIGHT = 100
    number_of_spells = 3

    def __init__(self):
        self.stop = False

        # TODO: fix this, is hacky.
        # First time we launch the spellbook, we want to hide it
        self.first = True

        Gtk.EventBox.__init__(self)

        background = Gtk.EventBox()
        background.get_style_context().add_class("spellbook_background")

        self.grid = Gtk.Grid()
        self.add(background)
        background.add(self.grid)

        screen = Gdk.Screen.get_default()
        self.win_width = screen.get_width()
        self.win_height = screen.get_height()

        self.WIDTH = self.win_width / 2

        self.set_size_request(self.WIDTH, self.HEIGHT)

        self.__pack_locked_spells()

    def repack_spells(self, commands):
        '''Unpack the spellbook and recreates array of commands into
        spells, and packs them up in the spellbook
        '''

        self.__pack_spells(commands)
        if self.first:
            self.first = False
        else:
            self.show_all()

    def __create_spell(self, name, locked=False):
        '''Create the individual GUI for a spell
        '''

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_size_request(self.CMD_WIDTH, self.CMD_HEIGHT)
        box.set_margin_top(10)
        box.set_margin_left(10)
        box.set_margin_right(10)
        box.set_margin_bottom(10)

        icon_background = Gtk.EventBox()
        icon_background.get_style_context().add_class("spell_icon_background")
        box.pack_start(icon_background, False, False, 0)

        label_background = Gtk.EventBox()
        label_background.get_style_context().add_class("spell_label_background")

        if locked:
            filename = os.path.join(common_media_dir, "padlock.png")
            icon_background.get_style_context().add_class("locked")
            label_background.get_style_context().add_class("locked")

        else:
            filename = os.path.join(common_media_dir, name + ".png")

        icon = Gtk.Image.new_from_file(filename)
        icon_background.add(icon)

        box.pack_start(label_background, False, False, 0)

        label = Gtk.Label(name)
        label.get_style_context().add_class("spell_command")
        label.set_alignment(xalign=0.5, yalign=0.5)
        label_background.add(label)

        return box

    def __pack_spells(self, commands):
        '''Takes in the array of commands, and creates the spells and
        packs them into a grid.
        '''

        left = 0

        if commands:
            for command in commands:
                if (left + 1) * (self.CMD_WIDTH + 20) < self.win_width:
                    box = self.__create_spell(command)
                    child = self.grid.get_child_at(left, 0)
                    self.grid.remove(child)
                    self.grid.attach(box, left, 0, 1, 1)
                    left += 1

    def __pack_locked_spells(self):
        '''Fill up the rest of the spells with locked boxes
        '''

        left = 0

        while left < self.number_of_spells:
            locked_box = self.__create_spell("...", locked=True)
            self.grid.attach(locked_box, left, 0, 1, 1)
            left += 1
