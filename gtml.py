#! /usr/bin/env python
#
# Program:      gtml
#
# Version:      3.6.1
#
# Description:  gtml is a program to manage groups of HTML files with
#               similar properties.
#
# Authors:      versions 1.0 to 2.3
#                   Gihan Perera <gihan@pobox.com>, First Step Communications
#               versions 3.0 to 3.5.3
#                   Bruno Beaufils <beaufils@lifl.fr>
#               version 3.5.4
#                   Andrew E. Schulman <schulman@users.sourceforge.net>
#               version 3.6.0+
#                   Kenneth J. Pronovici <pronovici@ieee.org>
#
# Documentation and updates for this program are available at:
#
#     https://github.com/pronovic/gtml
#
# Copying and Distribution:
#
# Copyright (C) 1996-1999 Gihan Perera
# Copyright (C) 1999 Bruno Beaufils
# Copyright (C) 2004 Andrew E. Schulman
# Copyright (C) 2022 Kenneth J. Pronovici
#
# This program is free software; you can redistribute it and/or  modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
# ----------------------------------------------------------------------------
import argparse

from os import environ

defines = {}
extensions = []


def Define(key, value):
    """
    Add a macro in the definition list.
    :param key:
    :param value:
    :return:
    """
    # Special macros.
    if (key == "__PYTHON__" or
            key == "__SYSTEM__" or
            key == "__NEWLINE__" or
            key == "__TAB__"):
        Warning("system macros unmodifiable `{}'".format(key))
        return

    if key == 'INCLUDE_PATH':
        includePath = value.split(':')

    if key == 'OUTPUT_DIR':
        outputDir = value

    if key == 'OPEN_DELIMITER':
        delim1 = value

    if key == 'CLOSE_DELIMITER':
        delim2 = value

    if key == 'ARGUMENT_SEPARATOR':
        argsep = value

    if key == 'EXTENSION':
        ext_target = value
        extensions.append(value)

    if key == 'DEBUG':
        debug = True

    if key == 'LANGUAGE':
        SetTimestamps()

    if value == '':
        value = "(((BLANK)))"

    defines[key] = value

def show_version():
    """
    Display the program's current version
    :return:
    """
    print ("""
GTML version 3.6.1 - python,
Copyright (C) 1996-1999 Gihan Perera
Copyright (C) 1999 Bruno Beaufils
Copyright (C) 2004 Andrew E. Schulman
Copyright (C) 2022 Kenneth J. Pronovici

GTML comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it
under the conditions defined in the GNU General Public License.
""")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        epilog=r"""
NOTES:
    Before processing command line arguments, gtml try to process project files
    `\${HOME}/.gtmlrc', `\${HOME}/gtml.conf', `./.gtmlrc' and `./gtml.conf' in
    this order, allowing one to add to/modify the default behavior of gtml.

    Exit status is 1 if errors have been encountered, and 0 if all was OK.""",
        formatter_class = argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-M',
                        nargs='?',
                        default='GNUmakefile',
                        help="""Do not produce output files but generate a makefile 
                                ready to create them with gtml. If no <file> is
                                given the generated file will be called `GNUmakefile'.""",
                        metavar='file')

    parser.add_argument('-D',
                        help='Define constant <macro> eventually defined by <definition>.',
                        metavar='macro[=definition]')

    parser.add_argument('-F',
                        help='Only process the specified file in the next project file.',
                        metavar='file')

    parser.add_argument('--version',
                        help="Show gtml's current version",
                        action='store_true')

    parser.add_argument('--silent',
                        help='Do not produce any output information during file processing.',
                        action='store_true')

    parser.add_argument('file',
                        nargs='+')

    args = parser.parse_args()

    if args.version:
        show_version()
        exit(0)

    for env_key in environ:
        Define(env_key, environ[env_key])
