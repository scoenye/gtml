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
import time

from os import environ, stat

be_silent = False
debug = False
line_counter = 0
defines = {}
extensions = []
stamp = ''
mstamp = ''
time_global = {}

def Notice(message):
    """
    Print a given message, as is, on the standard output if allowed.
    :param message:
    :return:
    """
    if not be_silent:
        print(message)

def Debug(message):
    """
    Print a debug information.
    :param message:
    :return:
    """
    if debug:
        print("########### {}".format(message))

def Warn(message):
    """
    Notice a given warning.
    :param message:
    :return:
    """
    if line_counter:
        Notice("    !!! Warning: lines {}: {}.".format(line_counter, message))
    else:
        Notice("    !!! Warning: {}.".format(message))

def SplitTime(time_stamp):
    """
    Split a given time into the following global printable values:

      $sec        Seconds, 00 - 59
      $min        Minutes, 00 - 59
      $hour       Hours, 00 - 23
      $wday       Day of the week, Sunday - Saturday
      $shortwday  First three letters of month name, Sun - Sat
      $mday       Day of the month, 1 - 31
      $mdayth     Day of the month with particuliar extension, 1st - 31th
      $mon        Month number, 1 - 12
      $monthname  Full month name, January - December
      $shortmon   First three letters of month name, Jan - Dec
      $year       Full year (e.g. 1996)
      $syear      Last two digits of year (e.g. 96)
    :param time_stamp: 
    :return: 
    """
    sec, min, hour, mday, mon, syear, wday, yday, isdst = time_stamp

    # Month and Weekdays are defined differently in each language.
    if GetValue("LANGUAGE") == "fr":
        Month = ["Janvier", "F�vrier", "Mars",
                 "Avril", "Mai", "Juin",
                 "Juillet", "Ao�t", "Septembre",
                 "Octobre", "Novembre", "D�cembre"]
        WeekDay = ["Dimanche", "Lundi", "Mardi",
                   "Mercredi", "Jeudi", "Vendredi", "Samedi"]
        if mday == 1:
            mdayth = "1er"
        else:
            mdayth = mday

    # "no" thanks to Helmers, Jens Bloch <Jens.Bloch.Helmers@dnv.com>
    elif GetValue("LANGUAGE") == "no":
        Month = ["januar", "februar", "mars",
                 "april", "mai", "juni",
                 "juli", "august", "september",
                 "oktober", "november", "desember"]
        WeekDay = ["S�ndag", "Mandag", "Tirsdag",
                   "Onsdag", "Torsdag", "Fredag", "L�rdag"]
        mdayth = mday + "."

    # "se" thanks to magog, <magog@swipnet.se>
    elif GetValue("LANGUAGE") == "se":
        Month = ["januari", "februari", "mars",
                 "april", "maj", "juni",
                 "juli", "augusti", "september",
                 "oktober", "november", "december"]
        WeekDay = ["S�ndag", "M�ndag", "Tisdag", "Onsdag",
                   "Torsdag", "Fredag", "L�rdag"]
        mdayth = mday  # XXX: Not verified

    # "it" thanks to Pioppo, <pioppo@4net.it>
    elif GetValue("LANGUAGE") == "it":
        Month = ["Gennaio", "Febbraio", "Marzo",
                 "Aprile", "Maggio", "Giugno",
                 "Luglio", "Agosto", "Settembre",
                 "Ottobre", "Novembre", "Dicembre"]
        WeekDay = ["Domenica", "Luned�", "Marted�", "Mercoled�",
                   "Gioved�", "Venerd�", "Sabato"]
        mdayth = mday

    # "nl" thanks to Gert-Jan Brink <gertjan@code4u.com>
    elif GetValue("LANGUAGE") == "nl":
        Month = ["januari", "februari", "maart",
                 "april", "mei", "juni",
                 "juli", "augustus", "september",
                 "oktober", "november", "december"]
        WeekDay = ["zondag", "maandag", "dinsdag", "woensdag",
                   "donderdag", "vrijdag", "zaterdag"]
        mdayth = mday

    # "de" thanks to Uwe Arzt <uwe.arzt@robots.de>
    elif GetValue("LANGUAGE") == "de":
        Month = ["Januar", "Februar", "M�rz",
                 "April", "Mai", "Juni",
                 "Juli", "August", "September",
                 "Oktober", "November", "Dezember"]
        WeekDay = ["Sonntag", "Montag", "Dienstag",
                   "Mittwoch", "Donnerstag", "Freitag", "Samstag"]
        mdayth = mday

    # "ie" thanks to Ken Guest <kengu@credo.ie>
    elif GetValue("LANGUAGE") == "ie":
        Month = ["En�ir", "Feabhra", "M�rta",
                 "Bealtaine", "Aibre�n", "Meitheamh",
                 "L�il", "L�nasa", "M�an Fomhair",
                 "Deireadh Fomhair", "Samhain", "M� na Nollaig"]
        WeekDay = ["Domhnach", "Luan", "M�irt",
                   "C�adaoin", "D�ardaoin", "Aoine", "Satharn"]
        mdayth = mday + "."

    # default is english.
    else:
        Month = ["January", "February", "March",
                 "April", "May", "June",
                 "July", "August", "September",
                 "October", "November", "December"]
        WeekDay = ["Sunday", "Monday", "Tuesday",
                   "Wednesday", "Thursday", "Friday", "Saturday"]
        mdayth = mday + "th"
        # from <agre3@ironbark.bendigo.latrobe.edu.au>
        if mday == 1 or mday == 21 or mday == 31:
            mdayth = mday + "st"
        if mday == 2 or mday == 22:
            mdayth = mday + "nd"
        if mday == 3 or mday == 23:
            mdayth = mday + "rd"

    time_global['sec']  = '{!02d}'.format(sec)
    time_global['min']  = '{!02d}'.format(min)
    time_global['hour'] = '{!02d}'.format(hour)

    time_global['wday'] = WeekDay[wday]    # from <agre3@ironbark.bendigo.latrobe.edu.au>
    time_global['shortwday'] = wday[:3]

    time_global['monthname'] = Month[mon]
    time_global['shortmon']  = time_global['monthname'][:3]

    year = syear + 1900
    time_global['year'] = year[:-2]
    time_global['syear'] = syear
    time_global['mday'] = mday
    time_global['mdayth'] = mdayth
    time_global['mon'] = mon + 1  # Because it starts from 0


def FormatTimestamp(format_str):
    """
    Returns a printable time/date string based on a given format string.

    The format string is passed in the variable $stamp, and the following
    substitutions are made in it:

      $ss         -> seconds
      $mm         -> minutes
      $hh         -> hour
      $Ddd        -> Short weekday name (Sun - Sat)
      $Day        -> full weekday name
      $dd         -> day of the month
      $ddth       -> day of the month with th extension
      $MM         -> month number (1 - 12)
      $Mmm        -> short month name (Jan - Dec)
      $Month      -> full month name
      $yyyy       -> full year (e.g. 1996)
      $yy         -> short year (e.g. 96)

    Make sure you call "SplitTime" first to initialise time global variables,
    i.e time to format. 
    :param format_str:
    :return: 
    """
    format_str = format_str.replace('$ss', time_global['sec'])
    format_str = format_str.replace('$mm', time_global['min'])
    format_str = format_str.replace('$hh', time_global['hour'])
    format_str = format_str.replace('$Ddd', time_global['shortwday'])
    format_str = format_str.replace('$Day', time_global['wday'])
    format_str = format_str.replace('$ddth', time_global['mdayth'])
    format_str = format_str.replace('$dd', time_global['mday'])
    format_str = format_str.replace('$MM', time_global['mon'])
    format_str = format_str.replace('$Month', time_global['monthname'])
    format_str = format_str.replace('$Mmm', time_global['shortmon'])
    format_str = format_str.replace('$yyyy', time_global['year'])
    format_str = format_str.replace('$yy', time_global['syear'])

    return format_str

def SetTimestamps(name=''):
    """
    Defines eventual timestamps macros.
    :param name: file name
    :return:
    """
    if stamp != "":
        SplitTime(time.localtime())
        Define("TIMESTAMP", FormatTimestamp(stamp))

    if mstamp != "" and name != "":
        SplitTime(time.localtime(stat(name).st_mtime))
        Define("MTIMESTAMP", FormatTimestamp(mstamp))

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
        Warn("system macros unmodifiable `{}'".format(key))
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
