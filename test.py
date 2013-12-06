# test the ctypes wrapper for PICAM

import ctypes as ctypes
picamDll = "libpicam.so"
picam = ctypes.cdll.LoadLibrary(picamDll)
from PiTypes import *
from PiTypesMore import *
from PiFunctions import *
from PiParameterLookup import *
def pointer(x):
        """Returns a ctypes pointer"""
        ptr = ctypes.pointer(x)
        return ptr
def load(x):
        """Loads DLL library where argument is location of library"""
        x = ctypes.cdll.LoadLibrary(x)
        return x
camera = PicamHandle()
print 'Initialize Camera.',Picam_InitializeLibrary()
print 'Opening First Camera', Picam_OpenFirstCamera(ctypes.addressof(camera))
readoutstride = piint(0);
print "Getting readout stride. ", Picam_GetParameterIntegerValue( camera, ctypes.c_int(PicamParameter_ReadoutStride), ctypes.byref(readoutstride) );
readout_count = pi64s(1)
readout_time_out = piint(100000)
available = PicamAvailableData()
errors = PicamAcquisitionErrorsMask()
Picam_Acquire.argtypes = PicamHandle, pi64s, piint, ctypes.POINTER(PicamAvailableData), ctypes.POINTER(PicamAcquisitionErrorsMask)
Picam_Acquire.restype = piint
#Picam_Acquire(camera, readout_count, readout_time_out, ctypes.byref(available), ctypes.byref(errors))
