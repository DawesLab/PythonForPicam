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
    readout_time_out = piint(-1) # same as NO_TIMEOUT?
    available = PicamAvailableData()
    errors = PicamAcquisitionErrorsMask()

    def __init__(self):
        print 'Opening First Camera'
        print Picam_OpenFirstCamera(pointer(self.camera))
        print "Getting readout stride. ", Picam_GetParameterIntegerValue( self.camera, ctypes.c_int(PicamParameter_ReadoutStride), ctypes.byref(self.readoutstride) );

    def configure_camera(self):
        print "Setting 4 MHz ADC rate..."
        print Picam_SetParameterFloatingPointValue(self.camera, ctypes.c_int(PicamParameter_AdcSpeed), pi32f(4.0))

        ## Commit parameters:
        failed_parameters = ctypes.c_int() # not sure this is "the right thing" but it seems to work
        failed_parameters_count = piint()
        print Picam_CommitParameters(self.camera, ctypes.byref(failed_parameters), ctypes.byref(failed_parameters_count))
        print "Cleaning up..."
        print Picam_DestroyParameters(failed_parameters)

    def acquire(self, N=1):
        self.readout_count = pi64s(N)
        print Picam_Acquire(self.camera, self.readout_count, self.readout_time_out, ctypes.byref(self.available), ctypes.byref(self.errors))

    def get_data(self):
        """ Test Routine to Access Data """

        """ Create an array type to hold 1300x400 16bit integers """
        DataArrayType = pi16u*520000

        """ Create pointer type for the above array type """
        DataArrayPointerType = ctypes.POINTER(pi16u*520000)

        """ Create an instance of the pointer type, and point it to initial readout contents (memory address?) """
        DataPointer = ctypes.cast(self.available.initial_readout,DataArrayPointerType)


        """ Create a separate array with readout contents """
        # TODO, check this stuff for slowdowns
        rawdata = DataPointer.contents
        numpydata = numpy.frombuffer(rawdata, dtype='uint16')
        data = numpy.reshape(numpydata,(1300,400))  # TODO: get dimensions officially,
        # note, the readoutstride is the number of bytes in the array, not the number of elements
        # will need to be smarter about the array size, but for now it works.
        return data



#########################
##### Main Routine  #####
#########################

if __name__ == '__main__':
    """ Load the libpicam.so library """
    # picamDll = 'C:/Users/becgroup/Documents/Python/DriverTest/Princeton Instruments/Picam/Runtime/Picam.dll'
    picamLibrary = 'libpicam.so'
    picam = load(picamLibrary)

    print 'Initialize Camera.',Picam_InitializeLibrary()
    print '\n'

    """ Print version of PICAM """
    major = piint()
    minor = piint()
    distribution = piint()
    release = piint()
    print 'Check Software Version. ',Picam_GetVersion(pointer(major),pointer(minor),pointer(distribution),pointer(release))
    print 'Picam Version ',major.value,'.',minor.value,'.',distribution.value,' Released: ',release.value
    print '\n'

    ## Test Routine to connect a demo camera
    ## p23
    print 'Preparing to connect Demo Camera'
    model = ctypes.c_int(428)
    serial_number = ctypes.c_char_p('12345')
    PicamID = PicamCameraID()
    """
    PICAM_API Picam_ConnectDemoCamera(
    PicamModel     model,
    const pichar*  serial_number,
    PicamCameraID* id );
    """
    print 'Demo camera connected with return value = ',Picam_ConnectDemoCamera(model, serial_number, pointer(PicamID))
    print '\n'

    print 'Camera model is ',PicamID.model
    print 'Camera computer interface is ',PicamID.computer_interface
    print 'Camera sensor_name is ', PicamID.sensor_name
    print 'Camera serial number is', PicamID.serial_number
    print '\n'

    ## Test routine to open first camera
    ## p20
    """
    PICAM_API Picam_OpenFirstCamera( PicamHandle* camera );
    """

    camera = PicamHandle()
    print 'Opening First Camera'

    #print Picam_OpenFirstCamera(ctypes.addressof(camera))
    print Picam_OpenFirstCamera(pointer(camera))

    ## Set ADC rate to high
    #     error = Picam_SetParameterFloatingPointValue(
    #             camera,
    #             PicamParameter_AdcSpeed,
    #             4.0 );
    # PrintError( error );


    print Picam_SetParameterFloatingPointValue(camera, ctypes.c_int(PicamParameter_AdcSpeed), pi32f(4.0))

    ## Commit parameters:
    failed_parameters = ctypes.c_int() # not sure this is "the right thing" but it seems to work
    failed_parameters_count = piint()
    print Picam_CommitParameters(camera, ctypes.byref(failed_parameters), ctypes.byref(failed_parameters_count))
    print "Cleaning up..."
    print Picam_DestroyParameters(failed_parameters)

    ## Test routine to acquire image
    ## p73
    """
    PICAM_API Picam_Acquire(
    PicamHandle                 camera,
    pi64s                       readout_count,
    piint                       readout_time_out,
    PicamAvailableData*         available,
    PicamAcquisitionErrorsMask* errors );
    """
    readoutstride = piint(0);
    print "Getting readout stride. ", Picam_GetParameterIntegerValue( camera, ctypes.c_int(PicamParameter_ReadoutStride), ctypes.byref(readoutstride) );

    """
    Prototype
    PICAM_API Picam_Acquire(
    PicamHandle                 camera,
    pi64s                       readout_count,
    piint                       readout_time_out,
    PicamAvailableData*         available,
    PicamAcquisitionErrorsMask* errors );
    """

    """
    typedef struct PicamAvailableData
    {
        void* initial_readout;
        pi64s readout_count;
    } PicamAvailableData;
    """
    readout_count = pi64s(1)
    readout_time_out = piint(-1) # same as NO_TIMEOUT?
    available = PicamAvailableData()

    """ Print Debug Information on initial readout """
    print '\n'
    print "available.initial_readout: ",available.initial_readout
    print "Initial readout type is", type(available.initial_readout)
    errors = PicamAcquisitionErrorsMask()

    """
    Prototype
    PICAM_API Picam_Acquire(
    PicamHandle                 camera,
    pi64s                       readout_count,
    piint                       readout_time_out,
    PicamAvailableData*         available,
    PicamAcquisitionErrorsMask* errors );
    """
    Picam_Acquire.argtypes = PicamHandle, pi64s, piint, ctypes.POINTER(PicamAvailableData), ctypes.POINTER(PicamAcquisitionErrorsMask)

    Picam_Acquire.restype = piint

    print '\nAcquiring... '
    print Picam_Acquire(camera, readout_count, readout_time_out, ctypes.byref(available), ctypes.byref(errors))
    print '\n'
    print 'step a'

    print "available.initial_readout: ",available.initial_readout
    print "Initial readout type is", type(available.initial_readout)
    print '\n'

    """ Close out Library Resources """
    ## Disconnected the above cameras
    print 'Disconnecting demo camera...'
    print Picam_DisconnectDemoCamera(pointer(PicamID))



    """ Test Routine to Access Data """

    """ Create an array type to hold 1300x400 16bit integers """
    DataArrayType = pi16u*520000

    """ Create pointer type for the above array type """
    DataArrayPointerType = ctypes.POINTER(pi16u*520000)

    """ Create an instance of the pointer type, and point it to initial readout contents (memory address?) """
    DataPointer = ctypes.cast(available.initial_readout,DataArrayPointerType)


    """ Create a separate array with readout contents """
    data = DataPointer.contents


    """ Write contents of Data to binary file"""
    libc = ctypes.CDLL('libc.so.6')
    fopen = libc.fopen
    fopen.argtypes = ctypes.c_char_p, ctypes.c_char_p
    fopen.restype = ctypes.c_void_p

    fwrite = libc.fwrite
    fwrite.argtypes = ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_void_p
    fwrite.restype = ctypes.c_size_t

    fclose = libc.fclose
    fclose.argtypes = ctypes.c_void_p,
    fclose.restype = ctypes.c_int

    fp = fopen('PythonBinOutput.raw', 'wb')
    print 'fwrite returns: ',fwrite(data, readoutstride.value, 1, fp)

    fclose(fp)

    ## Close camera
    print "Closing camera..."
    print Picam_CloseCamera(camera)

    ## Close down library
    print 'Uninitializing...'
    print Picam_UninitializeLibrary()
