# IPython log file

from pypicam import *
mycam = PyPICAM()
mycam.configure_camera()
mycam.acquire(N=2)
mycam.available
mycam.available()
mycam.available.initial_readout
mycam.available.readout_count
shotcount = mycam.available.readout_count
DataArrayType = pi16u*1340*400
DataArrayPointerType = ctypes.POINTER(DataArrayType)
DataPointer = ctypes.cast(mycam.available.initial_readout, DataArrayPointerType)
firstdata = DataPointer.contents
firstnumpy = numpy.frombuffer(firstdata, dtype='uint16')
firstnumpy
mycam.readoutstride
DataArrayType = pi16u*1340*400
DataPointer2 = ctypes.cast(mycam.available.initial_readout+mycam.readoutstride, DataArrayPointerType)
DataPointer2 = ctypes.cast(mycam.available.initial_readout+int(mycam.readoutstride), DataArrayPointerType)
int(mycam.readoutstride)
mycam.readoutstride.value
DataPointer2 = ctypes.cast(mycam.available.initial_readout + mycam.readoutstride.value, DataArrayPointerType)
seconddata = DataPointer2.contents
secondnumpy = numpy.frombuffer(seconddata, dtype='uint16')
secondnumpy
get_ipython().magic(u'logstart')
Picam_CloseCamera(mycam.camera)
Picam_UninitializeLibrary
Picam_UninitializeLibrary()
get_ipython().system(u'ls -F --color ')
exit()
