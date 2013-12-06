# IPython script to configure the camera
failed_parameter_count = piint()
failed_parameter_array = ctypes.c_int()
committed = pibln()
Picam_SetParameterFloatingPointValue(camera, PicamParameter_AdcSpeed, pi32f(4.0))
Picam_AreParametersCommitted(camera, ctypes.byref(committed))
committed
Picam_CommitParameters(camera, ctypes.byref(failed_parameter_array), ctypes.byref(failed_parameter_count))
Picam_AreParametersCommitted(camera, ctypes.byref(committed))
committed
