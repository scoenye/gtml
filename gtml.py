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
import os
import re
import subprocess
import time

from os import environ

ext_source  = [".gtm", ".gtml"]
ext_project = [".gtp"]
ext_target  = ".html"

delim1 = '<<'
delim2 = '>>'
argsep = ','

include_path = []

be_silent = False
debug = False
entities = True     # Convert HTML entities or not?
line_counter = 0
exit_status = 0
error_count = 0
defines = {}
characters = {}
file_aliases = {}
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

def Error(message):
    """
    Notice a given error.
    :param message:
    :return:
    """
    if line_counter:
        Notice("    *** Error: line {}: {}.".format(line_counter, message))
    else:
        Notice("    *** Error: {}}.".format(message))

    exit_status |= 2
    error_count += 1

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
        SplitTime(time.localtime(os.stat(name).st_mtime))
        Define("MTIMESTAMP", FormatTimestamp(mstamp))

def Define(key, value):
    """
    Add a macro in the definition list.
    :param key:
    :param value:
    :return:
    """
    global include_path

    # Special macros.
    if (key == "__PYTHON__" or
            key == "__SYSTEM__" or
            key == "__NEWLINE__" or
            key == "__TAB__"):
        Warn("system macros unmodifiable `{}'".format(key))
        return

    if key == 'INCLUDE_PATH':
        include_path = value.split(':')

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

def DefineFilename(key, value):
    """
    Add a file alias in the hash table of filename aliases.
    :param key:
    :param value:
    :return:
    """
    if value.startswith('/'):
        Error("no absolute file references allowed: {}".format(value))
        return

    file_aliases[key] = value
    Define(key, value)

def SetFileReferences():
    """
    Define the value of each filename aliases as macros.
    :return:
    """
    for alias in file_aliases:
        if GetValue("ROOT_PATH") == "(((BLANK)))":
            value = file_aliases[alias]
        else:
            value = GetValue("ROOT_PATH") + file_aliases[alias]

        value = ChangeExtension(value)
        Define(alias, value)

def GetValue(key):
    """
    Get the value of a specified macro.
    :param key:
    :return:
    """
    return defines[key]

def Undefine(key):
    """
    Remove a specified macro from the list of macros.
    :param key:
    :return:
    """
    del defines[key]
    del characters[key]

def Markup(statement, value):
    """
    Mark up a given definition in order to outline argument of a definition.
    :param statement:
    :param value:
    :return:
    """
    match = re.search(r'(.+)\((.+)\)', statement)     # statement(arg_list)

    if match:
        # Tag has parens: MACRO(x,y) ....x....y....
        statement = match.group(1)   # key is now just the command.
        arguments = match.group(2)   # the argument list that was part of key
        arg_list = arguments.split(argsep)

        start = 0   # Default next marker if the key is not yet defined.

        # Verify if key is not yet defined, if yes find last argument.
        old_value = GetValue(statement)

        if old_value != '':
            # Find rightmost occurrence of (((MARKERz)))
            last_arg = old_value[old_value.rfind("(((MARKER"):]

            level = re.match(r'\(\(\(MARKER([0-9])+\)\)\).*$', last_arg)
            if level:
                start = level.group(1) + 1          # Incoming argument will be old + 1

        # Markup argument
        for index, argument in enumerate(arg_list): # Go over all the statement's arguments
            pos = value.find(argument)      # Is the argument also in the value supplied to the function?
            length = len(argument)          # Can happen if ,, was in the statement arguments, but...

            # ... non-0 length requirement means ,, breaks the loop
            while pos >= 0 and length > 0:  # sensible argument, also present in the value parameter
                j = index + start           # New marker counter - does not change in this loop
                value[pos: pos+length] = "(((MARKER{})))".format(j) # Replace the argument value with the marker
                pos = value.find(argument)  # Replace remaining occurrences of the argument
                length = len(argument)      # with the same marker

    return statement, value

def Substitute(line):
    """
    Substitute all macros in a line read from the source file.
    :param line:
    :return: the line with all macros substituted
    """
    # HTML entities may be converted.
    if entities:
        # The default case: substitute '<', '&', and '>'.
        line = line.replace('&', '&amp;')
        line = line.replace('<', '&lt;')
        line = line.replace('>', '&gt;')

    # User-defined characters to be converted.
    for user_char in characters:
        line.replace(user_char, characters[user_char])

    # Macros have to be replaced by their values.
    # __NEWLINE__ and __TAB__ are substitute after all others.
    special = delim1 + '__NEWLINE__' + delim2
    line.replace(special, '__NEWLINE__')

    special = delim1 + '__TAB__'  + delim2
    line.replace(special, '__TAB__')

    l1 = len(delim1)
    l2 = len(delim2)

    more = True

    while more:
        p2 = line.find(delim2)              # Leftmost occurrence of >>, -1 if not found
        p1 = line.rfind(delim1, 0, p2)      # Locate the matching <<, before the >> found above.

        if p2 >= l1:                        # p2 == l1 for <<>>
            key = line[p1+l1, p2-p1-l2]

            if re.search(r'^[^ \t]+[ \t]*\(.*\)$', key):
                # Tag contains a keyword and arguments.
                key, argument = key.split('(', maxsplit=1)
                argument = re.sub(r'\)$', '', argument)
                args_list = SplitArgs(argument)

            if key == "__PYTHON__":
                value = eval(args_list[0])
            elif key == "__SYSTEM__":
                value = subprocess.check_output(args_list[0])
            else:
                value = defines[key]

                for i in range(len(args_list)):
                    # Argument substitution.
                    marker = '(((MARKER{})))'.format(i)
                    marker_location = value.find(marker)
                    while marker_location != -1:
                        # Substitution template contains a replacement marker.
                        length = len(marker)
                        value[marker_location:marker_location+length] = args_list[i]
                        marker_location = value.find(marker)

            # Make some verifications.
            if value == '' and not (key == "__PYTHON__" or key == "__SYSTEM__"):
                Warn("undefined name `{}'".format(key))

            match = re.search(r'\(\(\(MARKER([0-9])+\)\)\)', value)
            if match:
                Error("missing argument {}".format(match.group(1)))

            # Straightforward substitution.
            if value == '(((BLANK)))':
                value = ''

            line[p1, p2-p1+l2] = value
        else:
            # FIXME: something is missing here, but this is from the Perl version
            if value == '(((BLANK)))':
                value = ''

            more = False

    line.replace('__NEWLINE__', '\n')
    line.replace('__TAB__', '\t')

    return line

def SplitArgs(arg_string):
    """
    # Split a string containing arguments into an array of argument and returns
    # this array. Take care of quoted arguments, in order to allow the use of
    # argument separator in argument.
    :param arg_string:
    :return:
    """
    temp = arg_string.split(argsep)

    while len(temp) > 0:
        arg = temp.pop(0)

        if arg.startswith('"'):
            # Start of "quoted arg" detected, look for end, and add argument.
            # The argument may have been split if it had embedded separators.
            # This puts Humpty Dumpty back together again
            while not re.match(r'(^"[^"]*")', arg):
                arg += argsep + temp.pop(0)

            arg = arg.strip('"')
            args.append(arg)
        elif arg.startswith("'"):
            # Start of 'quoted arg' detected, look for end, and add argument.
            while not re.match(r"(^'[^']*')",arg):
                arg += argsep + temp.pop(0)

            arg = arg.strip("'", arg)
            args.append(arg)
        else:
            args.append(arg)

    return args

def isProjectFile(file_name):
    """
    Return True if given filename may be a project file, False otherwise.
    :param file_name:
    :return:
    """
    for ext in ext_project:
        if file_name.endswith(ext):
            return True

    return False

def isSourceFile(file_name):
    """
    Return True if given filename may be a source file, False otherwise.
    :param file_name:
    :return:
    """
    for ext in ext_source:
        if file_name.endswith(ext):
            return True

    return False

def ChangeExtension(file_name):
    """
    Return the given source filename with extension changed according to
    ext_tartget
    :param file_name:
    :return:
    """
    for extension in ext_source:
        # Match can occur anywhere in the string, but it is
        # only erased when at the end of the file name??
        # Also: ext_source elements already have a period?
        if re.search(r'\.{}'.format(extension), file_name):
            file_name = re.sub(r'\.{}$'.format(extension), '', file_name)

        # And now we're looking to substitute the extension at
        # the end, but we just erased the lower case variant?
        # => change to .html, but only if the original was upper case?
        if re.search(r'{}$'.format(extension), file_name,
                     flags=re.IGNORECASE):
            file_name = re.sub(r'{}$'.format(extensions), ext_target, file_name)

    return file_name

def GetPathname(name):
    """
    Get the pathname of a given file. Always ends with a `/' if non-null.
    :param name:
    :return:
    """

    name = name.replace('\\', '/')
    last_slash = name.rfind('/')

    if last_slash != -1:
        name = name[:last_slash+1]
    else:
        name = ''

    return name

def GetOutputBasename(name):
    """
    Get the basename of a given output file.
    :param name:
    :return:
    """
    name = name.replace('\\', '/')
    last_slash = name.rfind('/')

    base_name = name[:last_slash+1]
    base_name = re.sub(r'{}$'.format(ext_target), '', base_name)

    return base_name

def AllSourceFiles():
    """
    Returns a list of all source files under the `.' directory.
    :return:
    """
    files = []
    dirs = ['.']

    dir_name = dirs.pop()      # Start off with the current directory

    while dir_name:
        for entry in os.listdir(dir_name):
            if dir_name == '.':
                dir_name = ''
            else:
                dir_name += '/'

            if isSourceFile(entry):
                files.append('{}{}'.format(dir_name, entry))
            elif os.path.isdir('{}{}'.format(dir_name, entry)):
                dirs.append('{}{}'.format(dir_name, entry))

            dir_name = dirs.pop()

    return files

def GetPathToRoot(name):
    """
    Get the path to the root directory of the project from a given a file name.
    Always end with a `/' if non-null.
    :param name:
    :return:
    """
    basename = name.replace('\\', '/')     # "\" -> "/"
    last_slash = basename.rfind('/')

    if last_slash != -1:
        basename = basename[:last_slash+1]

    path_to_root = re.sub(r'{}'.format(basename), '', name)
    path_to_root = re.sub(r'[^/\.]+/', '../', path_to_root)

    return path_to_root

def ResolveIncludeFile(name):
    """
    Returns the complete name of a file which may be stored anywhere in the
    include path.
    :param name:
    :return:
    """
    path = GetValue("PATHNAME") + name
    path = path.replace('//', '/')

    if GetValue("PATHNAME") == "(((BLANK)))":
        path = name

    # Perl test uses -r: True if file readable by effective uid/gid.
    # os.access uses the real uid/gid. Impact TBD.
    if os.path.isfile(path) and os.access(path, os.R_OK):
        return path
    elif os.path.isfile(name) and os.access(name, os.R_OK):
        return name

    for directory in include_path:
        expanded_path = Substitute(directory)
        expanded_path = expanded_path + '/' + name
        expanded_path = expanded_path.replace('//', '')

        if os.path.isfile(expanded_path) and os.access(expanded_path, os.R_OK):
            return expanded_path

    Error("no include file '{}' in `{}'".format(name, GetValue("INCLUDE_PATH")))
    return ''

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
