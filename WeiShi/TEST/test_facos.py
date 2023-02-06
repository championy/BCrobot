from ctypes import *


facos = CDLL('./fwlibe1.dll')


a = facos.cnc_allclibhndl3("192.168.0.224", 8193, 10)
print(a)

