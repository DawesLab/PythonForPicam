"""
    PyPICAM provides a camera class for use with a Princeton Instruments CCD it uses the
    PythonForPicam interface:

    PythonForPicam is a Python ctypes interface to the Princeton Instruments PICAM Library
    Copyright (C) 2013  Joe Lowney.  The copyright holder can be reached at joelowney@gmail.com

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
"""

"""Test for talking to Picam"""
import ctypes as ctypes

""" Import standard type definitions from PiTypes.py """
from PiTypes import *

""" Import non-standard type definitions from PiTypesMore.py """
from PiTypesMore import *

""" Import function definitions from PiFunctions.py """
""" This should contian all of the functions from picam.h """
from PiFunctions import *

""" Import parameter lookup from PiParameterLookup.py """
""" This file includes a function PI_V and a lookup table to return the code
    for different Picam Parameters described in chapter 4 """
from PiParameterLookup import *

import numpy

############################
##### Custom Functions #####
############################

def pointer(x):
    """Returns a ctypes pointer"""
    ptr = ctypes.pointer(x)
    return ptr


def load(x):
    """Loads a library where argument is location of library"""
    x = ctypes.cdll.LoadLibrary(x)
    return x

picamLibrary = 'libpicam.so'
picam = load(picamLibrary) # Not sure where to put these?

print 'Initialize Camera.',Picam_InitializeLibrary()
print '\n'
major = piint()
minor = piint()
distribution = piint()
release = piint()
print 'Check Software Version. ',Picam_GetVersion(pointer(major),pointer(minor),pointer(distribution),pointer(release))
print 'Picam Version ',major.value,'.',minor.value,'.',distribution.value,' Released: ',release.value
print '\n'

class PyPICAM():
    """Provides basic camera features and init"""
    camera = PicamHandle()
    readoutstride = piint(0);
    readout_count = pi64s(1)
    readout_time_out = piint(-1) # -1 is same as NO_TIMEOUT?
    available = PicamAvailableData()
    errors = PicamAcquisitionErrorsMask()


    def __init__(self):
        print 'Opening First Camera'
        print Picam_OpenFirstCamera(ctypes.byref(self.camera))
        print "Getting readout stride. ", Picam_GetParameterIntegerValue( self.camera, ctypes.c_int(PicamParameter_ReadoutStride), ctypes.byref(self.readoutstride) );


    def close(self):
        """ Close camera and uninitialize PICAM library"""
        print 'closing camera'
        Picam_CloseCamera(self.camera)
        Picam_UninitializeLibrary()


    def configure_camera(self, T=-120):
        """ Sets 4 MHz ADC rate, temp parameter can be set as integer (Default T=-120) """
        print "Setting 4 MHz ADC rate..."
        print Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_AdcSpeed), pi32f(4.0))
        print "Setting temp setpoint to -120C"
        print Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_SensorTemperatureSetPoint), pi32f(-120.0))

        print "Setting trigger mode"
    # From picam.h: the enumeration of these options is:
    # PicamTriggerResponse_NoResponse               = 1,
    # PicamTriggerResponse_ReadoutPerTrigger        = 2,
    # PicamTriggerResponse_ShiftPerTrigger          = 3,
    # PicamTriggerResponse_ExposeDuringTriggerPulse = 4,
    # PicamTriggerResponse_StartOnSingleTrigger     = 5

        TriggerResponse = ctypes.c_int(2)  
        print Picam_SetParameterIntegerValue(self.camera, ctypes.c_int(PicamParameter_TriggerResponse), TriggerResponse)

        ShutterMode = ctypes.c_int(3)  # always open
        print Picam_SetParameterIntegerValue(self.camera, ctypes.c_int(PicamParameter_ShutterTimingMode), ShutterMode)
 
        ## Commit parameters:
        failed_parameters = ctypes.c_int() # not sure this is "the right thing" but it seems to work
        failed_parameters_count = piint()
        print Picam_CommitParameters(self.camera, ctypes.byref(failed_parameters), ctypes.byref(failed_parameters_count))
        print "Cleaning up..."
        print Picam_DestroyParameters(failed_parameters)


    def get_temp(self):
        temp = pi32f()
        print Picam_GetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_SensorTemperatureReading), ctypes.byref(temp))
        return temp

    def acquire(self, N=1):
        self.readout_count = pi64s(N)
        print Picam_Acquire(self.camera, self.readout_count, self.readout_time_out, ctypes.byref(self.available), ctypes.byref(self.errors))

    def get_data(self):
        """ Routine to access initial data.
        Returns numpy array with shape (400,1340) """

        """ Create an array type to hold 1340x400 16bit integers """
        DataArrayType = pi16u*536000

        """ Create pointer type for the above array type """
        DataArrayPointerType = ctypes.POINTER(pi16u*536000)

        """ Create an instance of the pointer type, and point it to initial readout contents (memory address?) """
        DataPointer = ctypes.cast(self.available.initial_readout,DataArrayPointerType)


        """ Create a separate array with readout contents """
        # TODO, check this stuff for slowdowns
        rawdata = DataPointer.contents
        numpydata = numpy.frombuffer(rawdata, dtype='uint16')
        data = numpy.reshape(numpydata,(400,1340))  # TODO: get dimensions officially,
        # note, the readoutstride is the number of bytes in the array, not the number of elements
        # will need to be smarter about the array size, but for now it works.
        return data

    def get_all_data(self):
        """ Routine to access all data shots from multi-shot run.
        Returns numpy array with shape (400,1340,shotcount)."""
        shotcount = self.available.readout_count
        stride = self.readoutstride.value

        """ Create an array type to hold 1340x400 16bit integers """
        DataArrayType = pi16u*536000

        """ Create pointer type for the above array type """
        DataArrayPointerType = ctypes.POINTER(pi16u*536000)

        data = numpy.zeros((400,1340,shotcount))

        for shot in range(shotcount):
            """ Create an instance of the pointer type, and point it to initial readout (memory address) """
            DataPointer = ctypes.cast(self.available.initial_readout + stride*shot, DataArrayPointerType)


            """ Create a separate array with readout contents """
            # TODO, check this stuff for slowdowns
            rawdata = DataPointer.contents
            numpydata = numpy.frombuffer(rawdata, dtype='uint16')
            data[:,:,shot] = numpy.reshape(numpydata,(400,1340))

        return data




#########################
##### Main Routine  #####
#########################

if __name__ == '__main__':
    newcam = PyPICAM()
    newcam.configure_camera()
    newcam.acquire(N=1)
    data = newcam.get_data()
    print "Collected data:"
    print data

    ## Close camera
    print "Closing camera..."
    print Picam_CloseCamera(newcam.camera)

    ## Close down library
    print 'Uninitializing...'
    print Picam_UninitializeLibrary()
    print 'Clean exit'
