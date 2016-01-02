# constants.py
import os


command_not_found = "command not found"
containing_dir = os.path.expanduser("~/.linux-story")

content_dir = os.path.join(
    os.path.dirname(
        os.path.realpath(__file__)
    ), "content"
)


def cd_permission(directory):
    return "-bash: cd: {}: Permission denied".format(directory)


def ls_cannot_read(directory):
    return "ls: cannot open directory {}: Permission denied".format(directory)