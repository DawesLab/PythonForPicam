PythonForPicam
==============


PythonForPicam is a Python ctypes interface to the Princeton Instruments PICAM Library
Copyright (C) 2013  Joe Lowney.  The copyright holder can be reached at joelowney@gmail.com

pypicam is a module that provides basic access to the first camera loaded
by the system. This module was added as part of our development of a
PyZMQ client/server model for passing image data (see https://github.com/DawesLab/Camserver)
Andrew M.C. Dawes - dawes@pacificu.edu

==============
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or any
later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.



A Python Interface for PICAM Library
----------------------------------------

The interface can nominally be run by building Main.py

The interface uses the built in Python ctypes module.  The interface reads in
a library, Picam.dll, provided by Princeton Instruments at
ftp://ftp.princetoninstruments.com/Public/Software/Official/PICam/

Main.py is the main application.  When compiled, Main.py reads in external types
defined in PiTypes.py and PiTypesMore.py as well as functions from PiFunctions.py.
PiParameterLookup.py is used to read in camera parameter values.  This is mainly
a workaround to address the fact that Python ctypes does not have a built in enum
class.


2013 June 26 -- Initial Release
------------------------------
Main.py
PiTypes.py
PiTypesMore.py
PiFunctions.py
PiParameterLookup.py

2013 December 8 -- Modifications for use in Linux (DawesLab)
------------------------------
- Import `libpicam.so` library instead of DLLs
- `pypicam.py` is written as a basic module to provide simple access
to the first camera loaded by the system.

2016 January 13 -- Modifications to run under Python 3
------------------------------
Simply replaced all `print ...` statements with `print(...)` statements. To use this under python 2, simply checkout commit a970928a64388cb1ee5bdc1a7f5f8e956f6413d9 instead of the latest.

TODO
-----------------------------
Handle some of the enum types in the Picam properties. Settings like TriggerResponse need to be set as integers now since there is no lookup table for these options. Parse picam.h to generate the necessary info.


