# MainWindow.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
import os
import time
from gi.repository import Gtk, Gdk, Pango

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from linux_story.dependencies import load_app_state_variable, Logger, apply_styling_to_screen, \
    ScrolledWindow
from linux_story.gtk3.TerminalUi import TerminalUi
from linux_story.gtk3.Spellbook import Spellbook
from linux_story.gtk3.Storybook import Storybook
from linux_story.common import css_dir
from linux_story.gtk3.MenuScreen import MenuScreen
from linux_story.load_defaults_into_filetree import revert_to_default_permissions


def save_point_exists():
    return load_app_state_variable('linux-story', 'level')


def user_used_echo(data_dict):
    return "print_text" in data_dict and data_dict["print_text"]


class MainWindow(Gtk.Window):

    CSS_FILE = os.path.join(css_dir, "style.css")
    COLOUR_CSS_FILE = os.path.join(css_dir, "colours.css")

    def __init__(self, queue, debug, challenge, step):
        Gtk.Window.__init__(self)

        self.__queue = queue

        apply_styling_to_screen(self.CSS_FILE)
        apply_styling_to_screen(self.COLOUR_CSS_FILE)

        self.__debug = debug
        self.__setup_gtk_properties()
        self.__setup_keymap()
        self.is_busy = False

        if challenge and step:
            self.__start_game_from_challenge(challenge, step)
        elif save_point_exists():
            self.__show_menu()
        else:
            self.__start_game_from_challenge("0", "1")

    def set_theme(self, dark=False):
        if dark:
            self.__set_dark_theme()
        else:
            self.__set_normal_theme()

    def __set_dark_theme(self):
        style_context = self.get_style_context()
        if "dark" not in style_context.list_classes():
            self.get_style_context().add_class("dark")
        self.__spellbook.set_dark_theme()
        self.__terminal.set_dark_theme()
        self.__story.set_dark_theme()

    def __set_normal_theme(self):
        style_context = self.get_style_context()
        if "dark" not in style_context.list_classes():
            style_context.remove_class("dark")
        self.__spellbook.set_normal_theme()
        self.__terminal.set_normal_theme()
        self.__story.set_normal_theme()

    def __setup_gtk_properties(self):
        self.connect('delete-event', self.__close_window)
        self.get_style_context().add_class("main_window")
        self.maximize()
        self.set_title("Terminal Quest")
        self.set_icon_name("linux-story")

    def __setup_keymap(self):
        keymap = Gdk.Keymap.get_for_display(self.get_display())
        keymap.connect('state-changed', self.__on_keymap_state_changed)
        self.__is_caps_lock_on = keymap.get_caps_lock_state()

    def __on_keymap_state_changed(self, keymap=None):
        is_caps_lock_on = keymap.get_caps_lock_state()

        if self.__is_caps_lock_on != is_caps_lock_on:
            self.__is_caps_lock_on = is_caps_lock_on
            self.on_caps_lock_changed(is_caps_lock_on)

    def __start_game_from_challenge(self, challenge, step):
        self.__setup_application_widgets()
        self.__start_script_in_terminal(challenge, step)
        self.show_all()
        if False:
            self.__terminal.hide()
            self.__spellbook.hide()

    def __show_menu(self):
        menu = MenuScreen()
        menu.connect('challenge_selected', self.__replace_widget_with_challenge)
        self.add(menu)
        self.show_all()

    def __setup_application_widgets(self):
        screen = Gdk.Screen.get_default()
        width = screen.get_width()
        height = screen.get_height()

        self.__terminal = TerminalUi()
        self.__spellbook = Spellbook(is_caps_lock_on=self.__is_caps_lock_on)
        self.__story = Storybook(
            width / 2 - 40,
            height - self.__spellbook.HEIGHT - 2 * 44 - 10
        )

        self.hbox = Gtk.Box()

        story_sw = ScrolledWindow()
        story_sw.apply_styling_to_screen()
        story_sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        story_sw.add(self.__story)

        left_background = Gtk.EventBox()
        left_background.get_style_context().add_class("story_background")
        left_background.add(story_sw)

        right_background = Gtk.EventBox()
        right_background.get_style_context().add_class("terminal_background")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        vbox.pack_start(self.hbox, False, False, 0)
        vbox.pack_start(self.__spellbook, False, False, 0)
        self.hbox.pack_start(left_background, False, False, 0)
        self.hbox.pack_start(right_background, False, False, 0)

        right_background.add(self.__terminal)

        # Allow for margin on bottom and top bar.
        self.__terminal.set_size_request(
            width / 2 - 20, height - self.__spellbook.HEIGHT - 2 * 44 - 20
        )
        story_sw.set_size_request(
            width / 2 - 20, height - self.__spellbook.HEIGHT - 2 * 44 - 10
        )

    def on_caps_lock_changed(self, is_caps_lock_on):
        if self.__spellbook:
            self.__spellbook.caps_lock_changed(is_caps_lock_on)

    def __start_script_in_terminal(self, challenge_number="", step_number=""):
        '''
        This function currently creates the thread that runs the
        storyline in the TerminalUi class and attaches an event listener
        to update the UI when the queue is updated.

        Args:
            challenge_number (str): The challenge number of the challenge that
                                    we want to start from.
            step_number (str): The step number of the challenge that
                               we want to start from.

        Returns:
            None
        '''

        if os.path.dirname(__file__).startswith('/usr'):
            filepath = '/usr/bin/linux-story'
        else:
            filepath = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../../bin/linux-story"
                )
            )

        command = (
            "python " +
            filepath + " " +
            challenge_number + " " +
            step_number
        )

        self.__terminal.launch_command(command)

    def finish_app(self):
        self.__stop_typing_in_terminal()
        self.__center_storybook()
        # TODO: update asset when we finish the last chapter in the storyline
        self.__story.print_coming_soon(self, self.__terminal)
        time.sleep(5)
        self.__close_window()

    def show_hint(self, hint):
        self.__stop_typing_in_terminal()
        self.__story.type_coloured_text(hint)
        self.__show_terminal()

    def __show_terminal(self):
        self.__terminal.show_all()
        self.__terminal.set_sensitive(True)
        self.__terminal.grab_focus()

    def start_new_challenge(self, data_dict):
        self.__story.clear()
        self.__stop_typing_in_terminal()
        self.__story.print_challenge_title(data_dict['challenge'])
        if 'xp' in data_dict and data_dict['xp']:
            self.__show_earned_xp(data_dict['xp'])
        self.__show_echo_choice(data_dict)
        self.__story.type_coloured_text(data_dict['story'])
        self.__repack_spells(data_dict["spells"], data_dict["highlighted"])
        self.__show_terminal()
        self.show_all()

    def __stop_typing_in_terminal(self):
        self.__terminal.set_sensitive(False)

    def __show_earned_xp(self, xp):
        self.__story.type_coloured_text(xp)

    def __show_echo_choice(self, data_dict):
        if user_used_echo(data_dict):
            self.__story.print_coloured_text(data_dict["print_text"] + "\n\n")

    def __repack_spells(self, spells, highlighted_spells):
        self.__spellbook.repack_spells(spells, highlighted_spells)

    def __center_storybook(self):
        """
        Centers the StoryBook in the window by hiding the Terminal.
        """
        self.__terminal.hide()
        self.hbox.set_halign(Gtk.Align.CENTER)

    def __replace_widget_with_challenge(self, widget, challenge_number):
        """
        Remove the menu and launch the selected challenge.

        Args:
            widget (Gtk.Widget): The button that was clicked.
            challenge_number (int)
        """

        self.remove(widget)
        self.__start_game_from_challenge(str(challenge_number), "1")

    def __close_window(self, widget=None, event=None):
        """
        Shut the server down and kills the application.

        Args:
            widget (Gtk.Widget)
            event (Gdk.EventButton)

        Returns:
            None
        """
        revert_to_default_permissions()
        Gtk.main_quit()

