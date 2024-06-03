from uitrace.api import *
#find(loc="obj_1682479928500.jpg", by=DriverType.CV, timeout=30)
#click(loc="obj_1682480033828.jpg", by=DriverType.CV, offset=None, timeout=30, duration=0.05, times=1)
init_driver
start_app('com.tencent.letsgo')

click(loc="obj_1682486049124.jpg", by=DriverType.CV, offset=None, timeout=30, duration=0.05, times=1)
