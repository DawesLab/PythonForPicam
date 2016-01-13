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

print('Initialize Camera.',Picam_InitializeLibrary())
print('\n')
major = piint()
minor = piint()
distribution = piint()
release = piint()
print('Check Software Version. ',Picam_GetVersion(pointer(major),pointer(minor),pointer(distribution),pointer(release)))
print('Picam Version ',major.value,'.',minor.value,'.',distribution.value,' Released: ',release.value)
print('\n')

class PyPICAM():
    """Provides basic camera features and init"""
    camera = PicamHandle()
    readoutstride = piint(0)
    readout_count = pi64s(1)
    readout_time_out = piint(-1) # -1 is same as NO_TIMEOUT?
    available = PicamAvailableData()
    errors = PicamAcquisitionErrorsMask()
    myroi = PicamRoi()


    def __init__(self):
        print('Opening First Camera')
        print(Picam_OpenFirstCamera(ctypes.byref(self.camera)))


    def close(self):
        """ Return shutter to normal, close camera, and uninitialize PICAM library"""

        ShutterMode = ctypes.c_int(1)  # normal
        print(Picam_SetParameterIntegerValue(self.camera, ctypes.c_int(PicamParameter_ShutterTimingMode), ShutterMode))
        ## Commit parameters:
        failed_parameters = ctypes.c_int() # not sure this is "the right thing" but it seems to work
        failed_parameters_count = piint()
        print(Picam_CommitParameters(self.camera, ctypes.byref(failed_parameters), ctypes.byref(failed_parameters_count)))
        print("Committed parameters (default shutter status)")
        print(Picam_DestroyParameters(failed_parameters))

        print("Closing camera")
        Picam_CloseCamera(self.camera)
        print("Uninitializing library")
        Picam_UninitializeLibrary()



    def configure_camera(self, T=-120, roi=[200,195,600,10,1,1]):
        """ Sets 4 MHz ADC rate, temp parameter can be set as integer (Default T=-120)
        roi is a parameter that controls the region of interest:
        roi = [x,y,width,height,x_binning,y_binning]"""
        print("Setting 4 MHz ADC rate...")
        print(Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_AdcSpeed), pi32f(2.0)))
        print("Setting temp setpoint to -120C")
        print(Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_SensorTemperatureSetPoint), pi32f(-120.0)))

        print("Setting trigger mode")
    # From picam.h: the enumeration of these options is:
    # PicamTriggerResponse_NoResponse               = 1,
    # PicamTriggerResponse_ReadoutPerTrigger        = 2,
    # PicamTriggerResponse_ShiftPerTrigger          = 3,
    # PicamTriggerResponse_ExposeDuringTriggerPulse = 4,
    # PicamTriggerResponse_StartOnSingleTrigger     = 5

        #TriggerResponse = ctypes.c_int(1)  # ignore trigger for now, we use ExposeMonitor as master trigger
        #print(Picam_SetParameterIntegerValue(self.camera, ctypes.c_int(PicamParameter_TriggerResponse), TriggerResponse)
        print("Setting ROI")
        # Set ROI to x = 100:700 y = 195:205
        self.myroi.x = roi[0]
        self.myroi.y = roi[1]
        self.myroi.width = roi[2]
        self.myroi.height = roi[3]
        self.myroi.x_binning = roi[4]
        self.myroi.y_binning = roi[5]
        rois = PicamRois()
        rois.roi_array = ctypes.pointer(self.myroi)
        rois.roi_count = 1
        print(Picam_SetParameterRoisValue(self.camera, ctypes.c_int(PicamParameter_Rois), ctypes.pointer(rois)))

        # Set shutter mode:
        ShutterMode = ctypes.c_int(3)  # always open
        print(Picam_SetParameterIntegerValue(self.camera, ctypes.c_int(PicamParameter_ShutterTimingMode), ShutterMode))

        # Set exposure time to 20 ms
        print(Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_ExposureTime), pi32f(20)))

        ## Commit parameters:
        failed_parameters = ctypes.c_int() # not sure this is "the right thing" but it seems to work
        failed_parameters_count = piint()
        print(Picam_CommitParameters(self.camera, ctypes.byref(failed_parameters), ctypes.byref(failed_parameters_count)))
        print("Cleaning up...")
        print(Picam_DestroyParameters(failed_parameters))

        print("Getting readout stride. ", Picam_GetParameterIntegerValue( self.camera, ctypes.c_int(PicamParameter_ReadoutStride), ctypes.byref(self.readoutstride) ))

    def get_temp(self):
        temp = ctypes.c_double()
        print(Picam_GetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_SensorTemperatureReading), ctypes.byref(temp)))
        print("Temp = %.1f" % temp.value)



    def acquire(self, N=1):
        self.readout_count = pi64s(N)
        print(Picam_Acquire(self.camera, self.readout_count, self.readout_time_out, ctypes.byref(self.available), ctypes.byref(self.errors)))

    def get_data(self):
        """ Routine to access initial data.
        Returns numpy array with shape (400,1340) """

        """ Create an array type to hold 1340x400 16bit integers """
        DataArrayType = pi16u*self.myroi.width*self.myroi.height

        """ Create pointer type for the above array type """
        DataArrayPointerType = ctypes.POINTER(pi16u*self.myroi.width*self.myroi.height)

        """ Create an instance of the pointer type, and point it to initial readout contents (memory address?) """
        DataPointer = ctypes.cast(self.available.initial_readout,DataArrayPointerType)


        """ Create a separate array with readout contents """
        # TODO, check this stuff for slowdowns
        rawdata = DataPointer.contents
        numpydata = numpy.frombuffer(rawdata, dtype='uint16')
        data = numpy.reshape(numpydata,(self.myroi.height,self.myroi.width))  # TODO: get dimensions officially,
        # note, the readoutstride is the number of bytes in the array, not the number of elements
        # will need to be smarter about the array size, but for now it works.
        return data

    def get_all_data(self):
        """ Routine to access all data shots from multi-shot run.
        Returns numpy array with shape (x,y,shotcount)."""
        shotcount = self.available.readout_count
        stride = self.readoutstride.value

        """ Create an array type to hold 1340x400 16bit integers """
        DataArrayType = pi16u*self.myroi.width*self.myroi.height

        """ Create pointer type for the above array type """
        DataArrayPointerType = ctypes.POINTER(pi16u*self.myroi.width*self.myroi.height)

        data = numpy.zeros((self.myroi.height,self.myroi.width,shotcount))

        for shot in range(shotcount):
            """ Create an instance of the pointer type, and point it to initial readout (memory address) """
            DataPointer = ctypes.cast(self.available.initial_readout + stride*shot, DataArrayPointerType)


            """ Create a separate array with readout contents """
            # TODO, check this stuff for slowdowns
            rawdata = DataPointer.contents
            numpydata = numpy.frombuffer(rawdata, dtype='uint16')
            data[:,:,shot] = numpy.reshape(numpydata,(self.myroi.height,self.myroi.width))

        return data




#########################
##### Main Routine  #####
#########################

if __name__ == '__main__':
    newcam = PyPICAM()
    newcam.configure_camera()
    newcam.acquire(N=1)
    data = newcam.get_data()
    print("Collected data:")
    print(data)

    ## Close camera
    print("Closing camera and uninitializing library...")
    print(newcam.close())
    print("Clean exit")
